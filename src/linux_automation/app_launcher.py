

import os
import json
import subprocess
from shlex import split as lex
from jtools.jconsole import test, ptest

display_server = os.environ['XDG_SESSION_TYPE'].casefold() # wayland or x11
if display_server == 'wayland':
    import window_manager.wm_wayland as wm
else:
    import window_manager.wm_xorg as wm


basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, '../../resources/paths.json')) as fp:
    paths = json.load(fp)


def open(name, options=None):
    """"
    Open a program/website or switch to it if it already exists. 

    @param name: one of the programs or websites named in resources/paths.json
    @param options: a list of strings that are options to be passed to the
    program indicated by the name paramter. This list is passed through to subprocess.Popen()
    For example: ['--no-recurse', '--level', '20', '-i', '--name', 'jeremy']
    """

    if options is None:
        options = []
    
    name = name.casefold()
    # Activate the program window if it's already running
    try:
        if display_server == 'wayland':
            window_title = paths[name]['wayland_window_title']
        else:
            window_title = paths[name]['window_title']
        
        if wm.win_exists(window_title):
            wm.win_activate(window_title)
            return
    except KeyError:
        subprocess.run(lex(f'zenity --warning --text="{name} was not found in the file paths.json" --title="window_manager.py"'))
        return

    # build and run an execution command to launch the program indicated by
    # name with args as its options
    exec_cmd = paths[name]['exec_cmd']
    # Single website opening
    if exec_cmd.casefold().startswith('http'):
        browser = paths['firefox']['exec_cmd']
        exec_cmd = lex(f'{browser} {exec_cmd}')
    else:
        exec_cmd = lex(exec_cmd)
        exec_cmd.extend(options)
        
    subprocess.Popen(exec_cmd, text=True, )


