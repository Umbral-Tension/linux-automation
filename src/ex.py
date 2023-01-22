import tag_editor as tg
import os
from os import path as opath
from jtools.jconsole import test, ptest
import string


mypath = '/home/jeremy/Desktop/Done'




arts = [opath.join(mypath, x) for x in os.listdir(mypath)]

for art in arts:
    albs = [opath.join(art, x) for x in os.listdir(art)]
    for alb in albs:
        names = sorted(os.listdir(alb))
        for x in names:
            stripped = opath.splitext(x)[0][4:]
            if stripped.count('-') != 2:
                # print(tg.red(x))
                continue
            
        
            info = [x.strip() for x in stripped.split('-')]
            tit, artist, album = string.capwords(info[0]), string.capwords(info[1]), string.capwords(info[2])
            # test(tit, artist, album)
         
            songpath = opath.join(alb, x)
            mut = tg.make_mutagen(songpath)
            tg.format_track_number(mut, songpath)
            mut['title'] = f'{tit} - {artist} - {album}'
            mut.save()
            tg.rename_file(mut, songpath)


    
    

        
    