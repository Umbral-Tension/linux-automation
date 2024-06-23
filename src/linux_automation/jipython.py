#!/bin/python3
import os
from os import path as opath
from jtools.jconsole import test, ptest, zen
from math import sin, asin, cos, acos, tan, atan, sqrt, pow, pi, factorial


math_funcs = ['sin/asin', 'cos/acos', 'tan/atan', 'sqrt', 'pow', 'pi', 'factorial' ]

os.system('clear')
print('imported from os:\n\tos, os.path as opath')
print('imported from jtools.jconsole:\n\t test, ptest, zen')
print(f'imported from math: \n\t{math_funcs}')
