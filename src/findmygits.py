import os
from subprocess import Popen, PIPE
import argparse
from pprint import pprint


def find_repos(ex_dirs=None, only_dirs=None):

    _check_flag_consistency(ex_dirs, only_dirs)

    shell_find_cmd = _write_cmd(ex_dirs, only_dirs)

    repos = Popen(shell_find_cmd, shell = True, stdout = PIPE) \
          . communicate()[0] \
          . decode('UTF-8') \
          . split('\n')[:-1]

    bares, actives = [], []

    for r in repos:
        if    _is_bare_repo(r):    bares  .append(r)
        else                  :    actives.append(r)

    return actives, bares


def print_repos(bares, actives):

    _header_bar = '#' * 80

    print( _header_bar
         + _TermColours.BOLD_HEADER
         + "\nBare repos (determined using 'git rev-parse --is_baresitory')\n"
         + _TermColours.END
         +_header_bar)

    for r in bares:  print(r)

    print( '\n' + _header_bar
         + _TermColours.BOLD_HEADER
         + "\nActive repos (characterised by a '.git' folder) and corresponding status/remotes\n"
         + _TermColours.END
         + _header_bar)

    sep = _path_sep()

    for r in actives:
        root = sep.join(r.split(sep)[:-1])

        os.chdir(root)

        #p_status = Popen('git status | grep -E "'+status_patterns+'"', shell=True, stdout=PIPE)
        remotes = Popen('git remote -v', shell=True, stdout=PIPE) . communicate()[0] . decode('UTF-8')
        status  = Popen('git status',    shell=True, stdout=PIPE) . communicate()[0] . decode('UTF-8')

        sync_remote_matches, changes_matches = [], []

        for s in status.split('\n'):
            if   s.startswith("Your branch is ahead"):      sync_remote_matches.append(_TermColours.BAD+s+_TermColours.END)
            elif s.startswith("Your branch is behind"):     sync_remote_matches.append(_TermColours.BAD+s+_TermColours.END)
            elif s.startswith("Your branch is up-to-date"): sync_remote_matches.append(_TermColours.OK +s+_TermColours.END)
            elif s.startswith("Changes not staged"):        changes_matches    .append(_TermColours.BAD+s+_TermColours.END)
            elif s.startswith("Changes to be committed"):   changes_matches    .append(_TermColours.BAD+s+_TermColours.END)
            elif s.startswith("nothing to commit"):         changes_matches    .append(_TermColours.OK +s+_TermColours.END)

        #print("Zi status iz: "+status)
        #print("sync_remote_matches: "+str(sync_remote_matches))
        #print("changes_matches: "+str(changes_matches))

        output_str = ('-'*40)+'\n{}:\n'+('-'*40)+'\nREMOTES:{}'+'\nREMOTE SYNC:{}'+'\nCHANGES:{}'
        print( output_str . format( root
                                  , _TermColours.BAD+'NONE\n'+_TermColours.END if remotes == '' else '\n' + remotes
                                  , ' '.join(sync_remote_matches)
                                  , ' '.join(changes_matches)
                                  ))


########################################################
# Private
########################################################
def _check_flag_consistency(ex_dirs, only_dirs):

    if ex_dirs is not None and only_dirs is not None:
        raise SystemExit('One of '+_flags['exclude']+' or '+_flags['include-only']+' flags expected, not both')

    if ex_dirs is []:
        raise SystemExit(_flags['exclude']+' flag provided without directories to exclude')

def _write_cmd(ex_dirs, only_dirs):

    def home_dir():

        os_ty = os.name
        if   os_ty == 'posix':  return os.environ['HOME']
        elif os_ty == 'nt':     raise SystemError("findmygits does not yet handle Windows")
        else:                   raise SystemError('Unknown os type {}'.format(os_ty))

    if only_dirs is not None:
        for d in only_dirs:
            shell_find_cmd = 'find '+d+' -type d -name "*.git"' # FIXME: missing += here?
    elif ex_dirs is not None:
        shell_find_cmd = 'find '+home_dir()+' -type d -name "*.git"'
        for d in ex_dirs:
            shell_find_cmd += '| grep -v ' + d
    else:
        shell_find_cmd = 'find '+home_dir()+' -type d -name "*.git"'

    return shell_find_cmd

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
        raise Exception(_TermColours.BAD
                       + '\nRepo'+repo+' was initially considered as a valid git repo on the basis that it has *.git ' \
                         'as part of its name, but running "git rev-parse --is-bare-repository" returned ' \
                         '"fatal: Not a git repository (or any of the parent directories)"'
                       + _TermColours.END)

    return decoded == 'TRUE'


class _TermColours:
    BOLD    = '\033[1m'
    HEADER  = '\033[95m'
    BOLD_HEADER = BOLD + HEADER
    OK    = '\033[92m'
    BAD  = '\033[91m'
    END   = '\033[0m'

def _path_sep():

    os_ty = os.name
    if   os_ty == 'posix':    return '/'
    elif os_ty == 'nt':       raise SystemError("findmygits does not yet handle Windows")
    else:                     raise SystemError('Unknown os type {}'.format(os_ty))

########################################################
# Main
########################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser('Lists all local git repos on your computer. Prints bare repos and working repos (with corresponding remotes and statuses')
    parser.add_argument('--exclude-dirs', nargs='*', dest='exclude',      metavar='dir',  help='Directories to exclude')
    parser.add_argument('--include-only', nargs=1,   dest='include_only', metavar='dir',  help='One Directory to include exclusively')

    args    = parser.parse_args()

    ex_dirs          = args.exclude
    include_only_dir = args.include_only

    actives, bares = find_repos(ex_dirs, include_only_dir)

    print_repos(bares, actives)
