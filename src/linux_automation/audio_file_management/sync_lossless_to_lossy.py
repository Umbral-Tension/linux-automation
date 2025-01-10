#!/bin/python3
""" Script to make and update a lossy mirror of my lossless music collection. 

- Does not mirror deletions or file changes (eg tag edits) that occur in the lossless collection. 
- Does warn of files that only exist in the lossy mirror (perhaps because I mistakenly placed a newly acquired file into the lossy rather than lossless directory)
"""

import os, shutil
from os import path as opath
from os.path import join as pjoin
import subprocess, shlex
from jtools import jconsole

root_lossless = "/run/media/jeremy/internal_6TB/lossless_music/"
root_lossy = "/home/jeremy/jdata/audio/music/"

os.makedirs(root_lossy, exist_ok=True)
newarrivals = []
for dirpath, dirnames, filenames in os.walk(root_lossless):
    relpath = dirpath.replace(root_lossless, "")
    for x in filenames:
        name, ext = opath.splitext(x)
        isflac = ext.casefold() == ".flac"
        
        if isflac:
            lossypath = pjoin(root_lossy, relpath, f"{name}.mp3")
        else:
            lossypath = pjoin(root_lossy, relpath, x)

        # If mirror doesn't already have this file, then do...
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
            
            jconsole.erase_line_previous()
            newarrivals.append(f"{relpath}/{name}")


# Check for files that only exist in the lossy mirror
lossyuniques = []
for dirpath, dirnames, filenames in os.walk(root_lossy):
    lossydirpath = dirpath
    losslessdirpath = dirpath.replace(root_lossy, root_lossless)
    for x in [opath.splitext(j) for j in os.listdir(lossydirpath)]:
        try:
            losslessfiles = [opath.splitext(x)[0] for x in os.listdir(losslessdirpath)]
        except FileNotFoundError:
            lossyuniques.extend([opath.join(lossydirpath, t) for t in os.listdir(lossydirpath)])
            break
        if x[0] not in losslessfiles:
            lossyuniques.append(opath.join(lossydirpath, x[0] + x[1]))

print(f"Files synced from lossless to lossy:\n\t", end="")
if len(newarrivals) == 0:
    print(jconsole.red("up to date; nothing to sync"))
else:
    print(jconsole.green("\n\t".join(sorted(newarrivals))))
if len(lossyuniques) > 0:
    print(f"These files only exist in the lossy directory (investigate):\n\t", end="")
    print(jconsole.red("\n\t".join(sorted(lossyuniques))))
            


        
        



