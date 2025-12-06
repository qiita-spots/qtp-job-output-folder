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

    def test_validate(self):
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

        out_dir = mkdtemp()
        self._clean_up_files.append(out_dir)
        obs_success, obs_ainfo, obs_error = validate(
            self.qclient, job_id, parameters, out_dir
        )

        self.assertTrue(obs_success)
        filepaths = [
            (f"{self.source_dir}", "directory"),
            (f"{out_dir}/summary.html", "html_summary"),
        ]
        exp = [ArtifactInfo(None, "job-output-folder", filepaths)]
        self.assertEqual(obs_ainfo, exp)
        self.assertEqual(obs_error, "")


if __name__ == "__main__":
    main()
