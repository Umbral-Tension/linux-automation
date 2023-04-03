import os, shutil, sys
import os.path as opath
from shlex import split as lex
from subprocess import run

from datetime import datetime

#TODO 
# 1. add /src to PATH  in ~/.profile  ||  put links to python files in ~/.local/bin
# 2. do dconf load to set up settings and keybindings
# 4. install desired programs
# 6. configure git, samba, keyd, bashrc, ssh, ufw firewall, pythonpath
#

def yesno(message ):
    while(True):
        response = input(f'{message}? (y/n)')
        if response.casefold() == 'y':
            return True
        if response.casefold() == 'n':
            return False

def exit_(message):
    print(message)
    exit()



# paths
home = os.environ['HOME']
git_repos = opath.join(home, 'Desktop/git-repos')
appdir = opath.dirname(__file__)
appname = opath.basename(appdir)
install_log = opath.join(appdir, f'logs/install log {datetime.now()}')

# current step in the installatino process
currstep = ''

def step(description, print_now=True, nocolor=False):
    """update and print the current installation step."""
    global currstep
    currstep = description
    if print_now:
        if nocolor:
            print(f'----- {currstep}')
        else:
            print(jc.bold(jc.blue(f'----- {currstep}')))


def log(result, action=None):
    if action is None:
        action = currstep
    """Add log the result of action. Default action is the currstep."""
    with open(install_log, 'a') as log:
        log.writelines('\n'.join([str(datetime.now()), '\t'+action, '\t'+result, '\n']))


def chain(cmds):
    """run a series of commands in the shell, returning with False if one in
      the series produces an exit code other than 0."""
    
    for x in cmds:
        try:
            resp = run(lex(x))
            if resp.returncode != 0:
                print(f'failed: {x}')
                return False
        except:
            print(f'failed: {x}')
            log('fail', x)
            return False
    return True


# step('get python packages', nocolor=True)
# chain([
#     'sudo dnf -y install pip',
#     'pip install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy',
# ])

# step('download jtools', nocolor=True)
# if chain([f'git clone https://github.com/umbral-tension/python-jtools {appdir}/localjtools']):
#     shutil.move(f'{appdir}/localjtools/src/jtools/jconsole.py', f'{appdir}/jconsole.py')
#     shutil.rmtree(f'{appdir}/localjtools')
#     import jconsole as jc

import jconsole as jc
step('download and install keyd')
run(lex(f'git clone https://github.com/rvaiya/keyd {appdir}/keyd'))
os.chdir(f'{appdir}/keyd')
chain([
    'make',
    'sudo make install',
    'sudo systemctl enable keyd',
    ])



