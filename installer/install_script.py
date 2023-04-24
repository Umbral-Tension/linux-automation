#!/bin/python3

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
    git_repos = opath.join(home, '@data/git-repos')
    os.makedirs(git_repos, exist_ok=True)
    installerdir = opath.dirname(opath.realpath(__file__))
    appdir = opath.dirname(installerdir)
    appname = opath.basename(appdir)

    ### Bootstrap prework to make jtools available for the rest of the script.
    if len(sys.argv) == 1:
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

        # have to relaunch or the modules that were just installed aren't found for import 
        os.execl(sys.argv[0], sys.argv[0], 'continuation')

    
    ### Begin the rest of installation
    sys.path.append(f'{installerdir}/localjtools/src/')
    from jtools import jconsole as jc
    from jtools.shelldo import Shelldo
    inst = Shelldo()

    # Collect input
    hostname = input(jc.yellow('What should be the hostname for this machine?: '))


    # # gcc
    # inst.set_action('get gcc')
    # outcome = inst.chain([inst.inst_cmd('gcc')])
    # inst.log(outcome, inst.curraction)
    # inst.set_result(outcome)

    
    # misc stuff
    inst.set_action('hostname')
    outcome = inst.chain(['hostnamectl set-hostname {hostname}'])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)

    # make ssh keys configure sshd 
    inst.set_action('generate SSH keys and configure sshd')
    if not opath.exists(f'{home}/.ssh/id_ed25519'): 
        outcome = inst.chain([f'ssh-keygen -N "" -t ed25519 -f {home}/.ssh/id_ed25519'])
    outcome = outcome and inst.chain([f'sudo cp {appdir}/resources/configs/sshd_config /etc/ssh/sshd_config'])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    
    # install Github client and add ssh keys to github        
    inst.set_action('install github cli and add ssh to github')
    gh_inst = {
        'apt': [
            'type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)',  
            'curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg',
            'sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg',
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null',
            'sudo apt update',
            'sudo apt -y install gh '
        ],
        'dnf': [
            'sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo',
            'sudo dnf -y install gh'
    ]}    
    outcome = inst.chain(gh_inst[inst.package_manager])    
    if outcome:
        # can't use chain because we need to interact with this command alot. 
        a = run(lex('gh auth login -p https -w'))
        b = run(lex('gh auth refresh -h github.com -s admin:public_key'))
        c = run(lex(f'gh ssh-key add {home}/.ssh/id_ed25519.pub --title "{hostname}"'))
    outcome = outcome and a + b + c == 0
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    
        
        
        
        
        
        
        

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

    # # keyd
    # inst.set_action('download and install keyd')
    # keyd_conf = f'{appdir}/resources/configs/my_keyd.conf'
    # inst.chain([f'git clone https://github.com/rvaiya/keyd {installerdir}/keyd'])
    # os.chdir(f'{installerdir}/keyd')
    # outcome = inst.chain([
    #     'make',
    #     'sudo make install',
    #     'sudo systemctl enable keyd',
    #     f'sudo cp {keyd_conf} /etc/keyd/default.conf',
    #     'sudo systemctl restart keyd',
    #     ])
    # inst.log(outcome, inst.curraction)
    # inst.set_result(outcome)
    # os.chdir(installerdir)


    
    # # bashrc, jrouter, dconf
    # inst.set_action('bashrc, jrouter, dconf')
    # with open(f'{home}/.bashrc', 'a') as f:
    #     f.writelines([f'. "{appdir}/resources/configs/bashrc fedora"\n'])
    
    # try:
    #     os.remove('/home/jeremy/bin/jrouter')
    # except FileNotFoundError:
    #     pass
    # os.makedirs('/home/jeremy/bin', exist_ok=True)
    # os.symlink(f'{appdir}/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')         
    # os.system(f'dconf load -f /org/gnome/settings-daemon/plugins/media-keys/ < "{appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:settings-daemon:plugins:media-keys:"')
    # inst.log(True, inst.curraction)
    # inst.set_result(True)

    # cleanup
    inst.set_action('cleanup')
    outcome = inst.chain([
        f'rm -rf {installerdir}/keyd',
        f'rm -rf {installerdir}/localjtools',
        #inst.inst_cmd('gh', uninstall=True),
    ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)

    # Show final report
    inst.report()