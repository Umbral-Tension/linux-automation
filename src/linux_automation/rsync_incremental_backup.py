#!/bin/python3

# * This script uses rsync to create full and incremental backups of the directories src(1)-src(n) in the directory backups.
# 
# * To achieve the incremental backups rsync is used as follows: rsync -avPh --link-dest=DIR --delete SRC... [DEST]
#     * --link-dest=DIR instructs rsync to search through DIR on the DEST machine for an exact match to the files in SRC. If
#     it finds a match, a hard link is made in DEST pointing to that file in DIR, rather than the file being copied from SRC 
#     to DEST. In this script --link-dest=DIR is set to a symlink that points to the latest backup. Therefore, for each file
#     in SRC rsync finds its match in the latest backup and, if it  hasn't changed, hardlinks to it. The hardlinking allows
#     for many incremental backups to be made with little more storage than is required for a single full backup. 
#         * The first time the script is run "current" doesn't exist, so rsync ignores the --link-dest option and does a full 
#         copy of SRC to DEST, i.e. "a full backup". Full and icnremental backups are labeled as such in their directory name.  
#         * Because rsync ignores non-existent --link-dest, accidentally or intenntionally deleting current symlink  or its 
#         target just results in a new full backup being created.                
#     
#     * --delete Allows file deletions in SRC to be reflected in DEST. That is, if a file in SRC is deleted, the next time rsync 
#     runs it will delete that file in DEST. 
#     
# * Note: If one of SRC does not exist, rsync still exits with code 0. The backup will not be marked failed, and the non-existent
#   SRC directory will not appear in that or subsequent backups, but it will still exist in previous backups. 
# * Note: After a failed backup current points to the latest backup that succeeded. Subsequent backups may be run with no consequence.
# * Credit to Samuel Hewitt for the outline of this script: https://samuelhewitt.com/blog/2018-06-05-time-machine-style-backups-with-rsync.

import sys
import os
from os import path as opath
import argparse
from datetime import datetime
import subprocess
import shlex
import shutil
from jtools.jconsole import test

