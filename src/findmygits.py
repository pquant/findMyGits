"""findmygits

Lists all local git repos on your computer. Built on Ubuntu 15.10 (Wily)

Usage:
    findmygits

Arguments:

Options:
"""

import os
import subprocess
# TODO : use docopt later when input arguments are needed (e.g. --exclude some_directory)
# from docopt import docopt


def find_repos():
    home = os.environ['HOME']
    p = subprocess.Popen('find ' + home + ' -type d -name "*.git"', shell=True, stdout=subprocess.PIPE)

    repo_list = p.communicate()[0].decode('UTF-8').split('\n')
    list_active = [r for r in repo_list if '/.git' in r]
    list_bare = [r for r in repo_list if r not in list_active]

    return list_active, list_bare


def print_repos(bare_repos, active_repos):

    tiny_bar = '-------------------'
    small_bar = tiny_bar * 2
    bar = small_bar * 2

    format_string = small_bar + '\n{0}:\n' + small_bar + '\nREMOTES:\n{1}' # + tiny_bar + '\nSTATUS:\n{2}'

    print(bar)
    print("-- Bare repos (expected to follow the naming convention XXX.git)")
    print(bar)
    for r in bare_repos:
        print(r)
    print('\n' + bar)

    # c) Print active working repos
    print("-- Active repos (characterised by a '.git' folder) and corresponding status/remotes")
    print(bar)
    sep = _path_sep()
    for r in active_repos:
        r_top_level = sep.join(r.split(sep)[:-1])
        os.chdir(r_top_level)
        p_remote = subprocess.Popen('git remote -v', shell=True, stdout=subprocess.PIPE)
        print(format_string.format(r_top_level, _decode_process(p_remote)))
        # p_status = subprocess.Popen('git status -v', shell=True, stdout=subprocess.PIPE)
        # print(format_string.format(r_top_level, _decode_process(p_remote), _decode_process(p_status)))


########################################################
# Private
########################################################
def _path_sep():

    os_type = os.name
    if os_type == 'posix':
        return '/'
    elif os_type == 'nt':
        return '\\'
    else:
        raise SystemError('Unknown os type {}'.format(os_type))

def _decode_process(process):
        return process.communicate()[0].decode('UTF-8')

########################################################
# Main
########################################################
if __name__ == '__main__':
    # args = docopt(__doc__)
    # print(args)

    # a) Get all active and bare repos
    active_repos, bare_repos = find_repos()

    # b) print output
    print_repos(bare_repos, active_repos)
