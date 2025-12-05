# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from inspect import currentframe, getfile
from json import dumps
from os import remove
from os.path import abspath, dirname, exists, isdir, join
from shutil import copytree, rmtree
from tempfile import mkdtemp
from time import sleep
from unittest import main

from qiita_client.testing import PluginTestCase

from qtp_job_output_folder import __version__, plugin


class PluginTests(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        self.source_dir = join(mkdtemp(), "test_data")
        source = join(dirname(abspath(getfile(currentframe()))), "test_data")
        copytree(source, self.source_dir)
        self._clean_up_files = [self.out_dir]

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def _wait_job(self, job_id):
        for i in range(20):
            status = self.qclient.get_job_info(job_id)["status"]
            if status != "running":
                break
            sleep(1)
        return status

    def test_plugin_summary(self):
        # creating new artifact
        files = [(self.source_dir, "directory")]
        data = {
            "filepaths": dumps(files),
            "type": "job-output-folder",
            "name": "A name",
            "data_type": "Job Output Folder",
        }
        aid = self.qclient.post("/apitest/artifact/", data=data)["artifact"]
        data = {
            "command": dumps(
                ["qtp-job-output-folder", __version__, "Generate HTML summary"]
            ),
            "parameters": dumps({"input_data": aid}),
            "status": "running",
        }
        job_id = self.qclient.post("/apitest/processing_job/", data=data)["job"]
        plugin("https://localhost:21174", job_id, self.out_dir)
        self._wait_job(job_id)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs["status"], "success")

    def test_plugin_validate(self):
        # test success
        files = {"directory": [self.source_dir]}
        parameters = {
            "template": None,
            "analysis": None,
            "files": dumps(files),
            "artifact_type": "job-output-folder",
        }
        data = {
            "command": dumps(["qtp-job-output-folder", __version__, "Validate"]),
            "parameters": dumps(parameters),
            "status": "running",
        }
        job_id = self.qclient.post("/apitest/processing_job/", data=data)["job"]
        plugin("https://localhost:21174", job_id, self.out_dir)
        self._wait_job(job_id)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs["status"], "success")

        # test failure
        files = {"directory": ["/do/not/exits"]}
        parameters["files"] = dumps(files)
        data["parameters"] = dumps(parameters)
        job_id = self.qclient.post("/apitest/processing_job/", data=data)["job"]
        plugin("https://localhost:21174", job_id, self.out_dir)
        self._wait_job(job_id)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs["status"], "error")


if __name__ == "__main__":
    main()
