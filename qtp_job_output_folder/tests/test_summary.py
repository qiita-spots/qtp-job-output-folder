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

from qiita_client.testing import PluginTestCase

from qtp_job_output_folder import __version__
from qtp_job_output_folder.summary import generate_html_summary


class SummaryTests(PluginTestCase):
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

    def test_summary(self):
        files = [(self.source_dir, "directory")]
        data = {
            "filepaths": dumps(files),
            "type": "job-output-folder",
            "name": "A name",
            "data_type": "Job Output Folder",
        }
        aid = self.qclient.post("/apitest/artifact/", data=data)["artifact"]
        parameters = {"input_data": aid}
        data = {
            "command": dumps(
                ["qtp-job-output-folder", __version__, "Generate HTML summary"]
            ),
            "parameters": dumps(parameters),
            "status": "running",
        }
        url = "/apitest/processing_job/"
        job_id = self.qclient.post(url, data=data)["job"]

        # Run the test
        obs_success, obs_ainfo, obs_error = generate_html_summary(
            self.qclient, job_id, parameters, self.out_dir
        )

        # asserting reply
        self.assertTrue(obs_success)
        self.assertIsNone(obs_ainfo)
        self.assertEqual(obs_error, "")

        # asserting content of html
        res = self.qclient.get("/qiita_db/artifacts/%s/" % aid)
        # cleaning artifact files, to avoid errors
        [
            self._clean_up_files.extend([ff["filepath"]])
            for f in res["files"].values()
            for ff in f
        ]
        html_fp = res["files"]["html_summary"][0]["filepath"]
        with open(html_fp) as html_f:
            html = html_f.read()

        self.assertEqual(html, EXP_HTML.format(aid=aid))

        # verifying the new MANIFEST.txt
        mfp = join(res["files"]["directory"][0]["filepath"], "MANIFEST.txt")
        self.assertTrue(exists(f"{mfp}"))
        with open(mfp, "r") as f:
            obs = f.readlines()
        self.assertCountEqual(obs, EXP_MANIFEST)


EXP_HTML = (
    '<a href="./{aid}/test_data/MANIFEST.txt" type="file" target="_blank">'
    "test_data/MANIFEST.txt</a><br/>\n"
    '<a href="./{aid}/test_data/file_1" type="file" target="_blank">'
    "test_data/file_1</a><br/>\n"
    '<a href="./{aid}/test_data/file_2" type="file" target="_blank">'
    "test_data/file_2</a><br/>\n"
    '<a href="./{aid}/test_data/folder_a/folder_b/index.html" type="file" '
    'target="_blank">test_data/folder_a/folder_b/index.html</a><br/>\n'
    '<a href="./{aid}/test_data/folder_1/index.html" type="file" '
    'target="_blank">test_data/folder_1/index.html</a>'
)
EXP_MANIFEST = [
    " test_data/\n",
    "|-- file_1\n",
    "|-- file_2\n",
    "|-- folder_a/\n",
    "|--|-- file_a\n",
    "|--|-- folder_b/\n",
    "|--|--|-- index.html\n",
    "|--|--|-- folder_c/\n",
    "|--|--|--|-- file_c\n",
    "|-- folder_1/\n",
    "|--|-- index.html",
]


if __name__ == "__main__":
    main()
