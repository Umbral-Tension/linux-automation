""" get tags for audio files. Either retrieve the embbeded tags or look them up on Musicbrainz"""
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, COMM
import os
import os.path as opath
import sys
import string
from datetime import datetime
from jtools.jconsole import test

class ProblemFileType(Exception):
    pass

SUPPORTED_FILETYPES = ['.mp3', '.flac']

def parse_filepath(filepath):
    """ return a sanitized list of audio file paths """
    # get filepath into list of strings format
    if type(filepath) is str:
        returnlist = [filepath]
    elif type(filepath) is list:
        returnlist = filepath.copy()
    else:
        raise TypeError
    
    #recurse if a directory was given 
    if opath.isdir(returnlist[0]):
        allfiles = []
        for path, dirs, files in os.walk(returnlist[0]):
                allfiles += [x.path for x in os.scandir(path) if x.is_file()]    
        returnlist = allfiles.copy()

    # purity test
    for x in returnlist:
        if not (opath.exists(x) and opath.isfile(x) and str.casefold(opath.splitext(x)[1]) in SUPPORTED_FILETYPES):
            returnlist.remove(x)
    return returnlist
    

# get embedded tags
def get_mutagens(filepaths, use_ID3=False):
    """Return a dictionary that maps each audio file to a Mutagen object containing its tags
    @param filepath: can be
        - path to a single audio file 
        - a list of file paths (only the 1st item in this list will be recursed into if it is a directory)
        - path to a directory to be recursed into
    @param use_ID3: use ID3 mutagen class instead of EasyID3 for advanced ID3 tag edditing.  
    """
    tagdict = {}
    filepaths = parse_filepath(filepaths)
    for x in filepaths:
        ext = opath.splitext(x)[1][1:]
        
        if ext.lower() == 'mp3':
            if use_ID3:
                mut = ID3(x)
            mut = EasyID3(x)
        if ext.lower() == 'flac':
            mut = FLAC(x)
        tagdict[x] = mut
    return tagdict





# get tags via musicbrainz lookup
def get_musicbrainz_tags(filepaths):
    """ """
    filepaths = parse_filepath(filepaths)


if __name__ == "__main__":
    b = get_mutagens("/home/jeremy/jdata/audio/music")

    print(b)
    print('\n\n\n')
    input('pausing block')