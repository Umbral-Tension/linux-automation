"""This script takes paths as arguments and removes or replaces a given string from the last component of each path. 
If a path to a directory is received the name of the directory ITSELF is changed; directories are not recursed into for safety reasons.
(intended to be invoked from the context menu of some file explorer like nemo, which can pass it the paths of mouse-selected files/directories)"""

from jtools import jconsole as jc
import os
import os.path as opath
import sys
from datetime import datetime
import traceback



if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        paths = [opath.join(os.getcwd(), x) for x in args[1:]]
    else:
        jc.exit_app('no path arguments recieved')
    
    print("##################\nThis script takes paths as arguments and removes/replaces a given string from the last component of each path. This means if a directory path is received the name of the directory is changed, NOT the names of the files in that directory. (intended to be invoked from the context menu of some file explorer like nemo, which can pass it the paths of mouse-selected files/directories)\n")
    
    badstring = input(jc.yellow('String to replace? (case-SENSITIVE, be mindful of SPACES):'))
    replacement = input(jc.yellow('Replace with? (leave blank to simply remove the string):'))
            

    paths_as_str = '\n\t'.join(paths)
    confirmation_message = \
        jc.yellow('Replace {{') + jc.white(badstring) + \
        jc.yellow('}} with {{') + jc.white(replacement) + \
        jc.yellow('}} in the following paths?\n\t') + \
        jc.white(f'{paths_as_str}\n')  
    

    if not jc.yes_no(confirmation_message):
        sys.exit()

    logfile = f'/home/jeremy/@data/logs/remove_string.py {str(datetime.now())}'    
    for x in paths:
        namestring = opath.basename(x)
        parent = opath.dirname(x)

        newname = namestring.replace(badstring, replacement)

        src = x
        dest = opath.join(parent, newname)

        try:
            os.rename(src, dest)
            with open(logfile, '+a') as f:
                f.writelines(f'{src}\n{dest}\n\n')
        except Exception as e:
            with open(logfile, '+a') as f:
                f.writelines(f'######FAILED RENAME\n{src}\n{dest}\n{traceback.format_exc()}\n\n')    
            
        
        

        
        

    