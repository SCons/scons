"""
Figure out paths in appveyor environment
"""
from __future__ import print_function
import os
import os.path

def check_dir(path):
    """ enumerate files/directories under path"""
    print(r'-- Directories under %s'%path)
    for item in os.listdir(path):
        print("Path->%s"%os.path.join(path, item))


PATHDIRS = os.environ['PATH'].split(os.pathsep)
for p in PATHDIRS:
    print("Path->%s"%p)

def find_file(filename):
    for p in PATHDIRS:
        if os.path.exists(os.path.join(p,filename)):
            print("Found %s in %s"%(filename, p))

# check_dir('c:\\')
# check_dir('C:/Program Files (x86)/')
# check_dir('C:/Program Files/')
#
# check_dir('C:/Program Files/LLVM/bin')
#
# check_dir('C:/msys64')

check_dir('C:/ProgramData/chocolatey/bin')
check_dir('C:/ProgramData/chocolatey/lib/swig/tools/install')


# check_dir('C:/Program Files/Git/usr/bin')
# find_file('xsltproc.exe')
# find_file('link.exe')
