import json


from subprocess import run

try:
    print("here 1")
    run('ls fake')
    print("second")
except:
    pass
