# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from qiita_client import QiitaArtifactType, QiitaTypePlugin

from .summary import generate_html_summary
from .validate import validate

__version__ = "2021.08"


# Define the supported artifact types
artifact_types = [
    # QiitaArtifactType(name, description, can_be_submitted_to_ebi,
    #                   can_be_submitted_to_vamps, is_user_uploadable,
    #                   filepath_types):
    QiitaArtifactType(
        "job-output-folder",
        "Job Output Folder",
        False,
        False,
        False,
        [("directory", True)],
    ),
]

# Initialize the plugin
plugin = QiitaTypePlugin(
    "qtp-job-output-folder",
    __version__,
    "job-output-folder artifact types plugin",
    validate,
    generate_html_summary,
    artifact_types,
)
