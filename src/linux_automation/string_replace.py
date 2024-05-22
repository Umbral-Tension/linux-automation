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
    try:
        args = sys.argv
        if len(args) > 1:
            paths = [opath.join(os.getcwd(), x) for x in args[1:]]
        else:
            jc.exit_app('no path arguments recieved')
        
        print("##################\nThis script takes paths as arguments and removes/replaces a given string from the last component of each path. This means if a directory path is received the name of the directory is changed, NOT the names of the files in that directory. (intended to be invoked from the context menu of some file explorer like nemo, which can pass it the paths of mouse-selected files/directories)\n")
        
        copy_paste_string = jc.yellow('####\n1st filename for COPY/PASTE purposes: {{') + jc.white(f'{opath.basename(paths[0])}') + jc.yellow('}}\n#####\n\n')
        print(copy_paste_string)

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

        if not opath.exists('/home/jeremy/jdata/logs/'):
            os.mkdir('/home/jeremy/jdata/logs/')
        logfile = f'/home/jeremy/jdata/logs/remove_string.py {str(datetime.now())}'    
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
                
            
        

    except Exception as e:
        print(jc.red(traceback.format_exc()))
        input()

    