"""script for classifying the currently playing song by reading the song info 
from a running Rhythmbox window title and updating one of my db files. """

import os, sys 
from os import path as opath
from fuzzywuzzy import fuzz
display_server = os.environ['XDG_SESSION_TYPE'].casefold() # wayland or x11
if display_server == 'wayland':
    from window_manager.wm_wayland import win_list
    rhythmbox_winclass = 'Rhythmbox'
else:
    from window_manager.wm_xorg import win_list
    rhythmbox_winclass = 'rhythmbox.Rhythmbox'

obsidian_vault = '/home/jeremy/@data/jvault/Memory 2/M2 Miscellaneous/music classifications'

def match_song():
    """Try to match the song info in the window title of Rhythmbox to a file in my music directory.
    Return a list like [path_to_song, artist, song] if a match is found or [rhythmbox_window_title] 
    if no match is found. """
    global rhythmbox_winclass
    my_artists = [x for x in os.scandir('/home/jeremy/@data/music') if x.is_dir]
    rbox = [x for x in win_list() if x['wm_class'] == rhythmbox_winclass]
    if rbox:
        # This parsing of the title string assumes no artist will have a hyphen in their name. 
        wintitle = rbox[0]['title'].split('-', 1)
        win_title_artist = wintitle[0].strip().casefold()
        win_title_song = wintitle[1].strip().casefold()
        
        for real_artist in my_artists:
            if fuzz.ratio(win_title_artist, real_artist.name.casefold()) > 80:
                for dirpath, dirs, files, in os.walk(real_artist.path):
                    for f in files:
                        real_title = f[f.find('.')+2:].casefold().replace('.flac','').replace('.mp3','').strip()
                        if fuzz.ratio(win_title_song, real_title) > 80:
                            # return [path_to_song, artist, title]
                            return [opath.join(dirpath, f), real_artist.name, real_title]
        return [rbox[0]['title']]
    else:
        os.system('zenity --warning --title "music tier script" --text "No Rhythmbox window found. \n\nCannot get song information; exitting now."')
        sys.exit()


def readfile(name):
    """get the contents of the Obsidian file with the given name as a list of lines"""
    global obsidian_vault
    try:
        with open(opath.join(obsidian_vault, name+'.md'), 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        return []


def writefile(name, lines):
    """write lines to the Obsidian file with the given name"""
    global obsidian_vault 
    try:
        with open(opath.join(obsidian_vault, name+'.md'), 'w') as f:
            f.writelines(lines)
        os.system(f'zenity --notification --text="Succesful {name} classification"')
    except: 
        os.system('zenity --warning --text="Music classification failed. Failed to write file. Attempting to dump current list to home directory"')
        with open(f'/home/jeremy/{name} emergency dump', 'w') as f:
            f.writelines(lines)


def set_tier(tier):
    """Assign a tier of 1 or 2 to the currently playing song"""

    if int(tier) not in [1, 2]:
        os.system('zenity --warning --text "invalid value for tier"')
        sys.exit()

    # get current list
    ls = readfile('by tiers')
    
    # format a new entry line
    song_info = match_song()
    if len(song_info) == 1:
        new_entry = f"tier {tier} (no match): {song_info[0]}"
    else:
        new_entry = f"tier {tier}: {song_info[0].replace('/home/jeremy/@data/music/', '')}\n"
    ls.append(new_entry)
    
    # remove duplictaes & sort
    ls = set(ls) 
    ls = sorted(list(ls), key=str.casefold)
    
    # write changes to file
    writefile('by tiers', ls)

        
def set_vibe(vibe):
    """ classify song as having the specified vibe by appending the song to
    the file with that vibe's name."""
    ls = readfile(vibe)
    song_info = match_song()
    if len(song_info) == 1:
        new_entry = song_info[0] # will be rhythmbox window title
        new_entry = f'(no match): {new_entry}\n'
    else:
        new_entry = song_info[0] # will be path to file
        new_entry = new_entry.replace('/home/jeremy/@data/music/', '') + '\n'
        

    ls.append(new_entry)
    ls = set(ls)
    ls = sorted(list(ls), key=str.casefold)

    writefile(vibe, ls)

    
    
    

if __name__=='__main__':
    import sys

    # Get tier info from args and exit if bad or no arguments are passed. 
    args = sys.argv
    try:
        if args[1] in ['-t', '--tier']:
            print(args[1], args[2])
            set_tier(args[2])
        if args[1] in ['-V', '--vibe']:
            set_vibe(args[2])
    except IndexError:
        pass

