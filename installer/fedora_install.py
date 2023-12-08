#!/bin/python3
"""Configure a fedora system."""

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
from subprocess import run
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
hostname = None

def bootstrap():
    """Prework to make jtools available for the rest of the script. """
    # get git, pip, and jtools
    print('---> Installing git, pip, and jtools')
    run(lex(f'sudo dnf install -y git'))
    run(lex(f'sudo dnf install -y pip'))
    run(lex(f'pip -q install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein'))
    if not opath.exists(f'{installerdir}/localjtools'):
        run(lex(f'git clone https://github.com/umbral-tension/python-jtools {installerdir}/localjtools'))
    print('---> success (git,pip,jtools)')


def collect_input():
    """collect some initial user input """
    global hostname
    hostname = input(jc.yellow('What should be the hostname for this machine?: '))
    return True


def install_repos():
    """install some repositories: rpm fusion free and non-free, vscode """
    fedora_version = run(lex('rpm -E %fedora'), capture_output=True, text=True).stdout.strip()
    outcome = shelldo.chain([
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm"',
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm"',
        'sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc',
        'sudo sh -c \'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo\'',
    ])
    return outcome


def freeworld_packages():
    """install some non-included codecs/drivers: ffmpeg-free, gstreamer, multimedia codecs, mesa drivers"""
    outcome = shelldo.chain([
        'sudo dnf -y swap ffmpeg-free ffmpeg --allowerasing',
        'sudo dnf -y groupupdate multimedia --setop="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin',
        'sudo dnf -y groupupdate sound-and-video',
        'sudo dnf -y swap mesa-va-drivers mesa-va-drivers-freeworld',
        'sudo dnf -y swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld',
    ])
    return outcome


def simple_installs():
    """simple package installs (gcc, tree, zenity, gnome-extensions-app, vscode, qbittorrent, chromium, GIMP, dconf-editor, xed, tldr)"""
    outcome = shelldo.chain([
        shelldo.inst_cmd('gcc'),
        shelldo.inst_cmd('tree'),
        shelldo.inst_cmd('zenity'),
        shelldo.inst_cmd('gnome-extensions-app'),
        shelldo.inst_cmd('code'),
        shelldo.inst_cmd('qbittorrent'),
        shelldo.inst_cmd('chromium'),
        shelldo.inst_cmd('gimp'),
        shelldo.inst_cmd('dconf-editor'),
        shelldo.inst_cmd('xed'),
        shelldo.inst_cmd('tldr'),
        shelldo.inst_cmd('vlc'),
        shelldo.inst_cmd('nemo'),
        ])
    return outcome


def miscellaneous():
    """miscellanea ()"""
    return True


def set_hostname():
    """set hostname"""
    outcome = False if hostname is None else shelldo.chain([f'hostnamectl set-hostname {hostname}'])
    return outcome
        

def configure_ssh():
    """generate ssh keys and configure sshd"""
    if not opath.exists(f'{home}/.ssh/id_ed25519'): 
        outcome = shelldo.chain([f'ssh-keygen -N "" -t ed25519 -f {home}/.ssh/id_ed25519'])
    else:
        outcome = True
    return outcome and shelldo.chain([f'sudo cp {appdir}/resources/configs/sshd_config /etc/ssh/sshd_config'])


def github_client():
    """install Github client and add ssh keys to github"""
    outcome = shelldo.chain([
        'sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo',
        'sudo dnf -y install gh'
    ])
    if outcome:
        # can't use chain because we need to interact with this command alot. 
        a = run(lex('gh auth login -p https -w -s admin:public_key')).returncode
        b = run(lex(f'gh ssh-key add {home}/.ssh/id_ed25519.pub --title "{hostname}"')).returncode
    return outcome and (a + b == 0)


def clone_repos():
    """clone my usual repos into ~/@data/git-repos/"""
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


# def input_device_ids():
#     """exhort user to get keyboard device id """
#     input(jc.yellow("Opening a terminal running keyd -m. Copy the device ids you want and paste them here in a comma seperated list.\n...press enter when ready"))
#     run(lex('gnome-terminal -- sudo keyd -m'))
#     device_ids = input(jc.yellow("device ids: "))
#     device_ids = device_ids.replace(',', '\n,').replace(' ','').split(',')
#     keyd_conf = f'{appdir}/resources/configs/my_keyd.conf'
#     temp_conf = f'{installerdir}/temp_keyd_conf'
#     with open(temp_conf, 'w') as tempfile, open(keyd_conf, 'r') as keydfile:
#         lines = ['[ids]\n'] + device_ids + keydfile.readlines()
#         tempfile.writelines(lines)
    
