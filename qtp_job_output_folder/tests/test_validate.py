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
from unittest import main

from qiita_client import ArtifactInfo
from qiita_client.testing import PluginTestCase

from qtp_job_output_folder import __version__
from qtp_job_output_folder.validate import validate


class ValidateTests(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        # need to refer to a valid mountpoint (here: job) and a directory
        # that exists in Qiita DB as 'directory' as fetching via https will
        # fail otherwise
        self.mountpoint = "job"
        self.source_dir = join(self.base_data_dir, self.mountpoint,
                               "2_test_folder")
        source = join(dirname(abspath(getfile(currentframe()))), "test_data")
        copytree(source, self.source_dir)
        self.qclient.push_file_to_central(self.source_dir)
        self._clean_up_files = [self.out_dir, dirname(self.source_dir)]

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def test_validate(self):
        files = {"directory": [self.source_dir]}
        atype = "job-output-folder"
        parameters = {
            "template": None,
            "analysis": None,
            "files": dumps(files),
            "artifact_type": atype,
        }
        data = {
            "command": dumps(["qtp-job-output-folder", __version__, "Validate"]),
            "parameters": dumps(parameters),
            "status": "running",
        }
        job_id = self.qclient.post("/apitest/processing_job/", data=data)["job"]

        obs_success, obs_ainfo, obs_error = validate(
            self.qclient, job_id, parameters, self.out_dir
        )

        self.assertTrue(obs_success)
        filepaths = [
            (f"{self.source_dir}", "directory"),
            (f"{self.out_dir}/summary.html", "html_summary"),
        ]
        exp = [ArtifactInfo(None, "job-output-folder", filepaths)]
        self.assertEqual(obs_ainfo, exp)
        self.assertEqual(obs_error, "")


if __name__ == "__main__":
    main()
