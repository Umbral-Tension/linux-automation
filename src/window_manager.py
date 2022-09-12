import os
import json

basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, '/home/jeremy/Desktop/git repos/linux-automation/resources/paths.json')) as fp:
    paths = json.load(fp)


def open(program_name, *args):
    program_name = str.lower(program_name)
    try:
        path = paths[program_name][0]
        window_title = paths[program_name][1]
    except KeyError:
        path = ''
        window_title = ''

    ###ADD LOGIC TO SWITCH TO APPROPRIATE WINDOW IF IT EXISTS


    cmd = ''
    browser = paths['firefox'][0]
    # random subreddit opener
    if program_name in ['r', 'rnsfw', 'rsfw']:
        cmd = f'jtools_random_reddit.py {program_name[1:]}'
    # Simple website opening
    elif path.startswith('http'):
        os.system(f'{browser} {path}')
    else:
        cmd = path
    

    # program opening
    os.system(cmd)

    
