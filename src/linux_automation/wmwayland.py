"""" Module for manipulating windows and launching programs in a Gnome+Wayland\
    environment.

Uses the Gnome extension "Window Calls" as a backend to send dbus calls.\
Multiple monitors are not explicitly supported but might work anyway. Only\
operatoes on windows in the current workspace.  
"""

import os
import json
import time
import subprocess
import shlex
from jtools.jconsole import test, zen
from time import sleep


# methods of the Gnome Extension "Window Calls"
methods = {x: ['--method', f'org.gnome.Shell.Extensions.Windows.{x}'] for x in 
           ['List', 'Details', 'GetTitle', 'Maximize', 'Minimize',
            'Resize', 'MoveResize', 'Move',
            'Unmaximize', 'Unminimize', 'Activate', 'Close',]}

basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, '../../resources/paths.json')) as fp:
    paths = json.load(fp)

def open(name, *args):
    """"
    Open a program/website or switch to it if it already exists. 

    @param name: one of the programs or websites named in resources/paths.json
    """
    name = name.casefold()
    try:
        exec_cmd = paths[name]['exec_cmd']
        window_title = paths[name]['window_title']
    except KeyError:
        os.system(f'zenity --warning --text="{name} not found in the file paths.json" --title="window_manager.py"')
        return

    # Activate the program window if it's already running
    if win_activate(window_title):
        return

    # Single website opening
    if exec_cmd.casefold().startswith('http'):
        browser = paths['firefox']['exec_cmd']
        exec_cmd = f'{browser} {exec_cmd}'
    
    os.system(exec_cmd + ' &')

def win_list():
    """
    Get info on all currently open windows
    """
    ls = []
    output = _run_wmctrl(methods['List'])
    if output:        
        output = output[2:-3]
        import json
        a = json.loads(output)
        test(a)
    return ls

def win_exists(title):
    """
    Return True if window exists in the 1st workspace. 
    
    @param title: window title to match against (as case-insensitive substring\
        match). For case-insensitive exact match based on \
        "window manager class" prepend title with "wm_class_"
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
    
def win_wait(title, refresh_rate=0.1):
    """
    Wait until the specified window exists. 

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    @param refresh_rate number of seconds between calls to win_exists and thus "wmctrl -l". Default is 0.1
    """    
    while not win_exists(title):
        sleep(refresh_rate)

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

def get_gemoetry():
    """
    return a tuple like (0,0,0,0)  that contains the desktop width/height and the "working area" width/height. 
    """
    out = _run_wmctrl(['-d']).split()
    desktop = out[3].split('x')
    wa = out[8].split('x')
    tup = [int(x) for x in desktop + wa]
    return tup
    

def win_snap(title, position: str):
    """
    Move and resize a window so that it occupies one of the screen's corners, sides, top, or bottom. 
    
    Limitation: will not work on maximized windows or windows that has been manually snapped already. 

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    @param position: one of [N, S, E, W, NW, NE, SW, SE]
    """
    position = position.casefold()
    geom = get_gemoetry()
    w, h = geom[2], geom[3]
    
    # represents the <MVARG> argument in wmctrl given by "gravity,x,y,width,height".
    mvarg = [0]
    presets = {'w': [0, 0, w/2, h], 'e': [w/2, 0, w/2, h], 'n': [0, 0, w, h/2], 's': [0, h/2, w, h/2],
     'nw': [0, 0, w/2, h/2], 'ne': [w/2, 0, w/2, h/2], 'sw': [0, h/2, w/2, h/2], 'se': [w/2, h/2, w/2, h/2]}
    
    mvarg.extend(presets[position])
    mvarg = [int(x) for x in mvarg]
    mvarg = [str(x) for x in mvarg]
    mvarg = ','.join(mvarg)
    args = []
    if title.startswith('wm_class_'):
        title = title.replace('wm_class_', '')
        args += ["-x"]
    args += ['-r', title, '-e', mvarg]
    _run_wmctrl(args)
    

# base gdbus call to the "Windows Calls" extension. Split into a list for the Popen function. 
gdbus = shlex.split('gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell/Extensions/Windows')
def _run_wmctrl(args):
    try:
        with subprocess.Popen(gdbus + args, stdout=subprocess.PIPE) as p:
            output = p.communicate()[0].decode()[:-1]  # Drop trailing newline
    except FileNotFoundError:
        return 1, 'ERROR: gdbus not available'

    return output


if __name__ == '__main__':

    # while True:
    #     for x in ['n', 's', 'e', 'w', 'nw', 'ne', 'sw', 'se']:
    #         win_snap('jdesk', x)
    #         from time import sleep
    #         sleep(2)
    
    
    win_list()

