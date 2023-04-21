#!/bin/python3

import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
from subprocess import Popen, PIPE, run
import traceback
from datetime import datetime


class Installer:

    def __init__(self):

        # relevant paths
        self.home = os.environ['HOME']
        self.git_repos = opath.join(self.home, '@data/git-repos')
        os.makedirs(self.git_repos, exist_ok=True)
        self.installerdir = opath.dirname(__file__)
        self.appdir = opath.dirname(self.installerdir)
        self.appname = opath.basename(self.appdir)

        logname = f'install log {datetime.now()}'
        latestlog = opath.join(self.installerdir, f'@LATEST-LOG.txt')
        try:
            os.remove(latestlog)
        except FileNotFoundError:
            pass
        os.makedirs(opath.join(self.installerdir, 'logs'), exist_ok=True)
        self.install_log = opath.join(self.installerdir, f'logs/{logname}')
        os.symlink(self.install_log, latestlog)
        
        try:
            run(['apt'], capture_output=True)
            self.package_manager = 'apt'
        except FileNotFoundError:
            try:
                run(['dnf'], capture_output=True)
                self.package_manager = 'dnf'
            except FileNotFoundError:
                print('No supported package manager found (apt, dnf). Exitting')
                sys.exit()
        
        # current step in the installatino process
        self.steps = []
        self.currstep = ''

    def install(self, program):
        """return either a dnf or apt install cmd depending on what is available"""
        return f'sudo {self.package_manager} -y install {program}'

    def step(self, description, print_now=True, nocolor=False):
        """update and print the current installation step."""
        self.currstep = description
        self.steps.append([description])
        if print_now:
            if nocolor:
                print(f'---->  {self.currstep}')
            else:
                print(jc.bold(jc.yellow('---->  ')+f'{self.currstep}'))

    def result(self, result, action=None, nocolor=False, norecord=False):
        """record and pretty print the specified result of the specified action
        Action defaults to currstep. 
        
        @param result: may be specified with the strings "ok/fail" or booleans. 
        @param nocolor: don't use color escape sequences
        @param norecord: Only print, don't record the result in self.steps
        """
        result = self._parseresult(result)
        if action is None:
            action = self.currstep
        if not norecord:
            for x in self.steps:
                if x[0] == action:
                    x.append(result)
        if nocolor:
            print(f'[{result}]:  {action}')
        else:
            if result == "OK":
                result = jc.green(result)
            else: 
                result = jc.red(result)
            print(f'[{jc.bold(result)}]:  {action}')
    

    def report(self):
        """ print and return a list of all installation steps and their results."""

        print(jc.bold(jc.yellow('\n////// Report /////')))
        for x in self.steps:
            self.result(x[1], x[0], norecord=True)
        

    def log(self, result, action):
        """add line to log file like \"[result]:  [action]\"
        
        @param result: may be specified with strings "ok/fail" or booleans. 
        """
        result = self._parseresult(result)
        with open(self.install_log, 'a') as log:
            line = f"[{result}]:  {action}\n"
            log.writelines(line)

    def _parseresult(self, result):
        if isinstance(result, str):
            result = result.casefold()
        return {True:"OK", False:"FAIL", "ok": "OK", "fail": "FAIL"}[result]


    def chain(self, cmds, logall=False, ignore_exit_code=False, quiet=False):
        """run a series of commands in the shell, returning False immediately
         if one in the series exits with any non-zero value. 
        
        @param cmds: list of strings, each of which is a single shell command,
        such as "mv src dest".  
        @param logall: if True, log each command that is run, not just those, that fail.
        @param ignore_exit_code: don't return if one of cmds returns non-zero.
        @param quiet: don't print stdout content as the subprocess makes it 
        available. 
        """
        
        for x in cmds:
            try:
                cmd = shlex.split(x)
                with Popen(cmd, bufsize=1, stdout=PIPE, stderr=PIPE, text=True) as resp:
                    if not quiet:
                        for line in resp.stdout:
                            print(line, end='') # process line here
                    resp.wait()
                    if ignore_exit_code:
                        return True
                    if resp.returncode != 0:
                        print(f'failed (return code {resp.returncode}): {x}')

                        errstr = ''.join([x for x in resp.stderr])
                        self.log(False,
                                f'(return code {resp.returncode}): {x}\
                                    \n\tstderr:\n\t\t{errstr}')
                    
                        return False
            except:
                estring = traceback.format_exc()
                print(estring)
                self.log(False, f'{x}\n\t{estring}')
                return False
            if logall:
                self.log(True, x)
        return True


