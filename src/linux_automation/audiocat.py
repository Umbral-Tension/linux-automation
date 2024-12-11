#!/bin/python3
import subprocess
import shlex
import os
from os import path as opath
from jtools.jconsole import test, ptest, zen
import sys
from jtools.jconsole import test, ptest
"""
concatenate audiobook files into one large file. Rename the result based on directory structure. 

"""

pwd = os.getcwd()
print(pwd)

cmd = "ffmpeg -f concat -safe 0 -i <(printf \"file '$PWD/%s'\n\" ./*.mp3) -c copy output.mp3"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        target = sys.argv[1]

    # generate file lists
    filelist = sorted([x for x in os.listdir(target) if x.casefold().endswith('mp3')])
    ffmpeglist = ["file '" + x + "'" for x in filelist]
    ffmpeglistfile = opath.abspath(opath.join(target, 'filelist.txt'))
    with open(ffmpeglistfile, 'w') as f:
        f.writelines('\n'.join(ffmpeglist))

    # extract cover art from 1st file in list
    coverfile = opath.abspath(opath.join(target, "cover.jpg"))
    subprocess.Popen(shlex.split(f"ffmpeg -hide_banner -i '{opath.join(target, filelist[0])}' -an -vcodec copy '{coverfile}'"))

    # concatenate audio files
    outfile = opath.abspath(opath.join(target, 'output.mp3'))
    cmd = f"ffmpeg -hide_banner -f concat -safe 0 -i '{ffmpeglistfile}' -c copy '{outfile}'"
    # subprocess.Popen(shlex.split(cmd))
    os.system(cmd)
    
    # use mutagen to transfer tags
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC
    mutold = EasyID3(opath.abspath(opath.join(target, filelist[0])))
    mutnew = EasyID3(outfile)
    mutnew['artist'] = mutold['artist']
    mutnew['album'] = mutold['album']
    mutnew['title'] = mutold['title']
    mutnew['tracknumber'] = mutold['tracknumber']
    mutnew.save()

    # use ID3 for album art transfer. From: https://stackoverflow.com/a/44573629
    mutnew = ID3(outfile)
    with open(coverfile, 'rb') as albumart:
        mutnew['APIC'] = APIC(
                          encoding=3,
                          mime='image/jpeg',
                          type=3, desc=u'Cover',
                          data=albumart.read()
                        )            
    mutnew.save()



    # cleanup
    newfilename = filelist[0]
    for x in range(len(filelist)):
        if filelist[x] == 'output.mp3':
            continue
        os.remove(opath.abspath(opath.join(target, filelist[x])))
    os.remove(ffmpeglistfile)
    os.rename(outfile, opath.abspath(opath.join(target, newfilename)))
    

