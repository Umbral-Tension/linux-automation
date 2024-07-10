""" Configure a fresh debian or redhat based linux installation with creature comforts"""

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
import subprocess
from subprocess import run
import traceback
from datetime import datetime
import platform



# environment info 
home = os.environ['HOME']
git_repos = opath.join(home, 'jdata/git-repos')
os.makedirs(git_repos, exist_ok=True)
installerdir = opath.dirname(opath.realpath(__file__))
appdir = opath.dirname(installerdir)
appname = opath.basename(appdir)
hostname = None
os_list = {'debian':'apt', 'ubuntu':'apt', 'mint':'apt', 'fedora':'dnf'}
try:
    osname = [x for x in os_list.keys() if x in platform.freedesktop_os_release()['ID']][0]
except IndexError:
    print('not a supported operating system')
    sys.exit()
pm = os_list[osname] # package manager



def bootstrap():
    """Prework to make jtools available for the rest of the script. """
    # get git, pip, and jtools
    print('---> Installing git, pip, and jtools')
    try:
        run(lex(f'sudo {pm} install -y git'))
        run(lex(f'sudo {pm} install -y pip'))
        run(lex(f'pip -q install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein'))
        if not opath.exists(f'{installerdir}/localjtools'):
            run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))
    except: 
        print('bootstrap failled')
        sys.exit()
    print('---> success (git,pip,jtools)')


