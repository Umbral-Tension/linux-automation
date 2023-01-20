#!/bin/python3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, COMM
import os
import os.path as opath
import sys
import string
from datetime import datetime
from jtools.jconsole import *



class ProblemFileType(Exception):
    pass


def append_problem_file(filepath, problemtype):
    with open('tag_editor - problem files.txt', "a") as problems:
        problems.write(problemtype + '\n\t' + filepath + '\n')


def get_music_directories():
    if len(sys.argv) > 1:
        music_dirs = sys.argv[1:]
        for x in music_dirs:
            if not (opath.exists(x) and opath.isdir(x)):
                music_dirs.remove(x)
        print('Formatting music tags in these directories:\n\t' + yellow('\n\t'.join([opath.abspath(relpath) for relpath in music_dirs])))
        return music_dirs
    else:
        music_dirs = input('Enter path to a directory that contains a structure like: Artist/Album/files: ')
        if opath.exists(music_dirs) and opath.isdir(music_dirs):
            return music_dirs
        else:
            print(yellow('That path is invalid'))
            return get_music_directories()


def make_mutagen(songfile):
    """ Make a mutagen object based on the song's filetype.

    parameters:
    songfile (os.DirEntry) - file object for which to find the filetype
    """
    ext = opath.splitext(songfile)[1][1:]
    if ext.lower() == 'mp3':
        return EasyID3(songfile.path)
    if ext.lower() == 'flac':
        return FLAC(songfile.path)
    else:
        if ext.lower() not in ['jpg', 'jpeg', 'png', 'db', 'ini']:
            append_problem_file(songfile.path, 'problematic file type')
        raise ProblemFileType


def format_track_number(mut, song):
    track = mut['tracknumber'][0]
    if len(track) == 0:
        append_problem_file(song.path, 'empty tag: tracknumber')
    for seperater in ['\\', '/', '-']:
        if seperater in track:
            track = track[0:track.index(seperater)]
    if len(track) == 1:
        track = '0' + track
    mut['tracknumber'] = track
    mut.save()


def titlecase(mut, song):
    if len(mut['title']) == 0:
        append_problem_file(song.path, 'empty tag: title')
        return
    mut['title'] = string.capwords(mut['title'][0])
    mut.save()


def set_single_artist(mut, song):
    if len(mut['artist']) == 0:
        append_problem_file(song.path, 'empty tag: artist')
        return
    artiststr = mut['artist'][0]
    artiststr = artiststr.split(';')[0]
    mut['artist'] = artiststr
    mut.save()


def remove_unwanted_tags(mut, song):
    for tag in ['albumartist', 'discnumber', 'composer']:
        mut[tag] = []
    mut.save()


def rename_file(mut, song):
    if len(mut['title']) == 0:
        return
    try:
        newname = f'{mut["tracknumber"][0]}. {mut["title"][0]}{opath.splitext(song)[1]}'
        # replace slashes with dashes so they're not interpreted as part of a path. 
        newname = newname.replace('/', '-').replace('\\', '-') 

        newpath = song.path.replace(song.name, newname)
        os.rename(song.path, newpath)
    except FileExistsError:
        append_problem_file(song.path, 'Cannot rename file; file already exists')
    except OSError:
        append_problem_file(song.path, 'OSError on rename')


def add_date_added(songfile):
    """Add a custom "date added" tag if it doesn't already exist. Used to track when songs were added to my collection.

    For flac files the key of the created tag is "jtag-date-added" 
    For mp3 files the key is "COMM:jtag-date-added:eng"
    """
    FLAC_KEY = u'jtag-date-added'
    ID3_KEY = u'COMM:jtag-date-added:eng'
    ext = opath.splitext(songfile)[1].casefold()
    if ext == '.flac':
        mut = FLAC(songfile.path)
        # return if the file already has a dateadded tag to avoid overwriting it with the current date. 
        if FLAC_KEY not in mut.keys():
            mut[FLAC_KEY] = str(datetime.now())
            mut.save()
    elif ext == '.mp3':
        mut = ID3(songfile.path)
        # return if the file already has a dateadded tag to avoid overwriting it with the current date. 
        if ID3_KEY not in mut.keys():
            mut.add(COMM(desc=u'jtag-date-added', lang='eng', text=str(datetime.now())))
            mut.save()


def get_jtag(jtag_key, songfile=None, mut=None):
    """return the value of one of my personal custom tags.
    
    Need this function to provide an easy way to access my custom tags in ID3 files, since they're 
    outside the limited set of tags that EasyID3 exposes in its dict like interface. 
    """
    ID3_CONV = {u'jtag-date-added':u'COMM:jtag-date-added:eng'}

    if not songfile and not mut:
        return None
    # make mutagen if only a filepath is given        
    if songfile and mut is None: 
        ext = opath.splitext(songfile)[1].casefold()
        if ext == '.flac':
            mut = FLAC(songfile.path)
        elif ext == '.mp3':
            mut = ID3(songfile.path)
        else:
            return None

    if isinstance(mut, ID3):
        return mut[ID3_CONV[jtag_key]]
    else:
        return mut[jtag_key][0]


def format_standard(music_directories):
    songs = []
    for d in music_directories:    
        for path, dirs, files in os.walk(d):
            songs += [x for x in os.scandir(path) if x.is_file()]
    counter = 1
    milestones = [int(.25*x*len(songs)) for x in range(1,5)]
    print('Processing ' + yellow(len(songs)) + ' files.')
    for song in songs:
        if counter >= milestones[0]:
            percentage = round(milestones.pop(0)/len(songs)*100)
            print('\t' + yellow(percentage) + yellow('%'))

        # Process custom tags 
        # These require an ID3 mutagen to manipulate rather than an EasyID3. 
        add_date_added(song)
        
        # Process common tags with EasyID3 mutagens
        try:
            mymutagen = make_mutagen(song)
        except ProblemFileType:
            continue
        except Exception as e:
            append_problem_file(song.path, str(e))
            continue

        # renaming invalidates the mutagen object and the song DirEntry so it must be the last function called.
        functions = [format_track_number, titlecase, set_single_artist, remove_unwanted_tags, rename_file]
        for func in functions:
            try:
                func(mymutagen, song)
            except Exception as e:
                append_problem_file(song.path, str(e))
                continue
        counter += 1
    # Call user's attention to problems if they exist. 
    if os.path.exists('tag_editor - problem files.txt'):
        print(red('Problem files exist.'))
        retcode = os.system('xed "tag_editor - problem files.txt"')
        if retcode != 0:
            print(red('Failed to auto-open the error log in a text editor.'))
        
if __name__ == '__main__':

    format_standard(get_music_directories())
    exit_app('----------\nFinished')


