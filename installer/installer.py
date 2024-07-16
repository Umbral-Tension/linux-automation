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

with open(f'{appdir}/resources/configs/platform_info.json', 'r') as f:
    platform = json.load(f)
os_release=osplatform.freedesktop_os_release()['ID']
try:
    platform = platform['os_list'][os_release]
except NameError:
    print('not a supported operating system')
    sys.exit()


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


def install(package):
    """return a platform specific installation command"""
    return f"{platform['install_cmd']} {package}"

def uninstall(package):
    """return a platform specific uninstallation command"""
    return f"{platform['uninstall_cmd']} {package}"




if __name__ == '__main__':

    print('\n/////////////////////////////////////////////////')
    print('////////   linux-automation installer  //////////\n')
    
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

    print(jc.blue('bluetext'))

    jc.test(platform)