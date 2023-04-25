#!/bin/python3
"""Configure a fedora system."""

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

    #### Bootstrap prework to make jtools available for the rest of the script.
    if len(sys.argv) == 1:  
        # get git, pip, and jtools
        run(lex(f'sudo dnf install -y git'))
        run(lex(f'sudo dnf install -y pip'))
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
    inst.set_action('install some repositories: rpm fusion free and non-free, ')
    fedora_version = run(lex('rpm -E %fedora'), capture_output=True, text=True).stdout.strip()
    outcome = inst.chain([
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm"',
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm"',
    ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    


    #### install packages
    inst.set_action('install some software: ffmpeg, multimedia codecs, mesa drivers')
    outcome = inst.chain([
        'sudo dnf -y swap ffmpeg-free ffmpeg --allowerasing',
        'sudo dnf -y groupupdate multimedia --setop="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin',
        'sudo dnf -y groupupdate sound-and-video',
        'sudo dnf -y swap mesa-va-drivers mesa-va-drivers-freeworld',
        'sudo dnf -y swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld',
    ])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)


    #### gcc
    inst.set_action('get gcc')
    outcome = inst.chain([inst.inst_cmd('gcc')])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)

    

    #### misc stuff
    inst.set_action('hostname')
    outcome = inst.chain([f'hostnamectl set-hostname {hostname}'])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)



    #### make ssh keys configure sshd 
    inst.set_action('generate SSH keys and configure sshd')
    if not opath.exists(f'{home}/.ssh/id_ed25519'): 
        outcome = inst.chain([f'ssh-keygen -N "" -t ed25519 -f {home}/.ssh/id_ed25519'])
    outcome = outcome and inst.chain([f'sudo cp {appdir}/resources/configs/sshd_config /etc/ssh/sshd_config'])
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    


    #### install Github client and add ssh keys to github        
    inst.set_action('install github cli and add ssh to github')
    outcome = inst.chain([
        'sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo',
        'sudo dnf -y install gh'
    ])
    if outcome:
        # can't use chain because we need to interact with this command alot. 
        a = run(lex('gh auth login -p https -w -s admin:public_key')).returncode
        b = run(lex(f'gh ssh-key add {home}/.ssh/id_ed25519.pub --title "{hostname}"')).returncode
    outcome = outcome and (a + b == 0)
    inst.log(outcome, inst.curraction)
    inst.set_result(outcome)
    


    #### clone my usual repos into git-repos/ 
    inst.set_action('clone my repos from github')
    repos = ['python-jtools', 'linux-automation', 'Croon', 'old-code-archive',
             'experiments', 'project-euler', 'misc-db-files']
    clone_cmds = [f'git clone git@github.com:umbral-tension/{x} {git_repos}/{x}' for x in repos]
    outcome = inst.chain(clone_cmds, ignore_exit_code=True)
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



    #### cleanup
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