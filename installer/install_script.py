import os, shutil, sys
import os.path as opath
import shlex
from shlex import split as lex
from subprocess import Popen, PIPE, run
import traceback

from datetime import datetime


class Installer:

    def __init__(self):

        # paths
        self.home = os.environ['HOME']
        self.git_repos = opath.join(self.home, '@data/git-repos')
        self.appdir = opath.dirname(__file__)
        self.appname = opath.basename(self.appdir)
        logname = f'install log {datetime.now()}'
        latestlog = opath.join(self.appdir, f'@LATEST-LOG.txt')
        try:
            os.remove(latestlog)
        except:
            pass
        self.install_log = opath.join(self.appdir, f'logs/{logname}')
        os.symlink(self.install_log, latestlog)
        # current step in the installatino process
        self.currstep = ''

    def step(self, description, print_now=True, nocolor=False):
        """update and print the current installation step."""
        self.currstep = description
        if print_now:
            if nocolor:
                print(f'---->  {self.currstep}')
            else:
                print(jc.bold(jc.blue('---->  ')+f'{self.currstep}'))

    def print_result(self, result, nocolor=False):
        """pretty print the specified result of currstep
        
        result may be specified with strings "ok/fail" or booleans. 
        """
        result = {True:"OK", False:"FAIL", "ok": "OK", "fail": "FAIL"}[result]
        if nocolor:
            print(f'[{result}]:  {self.currstep}')
        else:
            if result == "OK":
                result = jc.green(result)
            else: 
                result = jc.red(result)
            print(f'[{jc.bold(result)}]:  {self.currstep}')


    def log(self, result, action):
        """add line to log file like \"[result]:  [action]\"
        
        result may be specified with strings "ok/fail" or booleans. 
        """
        result = {True:"OK", False:"FAIL", "ok": "OK", "fail": "FAIL"}[result]
        with open(self.install_log, 'a') as log:
            line = f"[{result}]:  {action}\n"
            log.writelines(line)


    def chain(self, cmds, logall=False, ignore_exit_code=False, print_realtime=False):
        """run a series of commands in the shell, returning False immediately
         if one in the series exits with any non-zero value. 
        
        @param logall: if True, log each command that is run, not just those, that fail.
        @param ignore_exit_code: don't return if one of cmds returns non-zero.
        @param print_realtime: print stdout content as the subprocess makes it 
        available. 
        """
        
        for x in cmds:
            try:
                cmd = shlex.split(x)
                with Popen(cmd, bufsize=1, stdout=PIPE, stderr=PIPE, text=True) as resp:
                    if print_realtime:
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
                if print_realtime:
                    print()
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


    # 1.1 - 1.2
    inst.step('get python packages', nocolor=True)
    outcome = inst.chain([
        'sudo dnf install pip',
        'echo pip install ipython PyQt5 pandas mutagen colorama progress fuzzywuzzy Levenshtein',
    ])
    inst.log(outcome, inst.currstep)
    inst.print_result(outcome, nocolor=True)

    # 1.3
    inst.step('download jtools', nocolor=True)
    chain = inst.chain([f'git clone https://github.com/umbral-tension/python-jtools {inst.appdir}/localjtools'])
    outcome = False
    if chain:
        shutil.move(f'{inst.appdir}/localjtools/src/jtools/jconsole.py', f'{inst.appdir}/jconsole.py')
        shutil.rmtree(f'{inst.appdir}/localjtools')
        import jconsole as jc
        outcome = True
    inst.print_result(outcome, nocolor=True)
    inst.log(outcome, inst.currstep)
   
    # 1.4

    # 2.1
    inst.step('download and install keyd')
    keyd_conf = opath.realpath(inst.appdir + '/../resources/configs/my_keyd.conf')
    inst.chain([f'git clone https://github.com/rvaiya/keyd {inst.appdir}/keyd'])
    os.chdir(f'{inst.appdir}/keyd')
    outcome = inst.chain([
        'make',
        'sudo make install',
        'sudo systemctl enable keyd',
        f'rm -rf {inst.appdir}/keyd',
        f'sudo cp {keyd_conf} /etc/keyd/default.conf'
        ])
    inst.log(outcome, inst.currstep)
    inst.print_result(outcome)
    os.chdir(inst.appdir)

