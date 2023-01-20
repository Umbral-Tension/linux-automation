#!/bin/python3
from mutagen import easyid3
from mutagen import flac
import os
import os.path as opath
import sys
import string
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
            print()
            return get_music_directories()


def make_mutagen(songfile):
    """ Make a mutagen object based on the song's filetype.

    parameters:
    songfile (os.DirEntry) - file object for which to find the filetype
    """
    ext = opath.splitext(songfile)[1][1:]
    if ext.lower() == 'mp3':
        return easyid3.EasyID3(songfile.path)
    if ext.lower() == 'flac':
        return flac.FLAC(songfile.path)
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
        os.system('xed "tag_editor - problem files.txt"')
        
if __name__ == '__main__':

    format_standard(get_music_directories())
    exit_app('Finished')