if __name__ == '__main__':
    print("---------- STARTING Jeremy's incremental rsync backup  ----------\n")
    parser = argparse.ArgumentParser(prog="rsync incremental backup", description="This script uses rsync to create full and incremental backups of important directories. Backups are stored in a directory called \"backups\" whose location may be specified with the --path-to-backup option")
    parser.add_argument('--default', help='run normally', action='store_true')
    parser.add_argument('--full', help='force full backup rather than incremental', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--path-to-backups', default="/run/media/jeremy/internal_6TB/rsync_backups")
    args = parser.parse_args()
    if not (args.dry_run or args.full or args.default):
        print("error: specify one of [--default, --full, --dry-run]")
        sys.exit()
    
    
    # Directories to backup. 
    # These MUST NOT end with a slash or rsync will copy only their contents rather than the directory AND its contents.
    src=['"/home/jeremy/jdata"',
         '"/home/jeremy/Desktop"',
         '"/home/jeremy/jdata/jvault"',
         '"/home/jeremy/Downloads"']
    # Directories to exclude 
    # note: given as rsync "filter rules". Don't understand why, but the dir to filter must be given as how it will appear in the Destination, not how it appears locally. I.E. jdata/git-repos instead of /home/jeremy/jdata/git-repos
    exclusions=[
        '--exclude="/home/jeremy/Downloads"',   # Downloads is currently just a link to jdata/downloads (including it causes symlink shenanigans)
        '--exclude="jdata/.Trash-1000"',        # 
        '--exclude="jdata/git-repos"',          # syncing issues
        '--exclude="jdata/jvault"',             # --^
        '--exclude="jdata/videos/tv"',          # already stored on backup drive
        '--exclude="jdata/videos/movies"',      # --^
        '--exclude="jdata/$RECYCLE.BIN"',]      # dumb Windows dir that gets added every time I boot to windows. 
    timestamp = datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
    # directory to put backups into (Default is set in arg parser) 
    backups=args.path_to_backups 
    os.makedirs(backups, exist_ok=True)
    # paths to the current latest backup and the new backup being created
    current = f'{backups}/current'
    if not opath.exists(current):
        args.full = True # can't do incremental if current doesn't exist
    newbackup = f'{backups}/{timestamp}_Full' if args.full else f'{backups}/{timestamp}_Incremental'

    
    # Build and run an rsync command to create a new backup. Send stdout and stderr to file.
    rs_opts = ['--debug=FILTER', '--itemize-changes', '--human-readable', '--progress', '--archive', '--delete', '--partial', f'--log-file="{backups}/temp_rsync_log"']
    if not args.full: # don't do incremental if full option is given
        rs_opts.append(f'--link-dest="{current}"')
    if args.dry_run:
        rs_opts.append('--dry-run')
    rs_opts.extend(exclusions)
    rsync_cmd = f'rsync {" ".join(rs_opts)} {" ".join(src)} "{newbackup}" 2> "{backups}/temp_rsync_stderr" | tee "{backups}/temp_rsync_stdout"'
    print(f"running rsync as follows:\n{rsync_cmd}\n") 
    rproc = subprocess.run(rsync_cmd, shell=True)

    
    # gather logging info 
    if args.dry_run:
        print("\n\n---------- Jeremy's incremental rsync backup ----------")
        print("DRY-RUN finished.")
        shutil.move(f"{backups}/temp_rsync_stderr", f"{backups}/{timestamp}_DRY-RUN_rsync_stderr")
        shutil.move(f"{backups}/temp_rsync_stdout", f"{backups}/{timestamp}_DRY-RUN_rsync_stdout")
        shutil.move(f"{backups}/temp_rsync_log", f"{backups}/{timestamp}_DRY-RUN_rsync_log")
        sys.exit() # end program here if dryrun. 
    else:    
        shutil.move(f'{backups}/temp_rsync_stderr', f"{newbackup}/rsync_stderr")
        shutil.move(f'{backups}/temp_rsync_stdout', f"{newbackup}/rsync_stdout")
        shutil.move(f'{backups}/temp_rsync_log', f"{newbackup}/rsync_log")
    # prepare a diff file with the first part of paths truncated up to the timestamp
    if not args.full:
        print('\n---------- running diff...')
        diff = subprocess.run(
            f'diff -rq --exclude="DIFF_CHANGES_SINCE_PREVIOUS_INCREMENTAL_BACKUP" --exclude="rsync_log" --exclude="rsync_stdout" --exclude="rsync_stderr" --exclude="ADDITIONS" --exclude="DELETIONS" "{newbackup}" "{opath.realpath(current)}"',
            shell=True, stdout=subprocess.PIPE, text=True)
        diff = sorted([x.replace(f'{backups}/', "") for x in diff.stdout.split('\n')])
        diff_file = f"{newbackup}/DIFF_CHANGES_SINCE_PREVIOUS_INCREMENTAL_BACKUP"
        with open(diff_file, 'w') as f:
            f.writelines("\n".join(diff))
        print(f"---------- finished diff\n")
    # print Summary
    shortcurr = opath.realpath(current).replace(f'{backups}/', '')
    shortnew = newbackup.replace(f'{backups}/', '')
    print('---------- DELETED')
    # running grep with "| tee" prevents colored output so it is run twice here, once for terminal output and once for file redirection
    subprocess.run(f'grep --color "Only in {shortcurr}" < "{diff_file}"', shell=True) #
    subprocess.run(f'grep --color "Only in {shortcurr}" < "{diff_file}" > "{newbackup}/DELETIONS"', shell=True)
    print('---------- ADDED')
    subprocess.run(f'grep --color "Only in {shortnew}" < "{diff_file}"', shell=True)
    subprocess.run(f'grep --color "Only in {shortnew}" < "{diff_file}" > "{newbackup}/ADDITIONS"', shell=True)
    print(f"\n\n---------- rsync process finished with exit code: {rproc.returncode} ----------\n")


    # check exit status to see if backup failed
    if rproc.returncode == 0:
        try:
            os.remove(current)
        except FileNotFoundError:
            pass
        # make current link to the newest backup
        os.symlink(newbackup, current)
        print(f'\nBackup successful. Logs placed in {newbackup}')
    else:
        # Rename directory if failed
        os.rename(newbackup, f'{backups}/failed_{timestamp}')
        print(f'\nBackup failed. Logs placed in {backups}/failed_{timestamp}')
    



    