#     outcome = shelldo.chain([
#         f'sudo cp {temp_conf} /etc/keyd/default.conf',
#         'sudo systemctl restart keyd',
#     ])
#     os.remove(temp_conf)
#     return outcome


def bashrc():
    """source my bash aliases in .bashrc"""
    with open(f'{home}/.bashrc', 'a') as f:
        f.writelines([f'. "{git_repos}/linux-automation/resources/configs/bashrc fedora"\n'])
    return True


def jrouter():
    """place symlink to jrouter in ~/bin"""
    try:
        os.remove('/home/jeremy/bin/jrouter')
    except FileNotFoundError:
        pass
    os.makedirs('/home/jeremy/bin', exist_ok=True)
    os.symlink(f'{git_repos}/linux-automation/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')
    return True         


def dconf():
    """change some dconf settings (keybindings, app-switcher)"""
    outcome = os.system(f'dconf load -f /org/gnome/settings-daemon/plugins/media-keys/ < "{appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:settings-daemon:plugins:media-keys:"')
    #outcome2 = os.system(f'dconf load -f /org/gnome/desktop/wm/keybindings/ < "{appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:desktop:wm:keybindings:"')
    return True if outcome == 0 else False


def set_pythonpath():
    """append PYTHONPATH with jtools & linux-automation"""
    with open(f'{home}/.bash_profile', 'r+') as f:
        lines = f.readlines()
        pyexport = 'export PYTHONPATH=/home/jeremy/@data/git-repos/python-jtools/src:/home/jeremy/@data/git-repos/linux-automation/src/:"${PYTHONPATH}"\n'
        if pyexport not in lines:
            f.write(pyexport)
    return True

def remove_home_dirs():
    """remove unused home directories like ~/Templates ~/Music ..etc """
    dirs = ['Templates', 'Music', 'Pictures', 'Videos', 'Documents']
    for x in dirs:
        try:
            shutil.rmtree(f'{home}/{x}')
        except FileNotFoundError:
            pass
    return True

def gnome_terminal_themes():
    """install color themes for gnome-terminal"""
    # outcome1 = shelldo.chain([f'git clone https://github.com/Gogh-Co/Gogh.git {installerdir}/gogh'])
    # os.chdir(f'{installerdir}/gogh')
    # outcome2 = shelldo.chain([f'export TERMINAL=gnome-terminal'])
    # os.chdir('installs')
    

    # clone the repo into "$HOME/src/gogh"
    # mkdir -p "$HOME/src"
    # cd "$HOME/src"
    # cd gogh

    # # necessary in the Gnome terminal on ubuntu
    # export TERMINAL=gnome-terminal

    # # necessary in the Alacritty terminal
    # pip install -r requirements.txt
    # export TERMINAL=alacritty

    # # Enter theme installs dir
    # cd installs

    # 06 11 37 38 39 61 68 77 81 86 97 115 159 163 200 206
    # # install themes
    # ./afterglow.sh
    # ./aura.sh
    # ./chalk.sh
    # ./chameleon.sh
    # ./clone-of-ubuntu.sh
    # ./everblush.sh
    # ./flat.sh
    # ./gogh.sh
    # ./gotham.sh
    # ./gruvbox-dark.sh
    # ./horizon-dark.sh
    # ./lavandula.sh
    # ./one-half-black.sh
    # ./panda.sh
    # ./spacedust.sh
    # ./srcery.sh
    return False
def cleanup():
    """delete/uninstall unecessary remnants"""
    outcome = shelldo.chain([
        f'rm -rf {installerdir}/keyd',
        f'rm -rf {installerdir}/localjtools',
        shelldo.inst_cmd('gh', uninstall=True),
    ])
    return outcome

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

    # Master list of available tasks. 
    all_tasks = [collect_input, install_repos, freeworld_packages,
             simple_installs, miscellaneous, set_hostname, configure_ssh, github_client,
             clone_repos, keyd, bashrc, jrouter, dconf, set_pythonpath, gnome_terminal_themes, cleanup, ]
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
