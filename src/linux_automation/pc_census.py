#!/bin/python3
"""
This script creates a 'census' of the important directories on my pc. In the event of data loss, the census can be 
referenced during any rebuilding that takes place. It also warns if a lot of files have been deleted in a relevant directory since
the previous census so that accidental file deletions don't go unnoticed. 
"""
import shutil
import os
from os import path as opath    
from subprocess import run
from datetime import datetime
import xml.etree.ElementTree as ET
from jtools.jconsole import test, ptest, red

def diff(current, previous, sentinel_val=5):
    if previous is None:
        return []
    """compare file counts in various directories between current and prevous census"""
    warnings = []
    old = [x for x in os.listdir(previous) if x.endswith('XML')]
    new = [x for x in os.listdir(current) if x.endswith('XML')]

    for x in old:
        if x not in new:
            warnings.append(f'no census file for {x} in {current}')
            old.remove(x)
    
    for x in old:
        old_count = ET.parse(opath.join(previous, x)).find('./report/files').text
        new_count = ET.parse(opath.join(current, x)).find('./report/files').text
        difference = int(old_count) - int(new_count) 
        if difference >= sentinel_val:
            warnings.append(f'{difference} file deletions in {x} since last census')

    return warnings

def build_census():
    census_directory = '/media/jeremy/external_jdata/pc file census'
    warnings = []
    try:
        all_previous = sorted(os.listdir(census_directory))
    except FileNotFoundError:
        warnings.append(f'!! No census directory found at {census_directory}')
        os.makedirs(census_directory)
    try:
        previous = f'{census_directory}/{all_previous[-1]}'
    except IndexError:
        previous = None

    # make dir to hold new census
    timestamp = str(datetime.now())
    timestamp = timestamp[:timestamp.rfind('.')] # remove decimal seconds
    new = f'{census_directory}/pc_census {timestamp}'
    os.makedirs(new)
    
    # paths to monitor
    home = os.getenv('HOME')
    data = opath.join(home, '@data')
    data_dirs = os.listdir(data) # dirs I keep in a big personal @data directory
    other_dirs = [
        opath.join(home, 'Desktop'),
        opath.join(home, 'Downloads')
        ]

    # use tree cli utility to generate file listings
    def run_tree(path, outdir, outname):
        """use tree cli utility to generate file listings"""
        run(['tree', '-na', '-o', f'{outdir}/{outname}.md', path])
        run(['tree', '-Xa', '-o', f'{outdir}/{outname}.XML', path])
        # wrap human readable file in markdown code tags so it's displayed in monospace in obsidian
        with open(f'{outdir}/{outname}.md', 'r') as f:
            lines = f.readlines()
        outlines = ['```\n']
        outlines.extend(lines)
        outlines.append('\n```')
        with open(f'{outdir}/{outname}.md', 'w') as f:
            f.writelines(outlines)

    for x in data_dirs:
        path = opath.join(data, x)
        if not opath.exists(path):
            warnings.append(f'path does not exist: {path}')
            continue
        run_tree(path, new, x)
    
    for path in other_dirs:
        if not opath.exists(path):
            warnings.append(f'path does not exist: {path}')
            continue
        run_tree(path, new, path.replace('/', '-'))
        
    # check file count differences
    diff_warnings = diff(new, previous)
    warnings.extend(diff_warnings)
    
    # delete all but the newest 30 census (~30 days)
    newest_30 = all_previous[-29:]
    for x in all_previous:
        if x not in newest_30:
            shutil.rmtree(f'{census_directory}/{x}')

    # save and display warnings
    warnings_file = f'{new}/warnings'
    if len(warnings) > 0:
        with open(warnings_file, 'w') as f:
            f.write(f'Census: {timestamp}\n')
            for x in warnings:
                print(red(x))
                f.write(f'\t{x}\n')

    # copy newest and oldest census and warnings to Obsidian vault. 
    try:
        obsidian = '/home/jeremy/@data/jvault/Memory 2/pc file census'
        try:
            shutil.rmtree(f'{obsidian}/current')
            shutil.rmtree(f'{obsidian}/oldest')
        except FileNotFoundError:
            pass
        shutil.copytree(new, f'{obsidian}/current', dirs_exist_ok=True)
        shutil.copytree(f'{census_directory}/{newest_30[0]}', f'{obsidian}/oldest', dirs_exist_ok=True)
        if opath.exists(warnings_file):
            with open(warnings_file, 'r') as f:
                lines = f.readlines()
            with open(f'{obsidian}/warnings.md', 'a') as f:
                f.writelines(lines)
            
    except IndexError:
        pass




if __name__ == '__main__':
    print("/// Jeremy's pc file census")
    print('...')
    build_census()
    print('finished')

