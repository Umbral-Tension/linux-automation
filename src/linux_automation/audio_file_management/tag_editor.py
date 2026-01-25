#!/bin/python3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, COMM
import os
import os.path as opath
import sys
from datetime import datetime
from jtools.jconsole import yellow, red, yes_no, exit_app
from jtools import jstring
import audiotags


class ProblemFileType(Exception):
    pass


def append_problem_file(filepath, problemtype):
    with open('tag_editor - problem files.txt', "a") as problems:
        problems.write(problemtype + '\n\t' + filepath + '\n')


def get_music_directories():
    """
    Collect directories to process from cmd line args or user. 
    """
    if len(sys.argv) > 1:
        music_dirs = sys.argv[1:]
        bad_paths = [x for x in music_dirs if not (opath.exists(x) and opath.isdir(x))]
        [music_dirs.remove(x) for x in bad_paths]
        if len(bad_paths) != 0:
            print('Ignoring non-directory and non-existent paths:\n\t' + yellow('\n\t'.join([opath.abspath(relpath) for relpath in bad_paths])))
        
        print('Formatting music tags in these directories:\n\t' + yellow('\n\t'.join([opath.abspath(relpath) for relpath in music_dirs])))
        return music_dirs
    else:
        music_dirs = input('Enter path to a directory that contains a structure like: Artist/Album/files: ')
        if opath.exists(music_dirs) and opath.isdir(music_dirs):
            return [music_dirs]
        else:
            print(yellow('That path is invalid'))
            return get_music_directories()


def make_mutagen(songpath, use_ID3=False):
    """ 
    Return a mutagen object (FLAC or EasyID3) based on the song's filetype.

    @param songpath: path to audio file. 
    @param use_ID3: use ID3 mutagen class instead of EasyID3
    """
    ext = opath.splitext(songpath)[1][1:]
    if ext.lower() == 'mp3':
        if use_ID3:
            return ID3(songpath)
        return EasyID3(songpath)
    if ext.lower() == 'flac':
        return FLAC(songpath)
    else:
        if ext.lower() not in ['jpg', 'jpeg', 'png', 'db', 'ini']:
            append_problem_file(songpath, 'problematic file type')
        raise ProblemFileType


def format_track_number(mut, songpath):
    """ 
    Change tracks formated as '3/10' to '03'. Adds 0 padding to track numbers.
    
    limitation: To determine the number of '0's to add as padding, this func checks the number of files that are in the same directory as songpath.
    This strategy assumes all files in the same directory are of the same album. If that isn't true the padding will be innacurate, though the
    track number itself will still be accurate. 

    @param mut: mutagen object (FLAC, EasyID3, ID3)
    @param songpath: path to audio file
    """
    track = mut['tracknumber'][0]
    if len(track) == 0:
        append_problem_file(songpath, 'empty tag: tracknumber')
    for seperater in ['\\', '/', '-', ':']:
        if seperater in track:
            track = track[0:track.index(seperater)]
    
    numtracks = len([x for x in os.listdir(opath.dirname(songpath)) if opath.splitext(x)[1].casefold() in ['.mp3', '.flac']])
    len_track, len_total = len(track), len(str(numtracks))    
    padding = (len_total - len_track) * '0'
    if padding == '' and len_track == 1 and len_total == 1:
        padding = '0'
    mut['tracknumber'] = padding + track
    mut.save()


def format_title(mut, songpath):
    """
    Titlecase the track title and remove things like "album version". 
    
    @param mut: mutagen object (FLAC, EasyID3, ID3)
    @param songpath: path to audio file
    """    
    if len(mut['title']) == 0:
        append_problem_file(songpath, 'empty tag: title')
        return
    title = mut['title'][0]
    title = title.casefold().replace('(album version)','').replace('album version', '')
    title = jstring.advanced_titlecase(title)
    title = title.strip()
    mut['title'] = title
    mut.save()


