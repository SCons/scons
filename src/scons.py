#!/usr/bin/env python

import getopt
import os.path
import string
import sys

def PrintUsage():
    print "Usage: scons [OPTION]... TARGET..."
    print "Build TARGET or multiple TARGET(s)"
    print " "
    print '  -f CONSCRIPT        execute CONSCRIPT instead of "SConstruct"'
    print "  -j N                execute N parallel jobs"
    print "  --help              print this message and exit"

try:
    opts, targets = getopt.getopt(sys.argv[1:], 'f:j:', ['help'])
except getopt.GetoptError, x:
    print x
    PrintUsage()
    sys.exit()

Scripts = []

num_jobs = 1
for o, a in opts:
    if o == '-f': Scripts.append(a)

    if o == '-j':
        try:
            num_jobs = int(a)
        except:
            PrintUsage()
            sys.exit(1)

        if num_jobs <= 0:
            PrintUsage()
            sys.exit(1)
            
    if o == '--help':
        PrintUsage()
        sys.exit(0)
    
if not Scripts:
    Scripts.append('SConstruct')


# XXX The commented-out code here adds any "scons" subdirs in anything
# along sys.path to sys.path.  This was an attempt at setting up things
# so we can import "node.FS" instead of "scons.Node.FS".  This doesn't
# quite fit our testing methodology, though, so save it for now until
# the right solutions pops up.
#
#dirlist = []
#for dir in sys.path:
#    scons = os.path.join(dir, 'scons')
#    if os.path.isdir(scons):
#     dirlist = dirlist + [scons]
#    dirlist = dirlist + [dir]
#
#sys.path = dirlist


from scons.Node.FS import init, Dir, File, lookup
from scons.Environment import Environment
import scons.Job
from scons.Builder import Builder

init()



def Conscript(filename):
    Scripts.append(filename)



while Scripts:
    file, Scripts = Scripts[0], Scripts[1:]
    execfile(file)



class Task:
    "this is here only until the build engine is implemented"

    def __init__(self, target):
        self.target = target

    def execute(self):
        self.target.build()



class Taskmaster:
    "this is here only until the build engine is implemented"

    def __init__(self, targets):
        self.targets = targets
        self.num_iterated = 0


    def next_task(self):
        if self.num_iterated == len(self.targets):
            return None
        else:
            current = self.num_iterated
            self.num_iterated = self.num_iterated + 1
            return Task(self.targets[current])

    def is_blocked(self):
        return 0

    def executed(self, task):
        pass



taskmaster = Taskmaster(map(lambda x: lookup(File, x), targets))

jobs = scons.Job.Jobs(num_jobs, taskmaster)
jobs.start()
jobs.wait()


