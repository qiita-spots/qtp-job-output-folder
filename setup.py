#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2013, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from setuptools import setup
from glob import glob

__version__ = "2021.08"

classes = """
    Development Status :: 5 - Production/Stable
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules
    Programming Language :: Python
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: POSIX :: Linux
    Operating System :: MacOS :: MacOS X
"""

with open('README.rst') as f:
    long_description = f.read()

classifiers = [s.strip() for s in classes.split('\n') if s]

setup(name='qtp-job-output-folder',
      version=__version__,
      long_description=long_description,
      license="BSD",
      description='Qiita Type Plugin: Job Output Folder',
      author="Qiita development team",
      author_email="qiita.help@gmail.com",
      url='https://github.com/qiita-spots/qtp-job-output-folder',
      test_suite='nose.collector',
      packages=['qtp_job_output_folder'],
      package_data={'qtp_job_output_folder': ['support_files/config_file.cfg',
                                              'tests/test_data/*']},
      scripts=glob('scripts/*'),
      extras_require={'test': ["nose >= 0.10.1", "pep8"]},
      install_requires=['click >= 3.3', 'matplotlib',
                        'qiita-files @ https://github.com/'
                        'qiita-spots/qiita-files/archive/master.zip',
                        'qiita_client @ https://github.com/'
                        'qiita-spots/qiita_client/archive/master.zip'],
      classifiers=classifiers)
