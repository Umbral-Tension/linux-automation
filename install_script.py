import os, shutil
import os.path as opath
from os.path import join
from posixpath import abspath
from jtools.jconsole import test
#TODO 
# 1. add /src to PATH  in ~/.profile  ||  put links to python files in ~/.local/bin
# 2. do dconf load to set up settings and keybindings
# 4. install desired programs
# 6. configure git, samba, keyd, bashrc, ssh, ufw firewall, pythonpath
#

log = {}
def yesno(message ):
    while(True):
        response = input(f'{message}? (y/n)')
        if response.casefold() == 'y':
            return True
        if response.casefold() == 'n':
            return False
def exit_(message):
    print(message)
    exit


# paths
home = os.environ['HOME']
git_repos = join(home, 'Desktop/git-repos')
appdir = abspath('.')
appname = opath.basename(appdir)
desired_install_location = join(git_repos, appname)

# ####TODO uncomment this warning when finished. 
# if not yesno(f'This script will overwrite and replace the following directory if it allready exists:\n{desired_install_location}\nDo you want to continue'):
#     print('process cancelled')
#     exit

# if the app isn't installed in the correct location, install it there. 
if not opath.samefile(appdir, desired_install_location):
    print(f'--- Copying app files to {desired_install_location}')
    try:
        shutil.copytree(appdir, desired_install_location)
    except e:
        #TODO print error message from exception object
        exit_('failed to install app files in correct location. Exitting')
    appdir = desired_install_location


bin = join(appdir, 'bin')
src = join(appdir, 'src')
resources = join(appdir, 'resources')




# path tests
for x in [home, git_repos, bin]:
    if not opath.exists(x):
        print(f'failed to find/create directory: {x}')

def edit_profile():
    try:
        with open('/home/jeremy/profile'):
            pass
    except FileNotFoundError:
        pass


