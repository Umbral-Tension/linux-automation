#!/bin/python3
""" Script to make and update a lossy mirror of my lossless music collection. Does not mirror deletions or file changes (eg tag edits) that occur in the lossless collection. """

import os, shutil
from os import path as opath
from os.path import join as pjoin
import subprocess, shlex
from jtools.jconsole import test, ptest

root_lossless = "/run/media/jeremy/internal_6TB/lossless_music/"
root_lossy = "/home/jeremy/jdata/audio/music/"

os.makedirs(root_lossy, exist_ok=True)

for dirpath, dirnames, filenames in os.walk(root_lossless):
    for x in filenames:
        name, ext = opath.splitext(x)
        relpath = dirpath.replace(root_lossless, "")
        isflac = ext.casefold() == ".flac"
        
        if isflac:
            lossypath = pjoin(root_lossy, relpath, f"{name}.mp3")
        else:
            lossypath = pjoin(root_lossy, relpath, x)

        # If mirror doesn't already have this file
        if not opath.exists(lossypath):
            os.makedirs(pjoin(root_lossy, relpath), exist_ok=True)
            if isflac:
                #convert to mp3 and copy it                
                print(f"converting and copying: {pjoin(dirpath, x)}")
                ffmpeg = shlex.split(f"ffmpeg -hide_banner -i \"{pjoin(dirpath,x)}\" -ab 320k \"{lossypath}\"")
                proc = subprocess.run(ffmpeg, capture_output=True, text=True)
                if proc.returncode != 0:
                    with open("/home/jeremy/jdata/logs/sync_lossless_to_lossy", 'a') as f:
                        from datetime import datetime
                        f.writelines("\n".join([
                            str(datetime.now()),
                            f"--->: ffmpeg -hide_banner -i \"{pjoin(dirpath,x)}\" -ab 320k \"{lossypath}\"",
                            proc.stdout,
                            proc.stderr,
                            "\n\n"]))

            else:
                #just copy it to mirror
                print(f"copying: {pjoin(dirpath, x)}")
                shutil.copy(pjoin(dirpath, x), lossypath)


        
        



