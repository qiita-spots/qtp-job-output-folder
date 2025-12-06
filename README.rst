Job Output Folder Data Type Plugin
==================================

The goal of this Qiita type plugin is to validate and summarize any kind of folder output.

Note that `job-output-folder` expects a single folder and this will become an artifact that will live in
`[qiita-base-path]/job-output-folder/[artifact-id]/[output-folder]` and this plugin will generate:

- `summary.html`: a browser friendly file listing that will include all files at `[artifact-id]/[output-folder]` and
  any `index.html` files in any subfolder. As a reminder, the Qiita nginx basic configuration allows to display/load any
  html/JS available files; thus, able to display properly `index.html` files available
- `MANIFEST.txt`: a comprehensive list of all available files in the folder.

The two main plugins using this output are:

- https://github.com/qiita-spots/qp-knight-lab-processing: which will generate an `[output-folder]` contaning all the logs,
  files and summaries from BCL to clean FASTQ processing. Note that multiqc resoults are part of this and the outputs are
  properly displayed in Qiita using this method.
- https://github.com/qiita-spots/qp-pacbio: `PacBio processing`, the output are MAG, LCG and other output, which will be used
  for dowstream analyses.
