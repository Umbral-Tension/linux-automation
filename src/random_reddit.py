#!/bin/python3
import pandas as pd
import os
import sys
from jtools.jconsole import test
"""Script to select 5 random subreddits from a local csv database and open them in firefox. 

    Accepts "SFW" and "NSFW" as the first argument to include only one or the other. Default includes both. """

BASE_DIR = os.path.dirname(__file__)
VISITED_SUBS_FILE = os.path.join(BASE_DIR, '/home/jeremy/Desktop/git-repos/linux-automation/resources/visited_subreddits.csv')
UNVISITED_SUBS_FILE = os.path.join(BASE_DIR, '/home/jeremy/Desktop/git-repos/linux-automation/resources/unvisited_subreddits.csv')

# make pandas objects
unvisited = pd.read_csv(UNVISITED_SUBS_FILE)
visited = pd.read_csv(VISITED_SUBS_FILE)

# get a few random subreddits
if len(sys.argv) > 1 and sys.argv[1] in ['sfw', 'nsfw']:  # Trim unvisited to only sfw or nsfw if specified.
    pool = unvisited.loc[unvisited['content_type'] == sys.argv[1]]
else:
    pool = unvisited
samp = pool.sample(5)
names = list(samp['real_name'])

# build and run firefox terminal command
firefox = 'firefox'
for x in names:
    sub_url = f'https://www.reddit.com/r/{x}'
    firefox += ' ' + sub_url


os.system(firefox)


# update lists
unvisited = unvisited.drop(samp.index)
unvisited.to_csv(UNVISITED_SUBS_FILE, index=False)

visited = pd.concat([visited, samp])
visited.to_csv(VISITED_SUBS_FILE, index=False)
