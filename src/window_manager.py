import os
import json
import time
import subprocess
from jtools.jconsole import test

basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, '/home/jeremy/Desktop/git repos/linux-automation/resources/paths.json')) as fp:
    paths = json.load(fp)


def open(program_name, *args):
    """"
    Open a program/website or switch to it if it already exists. 
    
    @param program_name: one of the programs named in resources/paths.json
    """
    program_name = str.lower(program_name)
    try:
        path = paths[program_name][0]
        window_title = paths[program_name][1]
    except KeyError:
        path = ''
        window_title = ''

    # Activate the program window if it's already running
    if win_activate(window_title):
        return
    
    cmd = ''
    browser = paths['firefox'][0]
    # random subreddit opener
    if program_name in ['r', 'rnsfw', 'rsfw']:
        cmd = f'jtools_random_reddit.py {program_name[1:]}'
    # Simple website opening
    elif path.startswith('http'):
        os.system(f'{browser} {path}')
    else:
        cmd = path
    

    # program opening
    os.system(cmd)#+args)


def win_list():
    """
    Get info on all currently open windows
    """
    ls = []
    retCode, output = _run_wmctrl(["-lpx"])
    for line in output.split('\n'):
        info = line.split(maxsplit=5)
        ls.append({'window_id': info[0], 'desktop_num': info[1], 'pid': info[2], 'wm_class': info[3], 'title': info[5]})
    return ls

def win_exists(title):
    """
    Return True if window exists in the 1st workspace. 
    
    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    """
    if title == '':
        return False
    ls = win_list()
    for x in ls:
        if x['desktop_num'] != '0': # only consider windows on first workspace
            continue
        if title.startswith('wm_class_'):
            newtitle = title.replace('wm_class_', '').casefold()
            match = x['wm_class'].casefold() 
            if newtitle == match:
                return True
        else:
            if title.casefold() in x['title'].casefold():
                return True
    return False
    

def win_activate(title):
    """
    Activate the specified window. Returns True if window exists.

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    """
    if not win_exists(title): # this line stops matches from other workspaces from activating
        return False
    
    args = []
    if title.startswith('wm_class_'):
        title = title.replace('wm_class_', '')
        args += ["-x"]
    args += ['-a', title]
    _run_wmctrl(args)
    return True

def win_close(title):
    """
    Close the specified window gracefully

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    """
    if not win_exists(title): # this line stops matches from other workspaces from activating
        return
    
    args = []
    if title.startswith('wm_class_'):
        title = title.replace('wm_class_', '')
        args += ["-x"]
    args += ['-c', title]
    _run_wmctrl(args)


def _run_wmctrl(args):
    try:
        with subprocess.Popen(["wmctrl"] + args, stdout=subprocess.PIPE) as p:
            output = p.communicate()[0].decode()[:-1]  # Drop trailing newline
            returncode = p.returncode
    except FileNotFoundError:
        return 1, 'ERROR: Please install wmctrl'

    return returncode, output


