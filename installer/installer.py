#!/bin/python3
""" Configure a fresh debian or redhat based linux installation with creature comforts"""

import os
import shutil
import sys
import os.path as opath
from shlex import split as lex
from subprocess import run
import traceback
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
        run(lex(install('python3-pyqt5 python3-ipython python3-pandas python3-mutagen python3-colorama python3-fuzzywuzzy python3-Levenshtein')))
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
        retcodes = run('wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null', shell=True).returncode
        retcodes += shelldo.chain(['sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg'])
        retcodes += run('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list', shell=True).returncode
        retcodes += shelldo.chain([       
            'sudo apt update',
            'sudo apt -y install gh',
        ])
    elif platform['pm'] == 'dnf':
        outcome = shelldo.chain([install('gh')])
    if outcome:
        # can't use chain because we need to interact with this command alot. 
        retcodes = run(lex('gh auth login -p https -w -s admin:public_key')).returncode
        retcodes += run(lex(f'gh ssh-key add {home}/.ssh/id_ed25519.pub --title "{hostname}"')).returncode
    return outcome and retcodes == 0


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
    outcome = outcome and shelldo.chain([
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
        print(traceback.format_exc())
        return False
    return True


def place_symlinks():
    """place symlinks in relevant locations for jrouter, .desktop files, and other scripts"""

    context_menu_scripts = opath.join(git_repos, "linux-automation/src/linux_automation/context_menu_scripts")
    local_share = opath.join(home, ".local/share")
    links = [
        # ~/bin
        (f'{git_repos}/linux-automation/src/linux_automation/jrouter.py',   f'{home}/bin/jrouter'),
        (f'{context_menu_scripts}/jtag_editor',                             f'{home}/bin/jtag_editor'),
        (f'{context_menu_scripts}/open_with_puddletag',                     f'{home}/bin/open_with_puddletag'),
        (f'{context_menu_scripts}/string_replace',                          f'{home}/bin/string_replace'),

        # nemo and nautilus context menu
        (f'{context_menu_scripts}/jtag_editor',                 f'{local_share}/nemo/scripts/jtag_editor'),
        (f'{context_menu_scripts}/open_with_puddletag',         f'{local_share}/nemo/scripts/open_with_puddletag'),
        (f'{context_menu_scripts}/string_replace',              f'{local_share}/nemo/scripts/string_replace'),
        (f'{context_menu_scripts}/jtag_editor',                 f'{local_share}/nautilus/scripts/jtag_editor'),
        (f'{context_menu_scripts}/open_with_puddletag',         f'{local_share}/nautilus/scripts/open_with_puddletag'),
        (f'{context_menu_scripts}/string_replace',              f'{local_share}/nautilus/scripts/string_replace'),
    ]
    #AppImages
    for dirpath, dirnames, filenames in os.walk(f"{home}/jdata/AppImages/"):
        for file in filenames:
            if file.casefold().endswith(".desktop"):
                program_name = opath.basename(dirpath)
                links.append((opath.join(dirpath, file), f"{local_share}/applications/{program_name}.desktop"))


    os.makedirs(f'{home}/bin', exist_ok=True)
    os.makedirs(f'{local_share}/nautilus/scripts', exist_ok=True)
    os.makedirs(f'{local_share}/nemo/scripts', exist_ok=True)
    os.makedirs(f'{local_share}/applications', exist_ok=True)
    try:
        os.remove(f'{home}/bin/jrouter')
    except FileNotFoundError:
        pass
    
    for l in links:
        try:
            os.remove(l[1]) # remove any prexisting links of the same name 
        except FileNotFoundError:
            pass
        try:
            os.symlink(l[0], l[1])
        except Exception:
            print(traceback.format_exc())
            return False
    return True         


def dconf():
    """change some dconf settings (keybindings, app-switcher)"""
    dconfdir = opath.join(appdir, "resources/configs/dconf", platform['name'])
    try:
        for x in os.scandir(opath.join(dconfdir, 'dirs')):
            run(f'dconf load -f {x.name.replace("_---", "/")} < "{x.path}"', shell=True)
        for x in os.listdir(opath.join(dconfdir, 'keys')):
            run(f'dconf load -f {x.name.replace("_---", "/")} < "{x.path}"', shell=True)
    except:
        print(traceback.format_exc())
        return False
    return True #if outcome == 0 else False


def remove_home_dirs():
    """remove unused home directories like ~/Templates ~/Music ..etc """
    dirs = ['Templates', 'Music', 'Pictures', 'Videos', 'Documents']
    for x in dirs:
        try:
            shutil.rmtree(f'{home}/{x}')
        except FileNotFoundError:
            pass
    return True


## fedora only jobs
def install_repos():
    """add some repositories: rpm fusion free and non-free """
    fedora_version = run(lex('rpm -E %fedora'), capture_output=True, text=True).stdout.strip()
    outcome = shelldo.chain([
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm"',
        f'sudo dnf -y install "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm"'])
    return outcome

def freeworld_packages():
    """install some non-included codecs/drivers: ffmpeg-free, gstreamer, multimedia codecs, mesa drivers"""
    outcome = shelldo.chain([
        'sudo dnf -y swap ffmpeg-free ffmpeg --allowerasing',
        'sudo dnf update @multimedia --setopt="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin',
        'sudo dnf -y swap mesa-va-drivers mesa-va-drivers-freeworld',
        'sudo dnf -y swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld',
    ])
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
    
    # while True:
    #     a = input('interactive mode? (y/n)')
    #     if a.casefold() == y:

    ### Bootstrap stuff to make jtools available
    if '--no-bootstrap' not in sys.argv:
        # bootstrap()
        # have to relaunch after bootstrap or the modules that were just installed aren't importable
        os.execl(sys.argv[0], sys.argv[0], '--no-bootstrap')
    

    #### Begin the rest of the installation
    sys.path.append(f'{installerdir}/localjtools/src/')
    from jtools import jconsole as jc
    from jtools.shelldo import Shelldo
    shelldo = Shelldo(installerdir)
    # Master list of available tasks (functions). 
    all_tasks = [collect_input, simple_installs, install_repos, freeworld_packages, 
                 set_hostname, configure_ssh, github_client, clone_repos,
                 keyd, bashrc, place_symlinks, dconf, remove_home_dirs, cleanup,
                 ]
    # print list of available tasks
    i = 0
    for x in all_tasks:
        print(f"{i}. {x.__name__}")
        i += 1
    exit()

        

    # Tasks to be performed on this run. The order of these is important and should be changed with care.
    tasks = all_tasks
    # Tasks to skip on this run. Order is not important. 
    skip_tasks = [install_repos, freeworld_packages]
    for t in tasks:
        if t not in skip_tasks:
            shelldo.set_action(t.__doc__)
            outcome = t()
            shelldo.log(outcome, shelldo.curraction)
            shelldo.set_result(outcome)
        
    
    # Show final report
    shelldo.report()

