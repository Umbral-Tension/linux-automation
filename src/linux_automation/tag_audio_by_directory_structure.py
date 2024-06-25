"""  !!!Fragile Script
batch tags/renames mp3 files based on info gathered from the directory structure they exist within.
Mostly to be used on freshly segmented comedy specials. 

Requirements: 
    - mp3 files must already exist in an Artist/Album/files structure 
    - first 2 characters of the filenames must be the track number like "02.Marc.Maron.Think.Pain.mp3"
    - only works on MP3
"""

from jtools.jconsole import test, ptest, zen, yes_no
import os
from os import path as opath
from mutagen.easyid3 import EasyID3



def tag_by_directory_structure():
    top_level_dir = "/home/jeremy/jdata/downloads/newaudio/"

    rename_files = yes_no('Should files be renamed in addition to being tagged? The following template will be used: {{ track. artist - album.mp3 }}')
    renames = []


    for artist in os.scandir(top_level_dir):
        for album in os.scandir(artist):
            for x in os.scandir(album):
                if not str.casefold(x.name).endswith('.mp3'):
                    continue
                
                track = x.name[:2].strip()
                if len(track) == 1:
                    track = '0' + track
                title = f'{track}. {artist.name} - {album.name}'

                
                
                mut = EasyID3(x.path)
                mut['tracknumber'] = track
                mut['artist'] = artist.name
                mut['album'] = album.name
                mut['title'] = title
                mut.save()

                if rename_files:
                    src = x.path
                    dest = f'{opath.dirname(x)}/{title}.mp3'
                    renames.append([src,dest])
    
    #do renames outside of loops to avoid making a mess of the iterators
    for x in renames:
        os.rename(x[0], x[1])



if __name__ == '__main__':
    import traceback
    try:
        tag_by_directory_structure()
    except Exception as e:
        print(traceback.format_exc())
        input()

