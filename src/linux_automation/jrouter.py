#!/bin/python3
"""
(Keboard Shortcut Router) Script to route commands coming from the linux keyboard shortcut manager
"""
import os
import argparse
import sys
import app_launcher
import music_classifier


parser = argparse.ArgumentParser()
parser.add_argument('--volume', type=int, help='set system audio volume with pactl utility')
parser.add_argument('--open', type=str, help='open or switch to an application')
parser.add_argument('--tier', type=str, help='run the music classifier script with this value')
parser.add_argument('--vibe', type=str, help='run the music classifier script with this value')
args = parser.parse_args()



# Set system volume
if args.volume or args.volume == 0:
    if 0 <= args.volume <= 100:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ {args.volume}%')
        print(f'pactl set-sink-volume @DEFAULT_SINK@ {args.volume}%')
    else:
        raise ValueError


# Open/Switch-to application
if args.open:
    app_launcher.open(args.open)
elif args.tier:
    music_classifier.set_tier(args.tier)
elif args.vibe:
    music_classifier.set_vibe(args.vibe)


