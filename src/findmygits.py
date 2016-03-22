"""findmygits

Lists all local git repos on your computer. Build for Ubuntu 15.10 (Wily)

Usage:
    findmygits

Arguments:

Options:
"""

import os
import glob
import subprocess
from pprint import pprint
# TODO : use docopt later when input arguments are needed (e.g. --exclude some_directory)
#from docopt import docopt

def find():
    home = os.environ['HOME']
    os.chdir(home)
    match_active = '**/.git'
    match_bare = '**/*.git'
    list_active = glob.glob(match_active, recursive=True)
    list_bare = glob.glob(match_bare, recursive=True)

    return (list_active, list_bare)

if __name__ == '__main__':
    # args = docopt(__doc__)
    # print(args)

    # a) List all active and bare repos
    active, bare = find()
    bar = '-----------------------------'
    print(bar)
    print("-- Active repos (characerised by a '.git' folder)")
    print(bar)
    pprint(active)
    print('\n' + bar)
    print("-- Bare repos (expected to follow the naming convention XXX.git)")
    print(bar)
    pprint(bare)

    # b) For all active working directories, list remotes
