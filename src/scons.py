#!/usr/bin/env python

import getopt
import os.path
import string
import sys

opts, targets = getopt.getopt(sys.argv[1:], 'f:')

Scripts = []

for o, a in opts:
    if o == '-f': Scripts.append(a)

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
#	dirlist = dirlist + [scons]
#    dirlist = dirlist + [dir]
#
#sys.path = dirlist

from scons.Node.FS import init, Dir, File, lookup
from scons.Environment import Environment

init()



def Conscript(filename):
    Scripts.append(filename)



while Scripts:
    file, Scripts = Scripts[0], Scripts[1:]
    execfile(file)



for path in targets:
	target = lookup(File, path)
	target.build()
