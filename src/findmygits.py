"""findmygits

Lists all local git repos on your computer. Built on Ubuntu 15.10 (Wily)

Usage:
    findmygits

Arguments:

Options:
"""

import os
import subprocess
from pprint import pprint
# TODO : use docopt later when input arguments are needed (e.g. --exclude some_directory)
# from docopt import docopt


def find():
    home = os.environ['HOME']
    p = subprocess.Popen('find ' + home + ' -type d -name "*.git"', shell=True, stdout=subprocess.PIPE)

    search = p.communicate()[0].decode('UTF-8').split('\n')
    list_active = [s for s in search if '/.git' in s]
    list_bare = [s for s in search if s not in list_active]

    return list_active, list_bare

if __name__ == '__main__':
    # args = docopt(__doc__)
    # print(args)

    # a) List all active and bare repos
    active, bare = find()
    bar = '-----------------------------'
    print(bar)
    print("-- Bare repos (expected to follow the naming convention XXX.git)")
    print(bar)
    pprint(bare)
    print('\n' + bar)
    print("-- Active repos (characterised by a '.git' folder)")
    print(bar)
    pprint(active)

    # b) For all active working directories, list remotes
