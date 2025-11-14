# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from os.path import exists, isdir

from json import loads

from .summary import _generate_html_summary

from qiita_client import ArtifactInfo


def validate(qclient, job_id, parameters, out_dir):
    """Validae and fix a new artifact

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
    bool, list of ArtifactInfo, str
        Whether the job is successful
        a list of ArtifactInfo
        The error message, if not successful
    """
    qclient.update_job_step(job_id, "Step 1: Validating directory")

    files = loads(parameters['files'])
    # [0] we only expect one directory
    folder = files['directory'][0]

    success = False
    ainfo = None
    error_msg = f'{folder} does not exist or is not a folder'
    if exists(folder) and isdir(folder):
        qclient.update_job_step(job_id, "Step 2: Generating artifact")

        success = True
        error_msg = ''

        filepaths = [(folder, 'directory')]

        # let's generate the summary so it's ready to be displayed
        index_fp, viz_fp = _generate_html_summary(job_id, folder, out_dir)
        filepaths.append((index_fp, 'html_summary'))
        if viz_fp is not None:
            filepaths.append((viz_fp, 'html_summary_dir'))

        ainfo = [ArtifactInfo(None, 'job-output-folder', filepaths)]

    return success, ainfo, error_msg
