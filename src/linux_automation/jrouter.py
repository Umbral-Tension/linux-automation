#!/bin/python3
"""
Script that acts as an ingress point to the "linux-automation" project. It launches programs and performs various other tasks. 
It is intended to be run primarily via an OS's builtin keyboard shortcut manager and less commonly via manual command line. 
"""
import os 
import os.path as opath
import argparse
import sys
import audio_file_management.music_classifier
import json
import subprocess
from shlex import split as lex
from jtools.jconsole import test, ptest
import jtools.jconsole as jc

parser = argparse.ArgumentParser(prog='jrouter', description=__doc__)
parser.add_argument('--interactive', '-i', action='store_true', help='start ipython jrouter and window_manager.py functions available i.e launch() and  wm.win_list() [This is for debugging or getting window IDs]')
parser.add_argument('--volume', type=int, help='set system audio volume with pactl utility')
parser.add_argument('--open', type=str, nargs='*', help='open or switch to an application')
parser.add_argument('--tier', type=str, help='run the music classifier script with this value')
parser.add_argument('--vibe', type=str, help='run the music classifier script with this value')
args = parser.parse_args()


display_server = os.environ['XDG_SESSION_TYPE'].casefold() # wayland or x11
if display_server == 'wayland':
    import window_manager.wm_wayland as wm
else:
    import window_manager.wm_xorg as wm

with open("/home/jeremy/jdata/git-repos/linux-automation/resources/paths.json") as fp:
    paths = json.load(fp)


def launch(name, options=None):
    """"
    Open a program/website or switch to it if it already exists. 

    @param name: one of the programs or websites named in resources/paths.json
    @param options: a list of strings that are options to be passed to the
    program indicated by the name paramter. This list is passed through to subprocess.Popen()
    For example: ['--no-recurse', '--level', '20', '-i', '--name', 'jeremy']
    """

    name = name.casefold()
    # Activate the program window if it's already running
    try:
        if display_server == 'wayland':
            window_title = paths[name]['wayland_window_title']
        else:
            window_title = paths[name]['window_title']
        
        if wm.win_exists(window_title):
            print(f'jrouter: activating window: {window_title}')
            wm.win_activate(window_title)
            return
    except KeyError:
        subprocess.run(lex(f'zenity --warning --text="{name} was not found in the file paths.json" --title="window_manager.py"'))
        return

    # build and run a command to launch the program or website indicated by <name> with <args> as its options
    exec_cmd = paths[name]['exec_cmd']
    # if name is website, just open it in firefox
    if exec_cmd.casefold().startswith('http'):
        browser = paths['firefox']['exec_cmd']
        exec_cmd = lex(f'{browser} {exec_cmd}')
    else:
        exec_cmd = lex(exec_cmd)
        if options:
            exec_cmd.extend(options)
    print(f"jrouter: running command: {'--> ' + ' '.join(exec_cmd)}")
    subprocess.Popen(exec_cmd, text=True, )



# Argument handling
# set system volume
if args.volume is not None:
    if 0 <= args.volume <= 100:
        os.system(f'amixer set Master {args.volume}%')
    else:
        raise ValueError
elif args.open:
    launch(args.open[0], args.open[1:])
elif args.tier:
    music_classifier.set_tier(args.tier)
elif args.vibe:
    music_classifier.set_vibe(args.vibe)
elif args.interactive:
    print(jc.red(jc.bold('Entering interactive jrouter session. jrouter.py functions like launch() and window_manager functions like wm.win_list() are available.\njtools.jconsole available as jc')))
    cmd = f"{paths['terminal']['exec_cmd']} -- ipython3 -i /home/jeremy/jdata/git-repos/linux-automation/src/linux_automation/jrouter.py"
    subprocess.Popen(lex(cmd))




if __name__ == '__main__':
    pass
