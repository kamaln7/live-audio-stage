"""
If you have pip installed or you're using Python 2.7.9 or higher (which has pip pre-installed),
you can run this script to install of the prerequisites for RTSMCS.
"""

import os

PREREQUISITE_NAME_LIST = ['mido', 'optirx', 'nibabel', 'pygame']

if __name__ == '__main__':
    for prereq_name in PREREQUISITE_NAME_LIST:
        os.system('pip install ' + prereq_name)