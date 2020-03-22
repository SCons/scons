#!/usr/bin/env python
#
# A quick script to unzip a .zip archive and put the files in a
# subdirectory that matches the basename of the .zip file.
#
# This is actually generic functionality, it's not SCons-specific, but
# I'm using this to make it more convenient to manage working on multiple
# changes on Windows, where I don't have access to my Aegis tools.
#
import getopt
import os.path
import sys
import zipfile

helpstr = """\
Usage: scons-unzip.py [-o outdir] zipfile
Options:
  -o DIR, --out DIR           Change output directory name to DIR
  -v, --verbose               Print file names when extracting
"""

opts, args = getopt.getopt(sys.argv[1:],
                           "o:v",
                           ['out=', 'verbose'])

outdir = None
printname = lambda x: x

for o, a in opts:
    if o == '-o' or o == '--out':
        outdir = a
    elif o == '-v' or o == '--verbose':
        def printname(x):
            print(x)

if len(args) != 1:
    sys.stderr.write("scons-unzip.py:  \n")
    sys.exit(1)

zf = zipfile.ZipFile(str(args[0]), 'r')

if outdir is None:
    outdir, _ = os.path.splitext(os.path.basename(args[0]))

def outname(n, outdir=outdir):
    l = []
    while True:
        n, tail = os.path.split(n)
        if not n:
            break
        l.append(tail)
    l.append(outdir)
    l.reverse()
    return os.path.join(*l)

for name in zf.namelist():
    dest = outname(name)
    dir = os.path.dirname(dest)
    try:
        os.makedirs(dir)
    except:
        pass
    printname(dest)
    # if the file exists, then delete it before writing
    # to it so that we don't end up trying to write to a symlink:
    if os.path.isfile(dest) or os.path.islink(dest):
        os.unlink(dest)
    if not os.path.isdir(dest):
        open(dest, 'w').write(zf.read(name))

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
