#!/bin/python3
""" configure a linux system as far as is possible without much
distribution-specific information such as package manager specifics,
distro-specific repositories urls, desktop environment details...etc"""

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
from subprocess import Popen, PIPE, run
import traceback
from datetime import datetime




if __name__ == '__main__':
    print('\n/////////////////////////////////////////////////')
    print('////////   linux-automation installer  //////////\n')
    
    # relevant paths
    home = os.environ['HOME']
    git_repos = opath.join(home, 'jdata/git-repos')
    os.makedirs(git_repos, exist_ok=True)
    installerdir = opath.dirname(opath.realpath(__file__))
    appdir = opath.dirname(installerdir)
    appname = opath.basename(appdir)

    # determin package manager
    pm = None
    for x in ['apt', 'dnf']:
        try:
            run([x], capture_output=True)
            pm = x
        except FileNotFoundError:
            pass
    if pm is None:
        print('No usable package manager found. Exitting now.')
        sys.exit()
    
    # determine terminal (mostly for 'keyd -m' invocation later on)
    pass

    #### Bootstrap prework to make jtools available for the rest of the script.
    if len(sys.argv) == 1:  
        # get git, pip, and jtools
        run(lex(f'sudo {pm} install -y git'))
        run(lex(f'sudo {pm} install -y pip'))
        run(lex(f'pip install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein'))
        run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))
        # have to relaunch or the modules that were just installed aren't importable
        os.execl(sys.argv[0], sys.argv[0], 'continuation')
    

    #### Begin the rest of installation
    sys.path.append(f'{installerdir}/localjtools/src/')
    from jtools import jconsole as jc
    from jtools.shelldo import Shelldo
    inst = Shelldo()



    #### Collect input
    hostname = input(jc.yellow('What should be the hostname for this machine?: '))



    #### install repos
    inst.set_action('install some repositories: ...')
    outcome = inst.chain([
        'echo nothing here yet'
    ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    


    #### install packages
    inst.set_action('install some software: gcc, build-essential')
    outcome = inst.chain([
        f'sudo {pm} -y install gcc'
        f'sudo {pm} -y install build-essential'
    ], ignore_exit_code=True)
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)



    #### misc stuff
    inst.set_action('hostname')
    outcome = inst.chain(['hostnamectl set-hostname {hostname}'])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)



    #### make ssh keys 
    inst.set_action('generate SSH keys and configure sshd')
    if not opath.exists(f'{home}/.ssh/id_ed25519'): 
        outcome = inst.chain([f'ssh-keygen -N "" -C {hostname} -t ed25519 -f {home}/.ssh/id_ed25519'])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
        


    #### keyd
    inst.set_action('download and install keyd')
    inst.chain([f'git clone https://github.com/rvaiya/keyd {installerdir}/keyd'])
    os.chdir(f'{installerdir}/keyd')
    outcome = inst.chain([
        'make',
        'sudo make install',
        'sudo systemctl enable keyd',
        'sudo systemctl restart keyd',
        ])
    os.chdir(installerdir)



    # exhort user to get keyboard device id 
    input(jc.yellow("Opening a terminal running keyd -m. Copy the device ids you want and paste them here in a comma seperated list.\n...press enter when ready"))
    run(lex('gnome-terminal -- sudo keyd -m'))
    device_ids = input(jc.yellow("device ids: "))
    device_ids = device_ids.replace(',', '\n,').replace(' ','').split(',')
    keyd_conf = f'{appdir}/resources/configs/my_keyd.conf'
    temp_conf = f'{installerdir}/temp_keyd_conf'
    with open(temp_conf, 'w') as tempfile, open(keyd_conf, 'r') as keydfile:
        lines = ['[ids]\n'] + device_ids + keydfile.readlines()
        tempfile.writelines(lines)
    
    outcome2 = inst.chain([
        f'sudo cp {temp_conf} /etc/keyd/default.conf',
        'sudo systemctl restart keyd',
    ])
    os.remove(temp_conf)
    outcome = outcome and outcome2
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)



    #### bashrc, jrouter, dconf
    inst.set_action('bashrc, jrouter symlink')
    with open(f'{home}/.bashrc', 'a') as f:
        f.writelines([f'. "{appdir}/resources/configs/bashrc fedora"\n'])
    
    try:
        os.remove('/home/jeremy/bin/jrouter')
    except FileNotFoundError:
        pass
    os.makedirs('/home/jeremy/bin', exist_ok=True)
    os.symlink(f'{appdir}/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')         
    inst.log(True, inst.curraction)
    inst.set_result(True)



    #### cleanup
    inst.set_action('cleanup')
    outcome = inst.chain([
        f'rm -rf {installerdir}/keyd',
        f'rm -rf {installerdir}/localjtools',
    ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)



    # Show final report
    inst.report()