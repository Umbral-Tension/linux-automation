import shutil
import os
import sys
import jtools.jconsole
from jtools.jconsole import *
from jtools.jdir import jdir



try:
    top_dir = sys.argv[1]
except IndexError:
    exit_app('No directory received as argument')

dump = os.path.join(top_dir, '@root_dump')
if not yes_no('Perform root dump on \'' + top_dir + '\'?'):
    exit_app('Root dump operation canceled')
if jdir.is_danger_dir(top_dir):
    exit_app('Not safe to do a root dump on: ' + top_dir)

try:
    os.mkdir(dump)
except FileExistsError:
    exit_app('Cannot run root_dump.\n The directory: @root_dump already exists.')
except:
    exit_app('Unknown error.')

og_count = jdir.get_file_count(top_dir)
for currpath, dirs, files in os.walk(top_dir):
    if os.path.samefile(currpath, dump):
        continue
    for x in files:
        name = jdir.dup_rename(x, dump)
        try:
            shutil.copy2(currpath + '/' + x, dump + '/' + name)
        except OSError:
            print('OSError: ', OSError)
dump_count = jdir.get_file_count(dump)

if dump_count != og_count:
    exit_app('Warning: root dump was performed, but the file count in @root_dump does not match the file count in top_dir')
exit_app('Root dump was successful')