def rename_file(mut, songpath):
    """
    Rename file with format '{track}. {title}.{extension}'. 
    
    @param mut: mutagen object (FLAC, EasyID3, ID3)
    @param songpath: path to audio file
    """
    if len(mut['title']) == 0:
        return
    try:
        oldname = opath.basename(songpath)
        newname = f'{mut["artist"][0]} - {mut["album"][0]} - {mut["tracknumber"][0]}. {mut["title"][0]}{opath.splitext(songpath)[1]}'
        # replace slashes with dashes so they're not interpreted as part of a path. 
        newname = newname.replace('/', '-').replace('\\', '-') 
        # remove meaningful characters to placate bitch ass filesystems 
        illegal = '><:"|?*'
        for x in illegal:
            newname = newname.replace(x, '_')

        # Uncomment this to print filename changes if that's a concern. (like for processing large numbers of files ) 
        # if oldname != newname:
        #     print(f'\nfilename changed for path: {songpath}\nold: {oldname}\nnew: {newname}\n')
        
        newpath = songpath.replace(oldname, newname)
        os.rename(songpath, newpath)
    except FileExistsError:
        append_problem_file(songpath, 'Cannot rename file; file already exists')
    except OSError:
        append_problem_file(songpath, 'OSError on rename')


def add_date_added(mut, songpath):
    """Add a custom "date added" tag if it doesn't already exist. Used to track when songs were added to my collection.

    For flac files the key of the created tag is "jtag-date-added" 
    For mp3 files the key is "COMM:jtag-date-added:eng"
    
    @param mut: mutagen object (FLAC, EasyID3, ID3)
    @param songpath: path to audio file
    """
    FLAC_KEY = u'jtag-date-added'
    ID3_KEY = u'COMM:jtag-date-added:eng'
    if isinstance(mut, FLAC):
        # return if the file already has a dateadded tag to avoid overwriting it with the current date. 
        if FLAC_KEY not in mut.keys():
            mut[FLAC_KEY] = str(datetime.now())
    if isinstance(mut, ID3):
        if ID3_KEY not in mut.keys():
            mut.add(COMM(desc=u'jtag-date-added', lang='eng', text=str(datetime.now())))
    mut.save()



def get_jtag(jtag_key, mut=None, songpath=None):
    """return the value of one of my personal custom tags.
    
    Need this function to provide an easy way to access my custom tags in ID3 files, since they're 
    outside the limited set of tags that EasyID3 exposes in its dict like interface. 
    
    @param mut: mutagen object (FLAC, EasyID3, ID3)
    @param songpath: path to audio file
    """
    ID3_CONV = {u'jtag-date-added':u'COMM:jtag-date-added:eng'}

    if not songpath and not mut:
        return None
    # make mutagen if only a filepath is given        
    if songpath and mut is None: 
        mut = make_mutagen(songpath)

    if isinstance(mut, ID3):
        return mut[ID3_CONV[jtag_key]]
    else:
        return mut[jtag_key][0]


def format_standard(music_directories):
    if isinstance(music_directories, str):
        music_directories = [music_directories]
    songs = []
    for d in music_directories:    
        for path, dirs, files in os.walk(d):
            songs += [x.path for x in os.scandir(path) if x.is_file()]
    counter = 1
    numsongs = len(songs)
    milestones = [int(.25*x*numsongs) for x in range(1,5)]
    print('Processing ' + yellow(numsongs) + ' files.')
    for songpath in songs:
        if counter >= milestones[0]:
            percentage = round(milestones.pop(0)/numsongs*100)
            print('\t' + yellow(percentage) + yellow('%'))

        # Process uncommon tags 
        # These require an ID3 mutagen to manipulate rather than an EasyID3. 
        try:
            mut = make_mutagen(songpath, use_ID3=True)
        except ProblemFileType:
            continue
        except Exception as e:
            append_problem_file(songpath, str(e))
            continue
        add_date_added(mut, songpath)
        
        # Process common tags with EasyID3 mutagens
        try:
            mymutagen = make_mutagen(songpath)
        except ProblemFileType:
            continue
        except Exception as e:
            append_problem_file(songpath, str(e))
            continue

        # renaming invalidates the mutagen object so it must be the last function called.
        functions = [format_track_number, format_title, rename_file]
        for func in functions:
            try:
                func(mymutagen, songpath)
            except Exception as e:
                append_problem_file(songpath, str(e))
                continue
        counter += 1
    # Call user's attention to problems if they exist. 
    if os.path.exists('tag_editor - problem files.txt'):
        print(red('Problem files exist.'))
        retcode = os.system('xed "tag_editor - problem files.txt"')
        if retcode != 0:
            print(red('Failed to auto-open the error log in a text editor.'))
        
if __name__ == '__main__':
    music_dirs = get_music_directories()

    if yes_no(red(('Continue?'))):
        format_standard(music_dirs)
        exit_app('----------\nFinished')


