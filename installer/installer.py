#!/bin/python3
""" Configure a fresh debian or redhat based linux installation with creature comforts"""

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
import subprocess
from subprocess import run, Popen, PIPE, STDOUT
import traceback
from datetime import datetime
import platform as osplatform
import json

# environment info 
home = os.environ['HOME']
git_repos = opath.join(home, 'jdata/git-repos')
os.makedirs(git_repos, exist_ok=True)
installerdir = opath.dirname(opath.realpath(__file__))
appdir = opath.dirname(installerdir)
appname = opath.basename(appdir)
hostname = None
# detect platform
with open(f'{appdir}/resources/configs/platform_info.json', 'r') as f:
    jsondata = json.load(f)
    os_release=osplatform.freedesktop_os_release()['ID']
    try:
        platform = jsondata['os_list'][os_release]
    except KeyError:
        while(True):
            options = ["quit"] + list(jsondata["os_list"].keys())
            choice=input(f"Didn't detect suitable os. Try with manual selection? options:\n\t{options}]\n? ")
            if choice in options:
                platform = sys.exit() if choice == "quit" else jsondata["os_list"][choice]
                break
            run('clear')
json.dump(jsondata, open(f'{appdir}/resources/configs/platform_info.json', 'w'), indent=3, sort_keys=True)

def install(package):
    """return a platform specific installation command"""
    return f"{platform['install_cmd']} {package}"

def uninstall(package):
    """return a platform specific uninstallation command"""
    return f"{platform['uninstall_cmd']} {package}"




def bootstrap():
    """Prework to make jtools available for the rest of the script. """
    # get git, pip, and jtools
    print('---> Installing git, pip, and jtools')
    try:
        run(platform['update'], shell=True) # needs to be run with string and shell=true due to presence of "&&" in command
        run(lex(install('git')))
        run(lex(install('pip')))
        run(lex(f'pip install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein'))
        if not opath.exists(f'{installerdir}/localjtools'):
            run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))
    except: 
        print('bootstrap failed')
        sys.exit()
    print('---> success (git,pip,jtools)')

def collect_input():
    """collect some initial user input """
    global hostname
    hostname = input(jc.yellow('What should be the hostname for this machine?: '))
    return True

def simple_installs():
    """simple package installs (gcc, tree, qbittorrent...etc)"""
    cmds = [install(x) for x in platform["simple_installs"]]
    outcome = shelldo.chain(cmds)
    return outcome


def cleanup():
    """delete/uninstall unecessary remnants"""
    outcome = shelldo.chain([
        f'rm -rf {installerdir}/keyd',
        f'rm -rf {installerdir}/localjtools',
        uninstall('gh')
    ])
    return outcome


if __name__ == '__main__':

    print('\n/////////////////////////////////////////////////')
    print('////////   linux-automation installer  //////////')
    print(f'Installing for: {platform["name"]}')
    
    ### Bootstrap stuff to make jtools available
    if '--no-bootstrap' not in sys.argv:
        bootstrap()
        # have to relaunch after bootstrap or the modules that were just installed aren't importable
        os.execl(sys.argv[0], sys.argv[0], '--no-bootstrap')


    #### Begin the rest of the installation
    sys.path.append(f'{installerdir}/localjtools/src/')
    from jtools import jconsole as jc
    from jtools.shelldo import Shelldo
    shelldo = Shelldo(installerdir)

     # Master list of available tasks (functions). 
    all_tasks = []
    # Tasks to be performed on this run. The order of these is important and should be changed with care.
    tasks = all_tasks 
    # Tasks to skip on this run. Order is not important. 
    skip_tasks = []
    for t in tasks:
        if t not in skip_tasks:
            shelldo.set_action(t.__doc__)
            outcome = t()
            shelldo.log(outcome, shelldo.curraction)
            shelldo.set_result(outcome)
        
    
    # Show final report
    shelldo.report()

