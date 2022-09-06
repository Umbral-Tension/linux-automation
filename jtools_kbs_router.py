#!/bin/python3
"""
(Keboard Shortcut Router) Script to route commands coming from the linux keyboard shortcut manager
"""
import os
import argparse
import sys



parser = argparse.ArgumentParser()
parser.add_argument('--volume', type=int, help='set system audio volume with pactl utility')
parser.add_argument('--open', type=str, help='open or switch to an application')
args = parser.parse_args()



# Set system volume
if args.volume:
    if 0 <= args.volume <= 100:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ {args.volume}%')
    else:
        raise ValueError


# Open/Switch-to application
if args.open:
    os.system(args.open)
    
if len(sys.argv) < 2:
    os.system('gnome-calculator')

