import os
from os import walk
from os.path import join
from pathlib import Path
import json
from jtools.jdir.jdir import dup_rename, get_all_files, get_all_subdirs
from jtools.jconsole import test, ptest
"""
This script creates a 'census' of the important directories on a pc. In the event of data loss, the census can be 
referenced during any rebuilding that takes place. The list of directories to record the contents of is stored in 
census_paths.json, and the census itself is stored in pc_census.json
"""

def load_census_paths():
    """ Load list of directories to be checked. """
    scriptdir = Path(__file__).parent
    census_paths = join(scriptdir, 'census_paths.json')
    with open(census_paths, 'r') as cpaths:
        census_paths = json.load(cpaths)
    return census_paths


def get_census(census_paths):
    """ build census dictionary object. """
    census_dict = {}
    for x in census_paths:
        currpath = census_paths[x]
        if x == 'music':
            artists = sorted( [d for d in os.listdir(currpath)] )
            census_dict['music'] = {
                'artists': artists,
                'songs': get_all_files(currpath)
                }
        elif x == 'videos':
            census_dict['videos'] = get_all_files(currpath)
        else:
            census_dict[x] = get_all_subdirs(currpath)
    return census_dict


def serialize(census_dict):
    """ Save the census dictionary to a json file in the local google drive folder. """
    targetdir = 'c:/users/jeremy/google drive/documents/archival shit/media census'
    filename = dup_rename('pc_census.json', targetdir) 
    with open(join(targetdir, filename), 'w') as dumpfile:
        json.dump(census_dict, dumpfile, indent=2)

        
if __name__ == '__main__':
    census_paths = load_census_paths()
    census_dict = get_census(census_paths)
    serialize(census_dict)



