"""script that updates a file to assign a tier (1 or 2) to the song currently playing in Rhythmbox. To be used as I'm listening to my music library so i can slowly categorize
my music into tier 1 and 2 music. tier 1 = really good, tier 2 = okay. Uses winctrl to get window information to determine what song is playing."""

import os 
from os import path as opath
from fuzzywuzzy import fuzz
from window_manager import win_list

def set_tier(tier):
    if int(tier) not in [1, 2]:
        os.system('zenity --warning --text "invalid value for tier"')
        exit()
    dbfile = opath.join(opath.dirname(__file__), '../resources/music_tier_list.txt')
    my_artists = [x for x in os.scandir('/home/jeremy/@media/music') if x.is_dir]
    def get_output():
        # Get currently playing song from window title of Rhythmbox
        rbox = [x for x in win_list() if x['wm_class'] == 'rhythmbox.Rhythmbox']
        if rbox:
            # This parsing of the title string assumes no artist will have a hyphen in their name. 
            title = rbox[0]['title'].split('-', 1)
            artist = title[0].strip().casefold()
            song = title[1].strip().casefold()
            output = f'tier {tier} (no match): {rbox[0]["title"]}\n'
            for x in my_artists:
                if fuzz.ratio(x.name.casefold(), artist) > 80:
                    for path, dirs, files, in os.walk(x.path):
                        for f in files:
                            track = f[f.find('.'):].casefold().strip('.flac').strip('.mp3').strip()
                            if fuzz.ratio(song.casefold(), track) > 80:
                                output = f'tier {tier}: {opath.join(path, f)}\n'
        else:
            os.system('zenity --warning --title "music tier script" --text "No Rhythmbox window found. \n\nCannot get song information."')
            exit()
        return output

    try:
        with open(dbfile, 'r') as f:
            ls = f.readlines()
    except FileNotFoundError:
            ls = []

    ls.append(get_output())
    # remove duplictaes & sort
    ls = set(ls) 
    ls = sorted(list(ls), key=str.casefold)

    with open(dbfile, 'w') as f:
        f.writelines(ls)


        



if __name__=='__main__':
    import sys

    # Get tier info from args and exit if bad or no arguments are passed. 
    args = sys.argv
    try:
        if args[1] in ['-t', '--tier'] and args[2] in ['1', '2']:
            print(args[1], args[2])
            set_tier(args[2])
        else:
            exit()
    except IndexError:
        exit()

