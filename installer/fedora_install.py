#!/bin/python3
"""Configure a fedora system."""

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
from subprocess import Popen, PIPE, run
import traceback
from datetime import datetime

print('\n/////////////////////////////////////////////////')
print('////////   linux-automation installer  //////////\n')

# relevant paths
home = os.environ['HOME']
git_repos = opath.join(home, '@data/git-repos')
os.makedirs(git_repos, exist_ok=True)
installerdir = opath.dirname(opath.realpath(__file__))
appdir = opath.dirname(installerdir)
appname = opath.basename(appdir)
hostname = ''

def bootstrap():
    """ Bootstrap prework to make jtools available for the rest of the script. """
    # get git, pip, and jtools
    print('---> Installing git, pip, and jtools')
    run(lex(f'sudo dnf install -y git'))
    run(lex(f'sudo dnf install -y pip'))
    run(lex(f'pip -q install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein'))
    if not opath.exists(f'{installerdir}/localjtools'):
        run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))
    print('---> success (git,pip,jtools)')


def collect_input():
    """collect user input """
    shelldo.set_action('collect initial user input')
    global hostname
    hostname = input(jc.yellow('What should be the hostname for this machine?: '))
    shelldo.log(True, shelldo.curraction)
    shelldo.set_result(True)

def install_repos():
    """install non-included repositories"""
    shelldo.set_action('install some repositories: rpm fusion free and non-free, ')
    fedora_version = run(lex('rpm -E %fedora'), capture_output=True, text=True).stdout.strip()
    outcome = shelldo.chain([
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm"',
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm"',
    ])
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def freeworld_packages():
    """install non-free multimedia packages per https://rpmfusion.org/Howto/Multimedia """
    shelldo.set_action('install some multimedia codecs/drivers: ffmpeg-free, gstreamer, multimedia codecs, mesa drivers')
    outcome = shelldo.chain([
        'sudo dnf -y swap ffmpeg-free ffmpeg --allowerasing',
        'sudo dnf -y groupupdate multimedia --setop="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin',
        'sudo dnf -y groupupdate sound-and-video',
        'sudo dnf -y swap mesa-va-drivers mesa-va-drivers-freeworld',
        'sudo dnf -y swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld',
    ])
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def simple_installs():
    """simple installs"""
    shelldo.set_action('simple installs')
    outcome = shelldo.chain([shelldo.inst_cmd('gcc')])
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def miscellaneous():
    shelldo.set_action('miscellanea: hostname')
    outcome = shelldo.chain([f'hostnamectl set-hostname {hostname}'])
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def configure_ssh():
    """make ssh keys and configure sshd"""
    shelldo.set_action('generate SSH keys and configure sshd')
    if not opath.exists(f'{home}/.ssh/id_ed25519'): 
        outcome = shelldo.chain([f'ssh-keygen -N "" -t ed25519 -f {home}/.ssh/id_ed25519'])
    else:
        outcome = True
    outcome = outcome and shelldo.chain([f'sudo cp {appdir}/resources/configs/sshd_config /etc/ssh/sshd_config'])
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def github_client():
    """install Github client and add ssh keys to github"""
    shelldo.set_action('install github cli and add ssh to github')
    outcome = shelldo.chain([
        'sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo',
        'sudo dnf -y install gh'
    ])
    if outcome:
        # can't use chain because we need to interact with this command alot. 
        a = run(lex('gh auth login -p https -w -s admin:public_key')).returncode
        b = run(lex(f'gh ssh-key add {home}/.ssh/id_ed25519.pub --title "{hostname}"')).returncode
    outcome = outcome and (a + b == 0)
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def clone_repos():
    """clone my usual repos into ~/@data/git-repos/"""
    shelldo.set_action('clone my repos from github')
    repos = ['python-jtools', 'linux-automation', 'Croon', 'old-code-archive',
            'experiments', 'project-euler', 'misc-db-files']
    clone_cmds = [f'git clone git@github.com:umbral-tension/{x} {git_repos}/{x}' for x in repos]
    outcome = shelldo.chain(clone_cmds, ignore_exit_code=True)
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