if __name__ == '__main__':
    print('\n\n///////////////////////////////////////////////')
    print('///////   linux-automation installer    ///////\n')
    inst= Installer()

    # pip and python modules
    inst.step('get python packages', nocolor=True)
    outcome = inst.chain([
        inst.install('pip'),
        'pip install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein',
    ])
    inst.log(outcome, inst.currstep)
    inst.result(outcome, nocolor=True)

    # get jconsole 
    inst.step('download jtools', nocolor=True)
    chain = inst.chain([f'git clone https://github.com/umbral-tension/python-jtools {inst.installerdir}/localjtools'])
    outcome = False
    if chain:
        shutil.move(f'{inst.installerdir}/localjtools/src/jtools/jconsole.py', f'{inst.installerdir}/jconsole.py')
        shutil.rmtree(f'{inst.installerdir}/localjtools')
        import jconsole as jc
        outcome = True
    inst.result(outcome, nocolor=True)
    inst.log(outcome, inst.currstep)
   
    # gcc
    inst.step('get gcc')
    outcome = inst.chain([inst.install('gcc')])
    inst.log(outcome, inst.currstep)
    inst.result(outcome)

    # clone misc-db-files repo into git-repos/ 
    inst.step('get misc-db-files repository')
    outcome = inst.chain([
        f'git clone git@github.com:umbral-tension/misc-db-files {inst.git_repos}/misc-db-files'
    ])
    inst.log(outcome, inst.currstep)
    inst.result(outcome)

    # keyd
    inst.step('download and install keyd')
    keyd_conf = f'{inst.appdir}/resources/configs/my_keyd.conf'
    inst.chain([f'git clone https://github.com/rvaiya/keyd {inst.installerdir}/keyd'])
    os.chdir(f'{inst.installerdir}/keyd')
    outcome = inst.chain([
        'make',
        'sudo make install',
        'sudo systemctl enable keyd',
        f'sudo cp {keyd_conf} /etc/keyd/default.conf',
        'sudo systemctl restart keyd',
        ])
    inst.log(outcome, inst.currstep)
    inst.result(outcome)
    os.chdir(inst.installerdir)


    
    # bashrc, jrouter, dconf
    inst.step('bashrc, jrouter, dconf')
    with open(f'{inst.home}/.bashrc', 'a') as f:
        f.writelines([f'. {inst.appdir}/resources/configs/bashrc fedora'])
    try:
        os.remove('/home/jeremy/bin/jrouter')
    except FileNotFoundError:
        pass
    os.symlink(f'{inst.appdir}/src/linux_automation/jrouter.py', '/home/jeremy/bin/jrouter')         
    os.system(f'dconf load -f /org/gnome/settings-daemon/plugins/media-keys/ < "{inst.appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:settings-daemon:plugins:media-keys:"')
    # outcome = inst.chain([
    #     f'dconf load -f /org/gnome/settings-daemon/plugins/media-keys/ < "{inst.appdir}/resources/dconf/dconf fedora/dirs/:org:gnome:settings-daemon:plugins:media-keys:"'
    # ])
    # inst.log(outcome, inst.currstep)
    # inst.result(outcome)
    
    
    # cleanup
    inst.step('cleanup')
    outcome = inst.chain([
        f'rm -rf {inst.installerdir}/keyd',
        f'rm -rf {inst.installerdir}/jconsole.py',
    ])
    inst.log(outcome, inst.currstep)
    inst.result(outcome)

    # Show final report
    inst.report()