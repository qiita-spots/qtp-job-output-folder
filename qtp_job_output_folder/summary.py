# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from glob import glob
from json import dumps
from os.path import dirname, exists, isdir, join


def _folder_listing(folder):
    results = []
    for f in glob(f"{folder}/*"):
        if isdir(f):
            results.append(("folder", f))
            results.extend(_folder_listing(f"{f}/*"))
        else:
            results.append(("file", f))
    return results


def _generate_html_summary(jid, folder, out_dir):
    summary = f"<h3><b>{folder}</b> does not exist.</h3>"

    if exists(folder) and isdir(folder):
        # calculating the "trimming" for the fullpaths, +1 is to remove /
        tname = len(dirname(folder)) + 1
        tlink = len(dirname(dirname(folder)))
        summary = "<br/>\n".join(
            [
                f'<a href=".{f[tlink:]}" type="{ft}" target="_blank">{f[tname:]}</a>'
                for ft, f in _folder_listing(folder)
            ]
        )

    index_fp = join(out_dir, "summary.html")
    with open(index_fp, "w") as of:
        of.write(summary)

    # we could add a support folder for the summary
    viz_fp = None

    return index_fp, viz_fp


def generate_html_summary(qclient, job_id, parameters, out_dir):
    """Generates the HTML summary of job-output-folder type

    Parameters
    ----------
    qclient : qiita_client.QiitaClient
        The Qiita server client
    job_id : str
        The job id
    parameters : dict
        The parameter values to validate and create the artifact
    out_dir : str
        The path to the job's output directory

    Returns
    -------
    bool, None, str
        Whether the job is successful
        Ignored
        The error message, if not successful
    """
    # Step 1: gather file information from qiita using REST api
    # we are going to use the "raw" code for retrieving artifact_info vs. the
    # qiita_client.artifact_and_preparation_files method because this only
    # expects a single filepath
    artifact_id = parameters["input_data"]
    qclient_url = "/qiita_db/artifacts/%s/" % artifact_id
    artifact_info = qclient.get(qclient_url)

    # [0] there is only one directory
    folder = artifact_info["files"]["directory"][0]["filepath"]

    # 2. Generate summary
    index_fp, viz_fp = _generate_html_summary(job_id, folder, out_dir)

    # Step 3: add the new file to the artifact using REST api
    success = True
    error_msg = ""
    try:
        fps = dumps({"html": index_fp, "dir": viz_fp})
        qclient.patch(qclient_url, "add", "/html_summary/", value=fps)
    except Exception as e:
        success = False
        error_msg = str(e)

    return success, None, error_msg
