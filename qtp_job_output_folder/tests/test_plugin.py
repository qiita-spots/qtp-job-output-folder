# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import main
from tempfile import mkdtemp
from os import remove
from os.path import exists, isdir, join, dirname, abspath
from inspect import currentframe, getfile
from shutil import copytree, rmtree
from json import dumps
from time import sleep

from qiita_client.testing import PluginTestCase

from qtp_job_output_folder import plugin, __version__


class PluginTests(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        # need to refer to a valid mountpoint (here: job) and a directory
        # that exists in Qiita DB as 'directory' as fetching via https will
        # fail otherwise. To avoid collisions, a mid-level directory name is
        # a random string (= _get_candidate_names())
        self.mountpoint = 'job'
        # only adapt filepaths
        self.source_dir = join(self.base_data_dir, self.mountpoint,
                               '2_test_folder')
        source = join(dirname(abspath(getfile(currentframe()))), 'test_data')
        copytree(source, self.source_dir)
        self.qclient.push_file_to_central(self.source_dir)
        self._clean_up_files = [self.out_dir, dirname(self.source_dir)]
        self._clean_up_remote_files = []

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)
        for fp in self._clean_up_remote_files:
            self.qclient.delete_file_from_central(fp)

    def _wait_job(self, job_id):
        for i in range(20):
            status = self.qclient.get_job_info(job_id)['status']
            if status != 'running':
                break
            sleep(1)
        return status

    def test_plugin_summary(self):
        # creating new artifact
        files = [(self.source_dir, 'directory')]
        atype = 'job-output-folder'
        data = {'filepaths': dumps(files), 'type': atype,
                'name': "A name", 'data_type': 'Job Output Folder'}
        aid = self.qclient.post('/apitest/artifact/', data=data)['artifact']
        data = {'command': dumps(['qtp-job-output-folder', __version__,
                                  'Generate HTML summary']),
                'parameters': dumps({'input_data': aid}),
                'status': 'running'}
        job_id = self.qclient.post(
            '/apitest/processing_job/', data=data)['job']
        plugin("https://localhost:21174", job_id, self.out_dir)
        fp_target_dir = '%s/%s' % (self.source_dir.split(
            '/%s/' % self.mountpoint)[0], atype)
        self._clean_up_remote_files.append(fp_target_dir)
        self._clean_up_files.append(fp_target_dir)
        self._wait_job(job_id)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs['status'], 'success')

    def test_plugin_validate(self):
        # test success
        files = {'directory': [self.source_dir]}
        atype = 'job-output-folder'
        parameters = {'template': None,
                      'analysis': None,
                      'files': dumps(files),
                      'artifact_type': atype}
        data = {
            'command': dumps(
                ['qtp-job-output-folder', __version__, 'Validate']),
            'parameters': dumps(parameters),
            'status': 'running'}
        job_id = self.qclient.post(
            '/apitest/processing_job/', data=data)['job']
        plugin("https://localhost:21174", job_id, self.out_dir)
        fp_target_dir = '%s/%s' % (self.source_dir.split(
            '/%s/' % self.mountpoint)[0], atype)
        self._clean_up_remote_files.append(fp_target_dir)
        self._clean_up_files.append(fp_target_dir)
        self._wait_job(job_id)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs['status'], 'success')

        # test failure
        files = {'directory': [join(self.base_data_dir, 'do/not/exits')]}
        parameters['files'] = dumps(files)
        data['parameters'] = dumps(parameters)
        job_id = self.qclient.post(
            '/apitest/processing_job/', data=data)['job']
        plugin("https://localhost:21174", job_id, self.out_dir)
        self._wait_job(job_id)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs['status'], 'error')


if __name__ == '__main__':
    main()
