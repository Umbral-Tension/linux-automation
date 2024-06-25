""" !!!! FRAGILE SCRIPT

Breaks a bunch of long video or audio files into short mp3 audio segments. For use on 
downloaded stand up comedy specials or possibly audiobooks. 

Requirements:
- the video files are in a directory structure like: top_level_dir/Artist/Album/video_file. 
The script creates a mirror of that input directory structure in a directory called "audio_out" that 
sits in the parent directory of "top_level_dir" i.e. "top_level_dir/../audio_out/"

- each album directory must contain a single media file, the one that needs to be split into segments. 

"""

from jtools.jconsole import test, ptest, zen
import os
from os import path as opath
import subprocess
import shlex


def split_video_to_audio():
    top_level_dir = "/media/jeremy/internal_6TB/torrents/standup"


    for comic in os.scandir(top_level_dir):
        print(comic.name)
        for album in os.scandir(comic):
            # skip if there's more than 1 video file in an album dir
            if len(os.listdir(album)) > 1:
                continue
            
            src = list(os.scandir(album))[0].path
            output_dir = opath.abspath(f'{top_level_dir}/../audio_out/{comic.name}/{album.name}')
            os.makedirs(output_dir, exist_ok=True)
            output_template = f'{output_dir}/%02d. {comic.name} - {album.name}.mp3'


            ffmpeg_cmd = f'ffmpeg -i "{src}" -f segment -segment_time 450 -segment_start_number 1 -b:a 320K -vn "{output_template}"'
            ffmpeg_cmd = shlex.split(ffmpeg_cmd)
            subprocess.run(ffmpeg_cmd, text=True)

          


            
if __name__ == '__main__':
    split_video_to_audio()






