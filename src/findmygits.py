import os
import subprocess
import argparse
from pprint import pprint


def find_repos(exclude_dirs=None, only_dirs=None):
    # Check flag consistency
    _check_flag_consistency(exclude_dirs, only_dirs)
    # Define shell command to run
    shell_find_cmd = _write_cmd(exclude_dirs, only_dirs)
    # Integrate shell command in a subprocess and run it with shell
    p = subprocess.Popen(shell_find_cmd, shell=True, stdout=subprocess.PIPE)
    # Retrieve output
    repo_list = _decode_process(p).split('\n')[:-1]
    # split bare/active working repos
    list_bare, list_active = [], []
    for r in repo_list:
        if _is_bare_repo_cmd(r):
            list_bare.append(r)
        else:
            list_active.append(r)

    return list_active, list_bare


def print_repos(bare_repos, active_repos):

    print(_TerminalTextColours.BOLD + _bar + _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD + _bar + _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD_HEADER +
          "Bare repos (determined using 'git rev-parse --is_bare_repository')" +
          _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD + _bar + _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD + _bar + _TerminalTextColours.END)

    for r in bare_repos:
        print(r)
    print('\n')

    print(_TerminalTextColours.BOLD + _bar + _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD  + _bar + _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD_HEADER +
          "Active repos (characterised by a '.git' folder) and corresponding status/remotes" +
          _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD  + _bar + _TerminalTextColours.END)
    print(_TerminalTextColours.BOLD + _bar + _TerminalTextColours.END)

    sep = _path_sep()
    for r in active_repos:
        r_top_level = sep.join(r.split(sep)[:-1])
        os.chdir(r_top_level)
        p_remote = subprocess.Popen('git remote -v', shell=True, stdout=subprocess.PIPE)
        remotes_str = _decode_process(p_remote)
        _format_output(r_top_level, remotes_str)


def _format_output(root_str, remotes_str):
    # Highlight repos without remote
    remotes_str = _TerminalTextColours.WARNING + 'NONE\n' + _TerminalTextColours.END if remotes_str == '' else '\n' + remotes_str
    print(_output_template.format(root_str, remotes_str))


########################################################
# Private
########################################################
# TODO : check it actually works on Windows
_flags = {'exclude': '--exclude-dirs',
          'include-only': '--include-only'}

_tiny_bar = '-------------------'
_small_bar = _tiny_bar * 2
_bar = _small_bar * 2
_output_template = _small_bar + '\n{0}:\n' + _small_bar + '\nREMOTES:{1}'


class _TerminalTextColours:
    BOLD = '\033[1m'
    BOLD_HEADER = '\033[1m\033[95m'
    OK = '\033[92m'
    WARNING = '\033[91m'
    END = '\033[0m'


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


def _is_bare_repo_cmd(repo):
    os.chdir(repo)
    cmd = 'git rev-parse --is-bare-repository'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    is_bare_repo = _decode_process(p).split('\n')[0].upper() == 'TRUE'
    return is_bare_repo


def _check_flag_consistency(exclude_dirs, only_dirs):
    both_not_none = exclude_dirs is not None and only_dirs is not None
    if both_not_none:
        raise SystemExit('One of ' + _flags['exclude'] + ' or ' + _flags['include-only'] + ' flags expected, not both')
    if exclude_dirs is []:
        raise SystemExit(_flags['exclude'] + ' flag provided without directories to exclude')


def _write_cmd(exclude_dirs, only_dirs):
    home = os.environ['HOME']
    shell_find_cmd = ''
    # Restrict to dome dirs only
    if only_dirs is not None:
        for d in only_dirs:
            shell_find_cmd = 'find ' + d + ' -type d -name "*.git"'
    # Add directories to exclude from search, if specified by user
    elif exclude_dirs is not None:
        shell_find_cmd = 'find ' + home + ' -type d -name "*.git"'
        for d in exclude_dirs:
            shell_find_cmd += '| grep -v ' + d
    else:
        shell_find_cmd = 'find ' + home + ' -type d -name "*.git"'

    return shell_find_cmd


########################################################
# Main
########################################################
if __name__ == '__main__':
    # Define ParserExtract args from command-line
    parser = argparse.ArgumentParser('Lists all local git repos on your computer. Built on Ubuntu 15.10 (Wily)')
    parser.add_argument(_flags['exclude'], nargs='*', dest='exclude', metavar='dir',  help='Directories to exclude')
    parser.add_argument(_flags['include-only'], nargs=1, dest='include_only', metavar='dir',  help='One Directory to include exclusively')
    args = parser.parse_args()
    exclude_dirs = args.exclude
    include_only_dir = args.include_only
    # Get all active and bare repos
    active_repos, bare_repos = find_repos(exclude_dirs, include_only_dir)
    # print output
    print_repos(bare_repos, active_repos)