def keyd():
    """install and configure keyd"""
    shelldo.set_action('download and install keyd')
    shelldo.chain([f'git clone https://github.com/rvaiya/keyd {installerdir}/keyd'])
    os.chdir(f'{installerdir}/keyd')
    outcome = shelldo.chain([
        'make',
        'sudo make install',
        'sudo systemctl enable keyd',
        'sudo systemctl restart keyd',
        ])
    os.chdir(installerdir)
    _input_device_ids()


def _input_device_ids():
    """exhort user to get keyboard device id """
    input(jc.yellow("Opening a terminal running keyd -m. Copy the device ids you want and paste them here in a comma seperated list.\n...press enter when ready"))
    run(lex('gnome-terminal -- sudo keyd -m'))
    device_ids = input(jc.yellow("device ids: "))
    device_ids = device_ids.replace(',', '\n,').replace(' ','').split(',')
    keyd_conf = f'{appdir}/resources/configs/my_keyd.conf'
    temp_conf = f'{installerdir}/temp_keyd_conf'
    with open(temp_conf, 'w') as tempfile, open(keyd_conf, 'r') as keydfile:
        lines = ['[ids]\n'] + device_ids + keydfile.readlines()
        tempfile.writelines(lines)
    
    outcome = shelldo.chain([
        f'sudo cp {temp_conf} /etc/keyd/default.conf',
        'sudo systemctl restart keyd',
    ])
    os.remove(temp_conf)
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)

def bashrc():
    """source my bash aliases in .bashrc"""
    shelldo.set_action('bashrc')
    with open(f'{home}/.bashrc', 'a') as f:
        f.writelines([f'. "{appdir}/resources/configs/bashrc fedora"\n'])
    shelldo.log(True, shelldo.curraction)
    shelldo.set_result(True)

def jrouter():
    """place symlink to jrouter in ~/bin"""
    shelldo.set_action('jrouter')
    try:
        os.remove('/home/jeremy/bin/jrouter')
    except FileNotFoundError:
        pass
    os.makedirs('/home/jeremy/bin', exist_ok=True)
    os.symlink(f'{appdir}/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')         
    shelldo.log(True, shelldo.curraction)
    shelldo.set_result(True)

def dconf():
    """use dconf to load my keybindings and settings"""
    shelldo.set_action('dconf')
    os.system(f'dconf load -f /org/gnome/settings-daemon/plugins/media-keys/ < "{appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:settings-daemon:plugins:media-keys:"')
    shelldo.log(True, shelldo.curraction)
    shelldo.set_result(True)


def cleanup():
    #### cleanup
    shelldo.set_action('cleanup')
    outcome = shelldo.chain([
        f'rm -rf {installerdir}/keyd',
        f'rm -rf {installerdir}/localjtools',
        #shelldo.inst_cmd('gh', uninstall=True),
    ])
    shelldo.log(outcome, shelldo.curraction)
    shelldo.set_result(outcome)


if __name__ == '__main__':
    
    ### Bootstrap stuff to make jtools available
    if '--no-bootstrap' not in sys.argv:
        bootstrap()
        # have to relaunch after bootstrap or the modules that were just installed aren't importable
        os.execl(sys.argv[0], sys.argv[0], '--no-bootstrap')


    #### Begin the rest of the installation
    sys.path.append(f'{installerdir}/localjtools/src/')
    from jtools import jconsole as jc
    from jtools.shelldo import Shelldo
    shelldo = Shelldo()

    # The order of these is important and should be changed with care.
    tasks = [collect_input, install_repos, freeworld_packages,
             simple_installs, miscellaneous, configure_ssh, github_client,
             clone_repos, keyd, bashrc, jrouter, dconf, cleanup]
    skip_tasks = [keyd, github_client]
    for t in tasks:
        if t not in skip_tasks:
            t()


    # Show final report
    shelldo.report()