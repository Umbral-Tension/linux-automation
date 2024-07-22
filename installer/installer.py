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
user = os.environ['USER']
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
        run(platform['update'], shell=True) # needs to be run shell=true due to presence of "&&" in command
        run(lex(install('git')))
        run(lex(install('pip')))
        run(lex(f'pip install ipython PyQt5 pandas mutagen colorama fuzzywuzzy Levenshtein'))
        if not opath.exists(f'{installerdir}/localjtools'):
            run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))
    except: 
        print('bootstrap failed')
        sys.exit()
    print('\n\n---> success (git,pip,jtools)')



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

def set_hostname():
    """set hostname"""
    outcome = False if hostname is None else shelldo.chain([f'hostnamectl set-hostname {hostname}'])
    return outcome

def configure_ssh():
    """generate ssh keys and configure sshd"""
    if not opath.exists(f'{home}/.ssh/id_ed25519'): 
        outcome = shelldo.chain([f'ssh-keygen -N "" -t ed25519 -C "{user}@{hostname}" -f {home}/.ssh/id_ed25519'])
    else:
        outcome = True
    return outcome 

def github_client():
    """install Github client and add ssh keys to github"""
    if platform['pm'] == 'apt':
        outcome = shelldo.chain(['sudo mkdir -p -m 755 /etc/apt/keyrings'])
        a = run('wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null', shell=True).returncode
        b = shelldo.chain(['sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg'])
        c = run('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list', shell=True).returncode
        shelldo.chain([       
            'sudo apt update',
            'sudo apt -y install gh',
        ])
    elif platform['pm'] == 'dnf':
        outcome = shelldo.chain([install('gh')])
    if outcome:
        # can't use chain because we need to interact with this command alot. 
        a = run(lex('gh auth login -p https -w -s admin:public_key')).returncode
        b = run(lex(f'gh ssh-key add {home}/.ssh/id_ed25519.pub --title "{hostname}"')).returncode
    return outcome and a + b == 0

def clone_repos():
    """clone my usual repos into ~/jdata/git-repos/"""
    repos = ['python-jtools', 'linux-automation', 'Croon', 'old-code-archive',
            'experiments', 'project-euler', 'misc-db-files']
    clone_cmds = [f'git clone git@github.com:umbral-tension/{x} {git_repos}/{x}' for x in repos]
    outcome = shelldo.chain(clone_cmds, ignore_exit_code=True)
    return outcome

def keyd():
    """install and configure keyd"""
    shelldo.chain([f'git clone https://github.com/rvaiya/keyd {installerdir}/keyd'])
    os.chdir(f'{installerdir}/keyd')
    outcome = shelldo.chain([
        'make',
        'sudo make install',
        'sudo systemctl enable keyd',
        'sudo systemctl restart keyd',
        ])
    outcome = shelldo.chain([
        f'sudo cp {appdir}/resources/configs/my_keyd.conf /etc/keyd/default.conf',
        'sudo systemctl restart keyd',
    ])
    return outcome


def bashrc():
    """source my .bashrc and .bash_profile customization files"""
    # linux mint doesn't seem to follow .profile precedence rules. It ignores .bash_profile in favor of .profile. 
    profile_loc = ".profile" if platform['name'] == 'linuxmint' else ".bash_profile"
    try:
        with open(f'{home}/.bashrc', 'a') as f:
            f.writelines([f'\n. "{git_repos}/linux-automation/resources/configs/bashrc"\n'])
        with open(f'{home}/{profile_loc}', 'a') as f:
            f.writelines([f'\n. "{git_repos}/linux-automation/resources/configs/bash_profile"\n'])
    except:
        return False
    return True

def place_symlinks():
    """place symlinks to jrouter and other scripts in ~/bin and file manager configs"""
    os.makedirs('/home/jeremy/bin', exist_ok=True)
    try:
        os.remove('/home/jeremy/bin/jrouter')
    except FileNotFoundError:
        pass
    try:
        # ~/bin     
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/jtag_editor', '/home/jeremy/bin/jtag_editor')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/open-with-puddletag', '/home/jeremy/bin/open-with-puddletag')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/string_replace', '/home/jeremy/bin/string_replace')

        # place symlinks to context-menu scripts in file browser's script dir.
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/jtag_editor', '/home/jeremy/.local/share/nemo/scripts/jtag_editor')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/open-with-puddletag', '/home/jeremy/.local/share/nemo/scripts/open-with-puddletag')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/string_replace', '/home/jeremy/.local/share/nemo/scripts/string_replace')

        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/jtag_editor', '/home/jeremy/.local/share/nautilus/scripts/jtag_editor')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/open-with-puddletag', '/home/jeremy/.local/share/nautilus/scripts/open-with-puddletag')
        os.symlink(f'{git_repos}/linux-automation/src/linux_automation/context_menu_scripts/string_replace', '/home/jeremy/.local/share/nautilus/scripts/string_replace')
    except Exception:
        return False
    return True         



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
    all_tasks = [collect_input, simple_installs, set_hostname, configure_ssh, github_client, clone_repos, keyd, bashrc]
    # Tasks to be performed on this run. The order of these is important and should be changed with care.
    tasks = all_tasks 
    # Tasks to skip on this run. Order is not important. 
    skip_tasks = [github_client, clone_repos, set_hostname, simple_installs]
    for t in tasks:
        if t not in skip_tasks:
            shelldo.set_action(t.__doc__)
            outcome = t()
            shelldo.log(outcome, shelldo.curraction)
            shelldo.set_result(outcome)
        
    
    # Show final report
    shelldo.report()

