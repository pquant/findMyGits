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
    repo_list = p . communicate()[0] . decode('UTF-8') . split('\n')[:-1]

    # split bare/active working repos
    list_bare, list_active = [], []
    for r in repo_list:
        if _is_bare_repo_cmd(r):
            list_bare.append(r)
        else:
            list_active.append(r)

    return list_active, list_bare


def print_repos(bare_repos, active_repos):

    # View bare repos
    print(_header_bar)
    print(_TerminalTextColours.BOLD_HEADER +
          "Bare repos (determined using 'git rev-parse --is_bare_repository')" +
          _TerminalTextColours.END)
    print(_header_bar)

    for r in bare_repos:
        print(r)
    print('\n')

    # View active repos and list their remotes and status
    print(_header_bar)
    print(_TerminalTextColours.BOLD_HEADER +
          "Active repos (characterised by a '.git' folder) and corresponding status/remotes" +
          _TerminalTextColours.END)
    print(_header_bar)

    sep = _path_sep()
    for r in active_repos:
        r_top_level = sep.join(r.split(sep)[:-1])
        os.chdir(r_top_level)
        p_remote = subprocess.Popen('git remote -v', shell=True, stdout=subprocess.PIPE)
        p_status = subprocess.Popen('git status | grep "nothing to commit"', shell=True, stdout=subprocess.PIPE)
        remotes_str = p_remote . communicate()[0] . decode('UTF-8')
        status_str  = p_status . communicate()[0] . decode('UTF-8')
        _format_output(r_top_level, remotes_str, status_str)

########################################################
# Private
########################################################
# TODO : check it actually works on Windows
_flags = {'exclude': '--exclude-dirs',
          'include-only': '--include-only'}
_bar_elem_dash = '-'
_bar_elem_hash = '#'
_small_bar = _bar_elem_dash * 40
_header_bar = _bar_elem_hash * 80
_output_template = _small_bar + '\n{0}:\n' + _small_bar + '\nREMOTES:{1}' + '\nSTATUS:{2}'


class _TerminalTextColours:
    BOLD = '\033[1m'
    HEADER = '\033[95m'
    BOLD_HEADER = BOLD + HEADER
    OK = '\033[92m'
    FAIL = '\033[91m'
    END = '\033[0m'


def _path_sep():

    os_type = os.name
    if os_type == 'posix':
        return '/'
    elif os_type == 'nt':
        raise SystemError("findmygits does not yet handle Windows")#return '\\'
    else:
        raise SystemError('Unknown os type {}'.format(os_type))


def home_dir():

    os_type = os.name #os.environ['OS']
    if os_type == 'posix':
        return os.environ['HOME']
    elif os_type == 'nt':
        raise SystemError("findmygits does not yet handle Windows")#return os.environ['HOME']
    else:
        raise SystemError('Unknown os type {}'.format(os_type))


def _is_bare_repo_cmd(repo):
    os.chdir(repo)
    cmd = 'git rev-parse --is-bare-repository'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    decoded = p . communicate()[0] . decode('UTF-8') . split('\n')[0] . upper()
    # tried to catch Exception from Popen, couldn't
    # If Popen fails, it does however return '' when process decoded
    if decoded == '':
        err_mssg = _TerminalTextColours.FAIL + \
                   '\nRepo {0} was initially considered as a valid git repo on the basis that it has *.git ' \
                   'as part of its name, but running "git rev-parse --is-bare-repository" returned ' \
                   '"fatal: Not a git repository (or any of the parent directories)"' + _TerminalTextColours.END

        raise Exception(err_mssg.format(repo))
    return decoded == 'TRUE'


def _check_flag_consistency(exclude_dirs, only_dirs):
    both_not_none = exclude_dirs is not None and only_dirs is not None
    if both_not_none:
        raise SystemExit('One of ' + _flags['exclude'] + ' or ' + _flags['include-only'] + ' flags expected, not both')
    if exclude_dirs is []:
        raise SystemExit(_flags['exclude'] + ' flag provided without directories to exclude')


def _write_cmd(exclude_dirs, only_dirs):
    home = home_dir()
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


def _format_output(root_str, remotes_str, status_str):
    # Highlight repos without remote
    remotes_str = _TerminalTextColours.FAIL + 'NONE\n' + _TerminalTextColours.END if remotes_str == '' \
        else '\n' + remotes_str
    status_str = _TerminalTextColours.FAIL + 'MODIFIED\n' + _TerminalTextColours.END if status_str == '' \
        else _TerminalTextColours.OK + 'CLEAN\n' + _TerminalTextColours.END
    print(_output_template.format(root_str, remotes_str, status_str))


########################################################
# Main
########################################################
if __name__ == '__main__':
    # Define ParserExtract args from command-line
    parser = argparse.ArgumentParser('Lists all local git repos on your computer. Prints bare repos and working repos (with corresponding remotes and statuses')
    parser.add_argument(_flags['exclude'], nargs='*', dest='exclude', metavar='dir',  help='Directories to exclude')
    parser.add_argument(_flags['include-only'], nargs=1, dest='include_only', metavar='dir',  help='One Directory to include exclusively')
    args = parser.parse_args()
    exclude_dirs = args.exclude
    include_only_dir = args.include_only
    # Get all active and bare repos
    active_repos, bare_repos = find_repos(exclude_dirs, include_only_dir)
    # print output
    print_repos(bare_repos, active_repos)
