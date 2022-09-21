import os, shutil
import os.path as opath
from os.path import join
from posixpath import abspath
from jtools.jconsole import test, ptest
from datetime import datetime
#TODO 
# 1. add /src to PATH  in ~/.profile  ||  put links to python files in ~/.local/bin
# 2. do dconf load to set up settings and keybindings
# 4. install desired programs
# 6. configure git, samba, keyd, bashrc, ssh, ufw firewall, pythonpath
#

def yesno(message ):
    while(True):
        response = input(f'{message}? (y/n)')
        if response.casefold() == 'y':
            return True
        if response.casefold() == 'n':
            return False

def exit_(message):
    print(message)
    exit()



# paths
home = os.environ['HOME']
git_repos = join(home, 'Desktop/git-repos')
appdir = abspath('.')
appname = opath.basename(appdir)
desired_install_location = '/home/jeremy/Desktop/LINUXAUTOMATION' #join(git_repos, appname)
install_log = join(appdir, 'installation-log.txt')

# current step in the installatino process
currstep = ''

def step(description, print_now=True):
    """update and print the current installation step."""
    global currstep
    currstep = description
    if print_now:
        print(f'--- {currstep}')

def log(result, action=None):
    if action is None:
        action = currstep
    """Add log the result of action. Default action is the currstep."""
    with open(install_log, 'a') as log:
        log.writelines('\n'.join([str(datetime.now()), '\t'+action, '\t'+result, '\n']))

#TODO remove this in production
with open(install_log, 'a') as logfile:
    logfile.writelines('\n'.join(['####BEGIN INSTALL#####   '+ str(datetime.now()), '']))

# ####TODO uncomment this warning when finished. 
# if not yesno(f'This script will overwrite and replace the following directory if it allready exists:\n{desired_install_location}\nDo you want to continue'):
#     print('process cancelled')
#     exit

# if the app isn't installed in the correct location, install it there. 
if not opath.exists(desired_install_location):
    os.mkdir(desired_install_location)
if not opath.samefile(appdir, desired_install_location):
    step(f'Copying app files to {desired_install_location}')
    try:
        shutil.rmtree(desired_install_location)
        shutil.copytree(appdir, desired_install_location, dirs_exist_ok=True)
    except Exception as e:
        #TODO print error message from exception object better
        print(e)
        log('fail')
        exit_('failed to install app files in correct location. Exiting.')
    log('ok')
    appdir = desired_install_location

# paths
bin = join(appdir, 'bin')
src = join(appdir, 'src')
resources = join(appdir, 'resources')
# path tests
for x in [home, git_repos, bin]:
    if not opath.exists(x):
        print(f'failed to find/create directory: {x}')



