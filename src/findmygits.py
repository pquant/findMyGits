import os
from subprocess import Popen, PIPE
import argparse
from pprint import pprint


def find_repos(ex_dirs=None, only_dirs=None):

    _check_flag_consistency(ex_dirs, only_dirs)

    shell_find_cmd = _write_cmd(ex_dirs, only_dirs)

    repos      = Popen(shell_find_cmd, shell = True, stdout = PIPE) \
               . communicate()[0] \
               . decode('UTF-8') \
               . split('\n')[:-1]

    bares, actives = [], []

    for r in repos:
        if    _is_bare_repo(r):    bares  .append(r)
        else                  :    actives.append(r)

    return actives, bares


def print_repos(bares, actives):

    print(_header_bar)
    print( _TermColours.BOLD_HEADER
         + "Bare repos (determined using 'git rev-parse --is_baresitory')"
         + _TermColours.END)
    print(_header_bar)

    for r in bares:  print(r)

    print('\n')

    print(_header_bar)
    print( _TermColours.BOLD_HEADER
         + "Active repos (characterised by a '.git' folder) and corresponding status/remotes"
         + _TermColours.END)
    print(_header_bar)

    sep = _path_sep()
    for r in actives:
        r_top_level = sep.join(r.split(sep)[:-1])

        os.chdir(r_top_level)

        p_remote = Popen('git remote -v', shell=True, stdout=PIPE)
        p_status = Popen('git status | grep "nothing to commit"', shell=True, stdout=PIPE)

        remotes_str = p_remote . communicate()[0] . decode('UTF-8')
        status_str  = p_status . communicate()[0] . decode('UTF-8')

        _format_output(r_top_level, remotes_str, status_str)

########################################################
# Private
########################################################
# TODO : check it actually works on Windows
_flags = {'exclude': '--exclude-dirs',   'include-only': '--include-only'}
_bar_elem_dash = '-'
_bar_elem_hash = '#'
_small_bar  = _bar_elem_dash * 40
_header_bar = _bar_elem_hash * 80
_output_template = _small_bar + '\n{0}:\n' + _small_bar + '\nREMOTES:{1}' + '\nSTATUS:{2}'


class _TermColours:
    BOLD    = '\033[1m'
    HEADER  = '\033[95m'
    BOLD_HEADER = BOLD + HEADER
    OK    = '\033[92m'
    FAIL  = '\033[91m'
    END   = '\033[0m'


def _path_sep():

    os_ty = os.name
    if   os_ty == 'posix':    return '/'
    elif os_ty == 'nt':       raise SystemError("findmygits does not yet handle Windows")
    else:                     raise SystemError('Unknown os type {}'.format(os_ty))


def home_dir():

    os_ty = os.name
    if   os_ty == 'posix':  return os.environ['HOME']
    elif os_ty == 'nt':     raise SystemError("findmygits does not yet handle Windows")
    else:                   raise SystemError('Unknown os type {}'.format(os_ty))


def _is_bare_repo(repo):

    os.chdir(repo)

    decoded = Popen('git rev-parse --is-bare-repository', shell=True, stdout=PIPE) \
            . communicate()[0] \
            . decode('UTF-8') \
            . split('\n')[0] \
            . upper()

    # tried to catch Exception from Popen, couldn't
    # If Popen fails, it does however return '' when process decoded
    if decoded == '':
        err_mssg = _TermColours.FAIL + \
                   '\nRepo {0} was initially considered as a valid git repo on the basis that it has *.git ' \
                   'as part of its name, but running "git rev-parse --is-bare-repository" returned ' \
                   '"fatal: Not a git repository (or any of the parent directories)"' + _TermColours.END

        raise Exception(err_mssg.format(repo))
    return decoded == 'TRUE'


def _check_flag_consistency(ex_dirs, only_dirs):

    if ex_dirs is not None and only_dirs is not None:
        raise SystemExit('One of ' + _flags['exclude'] + ' or ' + _flags['include-only'] + ' flags expected, not both')

    if ex_dirs is []:
        raise SystemExit(_flags['exclude'] + ' flag provided without directories to exclude')


def _write_cmd(ex_dirs, only_dirs):

    home           = home_dir()
    shell_find_cmd = ''

    if only_dirs is not None:
        for d in only_dirs:
            shell_find_cmd = 'find ' + d + ' -type d -name "*.git"' # FIXME: missing += here?

    elif ex_dirs is not None:
        shell_find_cmd = 'find ' + home + ' -type d -name "*.git"'
        for d in ex_dirs:
            shell_find_cmd += '| grep -v ' + d

    else:
        shell_find_cmd = 'find ' + home + ' -type d -name "*.git"'

    return shell_find_cmd


def _format_output(root: str, remotes: str, status: str):

    remotes = _TermColours.FAIL + 'NONE\n'     + _TermColours.END if remotes == '' else '\n' + remotes
    status  = _TermColours.FAIL + 'MODIFIED\n' + _TermColours.END if status == ''  else _TermColours.OK + 'CLEAN\n' + _TermColours.END

    print(_output_template.format(root, remotes, status))


########################################################
# Main
########################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser('Lists all local git repos on your computer. Prints bare repos and working repos (with corresponding remotes and statuses')
    parser.add_argument(_flags['exclude'],      nargs='*', dest='exclude',      metavar='dir',  help='Directories to exclude')
    parser.add_argument(_flags['include-only'], nargs=1,   dest='include_only', metavar='dir',  help='One Directory to include exclusively')

    args    = parser.parse_args()

    ex_dirs          = args.exclude
    include_only_dir = args.include_only

    actives, bares = find_repos(ex_dirs, include_only_dir)

    print_repos(bares, actives)
