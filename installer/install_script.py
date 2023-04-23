#!/bin/python3

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
from subprocess import Popen, PIPE, run
import traceback
from datetime import datetime



if __name__ == '__main__':
    print('/////////////////////////////////////////////////')
    print('////////   linux-automation installer  //////////\n')
    # relevant paths
    home = os.environ['HOME']
    git_repos = opath.join(home, '@data/git-repos')
    os.makedirs(git_repos, exist_ok=True)
    installerdir = opath.dirname(opath.realpath(__file__))
    appdir = opath.dirname(installerdir)
    appname = opath.basename(appdir)



    ### Bootstrap phase
    # need to do a few thing so jtools can be used for the rest of the script. 
    # determin package manager to use
    try:
        run(['apt'], capture_output=True)
        pm = 'apt'
    except FileNotFoundError:
        try:
            run(['dnf'], capture_output=True)
            pm = 'dnf'
        except FileNotFoundError:
            print('shelldo: No supported package manager found (apt, dnf)')    
    # get git, pip, and jtools
    run(lex(f'sudo {pm} install -y git'))
    run(lex(f'sudo {pm} install -y pip'))
    run(lex(f'pip install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein'))
    run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))



    sys.path.append(f'{installerdir}/localjtools/src/')
    from jtools import jconsole as jc
    from jtools.shelldo import Shelldo

    inst = Shelldo()

   
    # gcc
    inst.set_action('get gcc')
    outcome = inst.chain([inst.inst_cmd('gcc')])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)

    # #Generate SSH keys
    # inst.set_action('generate SSH keys and add to Github')
    # outcome = inst.chain([
    #     f'ssh-keygen -N "" -t ed25519 -f {home}/.ssh/id_ed25519'
    # ])

    # #TODO install Github cli and authenticiate. 
    # # clone my usual repos into git-repos/ 
    # inst.set_action('get misc-db-files repository')
    # repos = ['python-jtools', 'linux-automation', 'Croon', 'old-code-archive',
    #          'experiments', 'project-euler']
    # for x in repos:
    #     apath = f'{git_repos}/x'
    # outcome = inst.chain([
    #     f'git clone git@github.com:umbral-tension/{x} {git_repos}/misc-db-files'
    # ])
    # inst.log(outcome, inst.curraction)
    # inst.set_result(outcome)

    # keyd
    inst.set_action('download and install keyd')
    keyd_conf = f'{appdir}/resources/configs/my_keyd.conf'
    inst.chain([f'git clone https://github.com/rvaiya/keyd {installerdir}/keyd'])
    os.chdir(f'{installerdir}/keyd')
    outcome = inst.chain([
        'make',
        'sudo make install',
        'sudo systemctl enable keyd',
        f'sudo cp {keyd_conf} /etc/keyd/default.conf',
        'sudo systemctl restart keyd',
        ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    os.chdir(installerdir)


    
    # bashrc, jrouter, dconf
    inst.set_action('bashrc, jrouter, dconf')
    with open(f'{home}/.bashrc', 'a') as f:
        f.writelines([f'. "{appdir}/resources/configs/bashrc fedora"\n'])
    
    try:
        os.remove('/home/jeremy/bin/jrouter')
    except FileNotFoundError:
        pass
    os.makedirs('/home/jeremy/bin', exist_ok=True)
    os.symlink(f'{appdir}/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')         
    os.system(f'dconf load -f /org/gnome/settings-daemon/plugins/media-keys/ < "{appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:settings-daemon:plugins:media-keys:"')
    inst.log(True, inst.curraction)
    inst.set_result(True)

    # cleanup
    inst.set_action('cleanup')
    outcome = inst.chain([
        f'rm -rf {installerdir}/keyd',
        f'rm -rf {installerdir}/localjtools',
    ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)

    # Show final report
    inst.report()