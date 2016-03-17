"""findmygits

Lists all local git repos on your computer. Build for Ubuntu 15.10 (Wily)

Usage:
    findmygits

Arguments:

Options:
"""

import os
import glob
from pprint import pprint
# TODO : use docopt later when input arguments are needed (e.g. --exclude some_directory)
#from docopt import docopt

def find():
    home = os.environ['HOME']
    os.chdir(home)
    match = '**/.git'
    list = glob.glob(match, recursive=True)
    return list


if __name__ == '__main__':
    # args = docopt(__doc__)
    # print(args)
    pprint(find())
