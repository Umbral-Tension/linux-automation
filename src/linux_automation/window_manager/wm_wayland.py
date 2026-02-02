"""" Module for manipulating windows in a Gnome+Wayland\
    environment.

Uses the Gnome extension "Window Calls (https://extensions.gnome.org/extension/4724/window-calls/)" as a backend to send dbus calls.\
Multiple monitors are not explicitly supported but might work anyway. Only\
operatoes on windows in the current workspace.  
"""

import os
import json
import ast
import subprocess
import shlex
from jtools.jconsole import test, ptest, zen
from time import sleep


# methods of the Gnome Extension "Window Calls"
methods = {x: ['--method', f'org.gnome.Shell.Extensions.Windows.{x}'] for x in 
           ['List', 'Details', 'GetTitle', 'Maximize', 'Minimize',
            'Resize', 'MoveResize', 'Move',
            'Unmaximize', 'Unminimize', 'Activate', 'Close',]}



basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, '../../../resources/paths.json')) as fp:
    paths = json.load(fp)


def win_list():
    """
    Get info on all currently open windows, returns a list of dictionaries
    """  
    winlist = _run_gdbus(methods["List"])[0] # extract json string, (first item in the tuple returned by gdbus call)
    winlist = json.loads(winlist)
    if winlist:        
        for x in range(len(winlist)):
            args = methods['GetTitle'] + [winlist[x]['id']]
            title = _run_gdbus(args)[0] # extract title, (first item in tuple returned by gdbus call)
            winlist[x]['title'] = title
    return winlist

def win_list_raw():
    """
    get raw json string output of gdbus List call 
    """
    gdbus = shlex.split("gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell/Extensions/Windows --method org.gnome.Shell.Extensions.Windows.List")
    gdbuscall = subprocess.run(gdbus, text=True, capture_output=True)
    return ast.literal_eval(gdbuscall.stdout)[0]


def win_exists(title):
    """
    Return True if window exists in the 1st workspace. 
    
    @param title: window title to match against (as case-insensitive substring
    match). For case-insensitive exact match based on "window manager class"
    prepend title with "wm_class_"
    """
    if win_id(title):
        return True
    else:
        return False
    
def win_id(title):
    """return the id of the window with this title if it exists, else None

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    """
    # '' would otherwise match paths.json entries that have no value for the 
    # title key, which is not desirable. 
    if title == '': 
        return None
    ls = win_list()
    for x in ls:
        if not x['in_current_workspace']: # only consider windows on first workspace
            continue
        if title.startswith('wm_class_'):
            newtitle = title.replace('wm_class_', '').casefold()
            match = str(x['wm_class']).casefold() 
            if newtitle == match:
                return str(x['id'])
        else:
            if title.casefold() in x['title'].casefold():
                return str(x['id'])
    return None

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
    Activate the specified window.

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    """
    id_ = win_id(title)
    if id_ is None:
        return
    args = methods['Activate'] + [id_]
    _run_gdbus(args)

def win_close(title):
    """
    Close the specified window gracefully

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    """
    id_ = win_id(title)
    if id_ is None:
        return
    args = methods['Close'] + [id_]
    _run_gdbus(args)

def get_gemoetry():
    """
    return a tuple like (0,0,0,0)  that contains the desktop width/height and the "working area" width/height. 
    """
    #TODO x,y values being repoted by gdbus do not seem very reliable. 
    #Fullscreen apps report coords of (-2,-2), (-40,-40)...etc 
    pass
    
def win_snap(title, position: str):
    """
    Move and resize a window so that it occupies one of the screen's corners, sides, top, or bottom. 
    
    Limitation: will not work on maximized windows or windows that has been manually snapped already. 

    @param title: window title to match against (as case-insensitive substring match). 
    For case-insensitive exact match based on "window manager class" prepend title with "wm_class_"
    @param position: one of [N, S, E, W, NW, NE, SW, SE]
    """
    # position = position.casefold()
    # geom = get_gemoetry()
    # w, h = geom[2], geom[3]
    
    # # represents the <MVARG> argument in wmctrl given by "gravity,x,y,width,height".
    # mvarg = [0]
    # presets = {'w': [0, 0, w/2, h], 'e': [w/2, 0, w/2, h], 'n': [0, 0, w, h/2], 's': [0, h/2, w, h/2],
    #  'nw': [0, 0, w/2, h/2], 'ne': [w/2, 0, w/2, h/2], 'sw': [0, h/2, w/2, h/2], 'se': [w/2, h/2, w/2, h/2]}
    
    # mvarg.extend(presets[position])
    # mvarg = [int(x) for x in mvarg]
    # mvarg = [str(x) for x in mvarg]
    # mvarg = ','.join(mvarg)
    # args = []
    # if title.startswith('wm_class_'):
    #     title = title.replace('wm_class_', '')
    #     args += ["-x"]
    # args += ['-r', title, '-e', mvarg]
    # _run_gdbus(args)
    pass
    


def _run_gdbus(args):
    """ use gdbus to call a specific method of the Window Calls extension and return a tuple of its output"""
    # base gdbus call to the "Windows Calls" extension. Split into a list for the Popen function. 
    gdbus = shlex.split("gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell/Extensions/Windows")
    args = [str(x) for x in args]
    gdbus = gdbus + args
    gdbuscall = subprocess.run(gdbus, text=True, capture_output=True)
    # python json module fails to parse gdbus output when a window with an apostrophe in its title exists, and perhaps there are other triggers too. 
    # found this workaround at the Window Calls github issues: https://github.com/ickyicky/window-calls/issues/38#issuecomment-3659560491
    # First use the ast module to evaluate the gdbus output string into a python object. It evals to a tuple continaing a string. 
    # That string is then parasable by the json module. 
    return ast.literal_eval(gdbuscall.stdout)


if __name__ == '__main__':


    print(win_list_raw())

