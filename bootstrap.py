"""bootstrap.py

This is an Aegis-to-SCons build script that collects a copy of the
current SCons into a bootstrap/ subdirectory and then executes it with
the supplied command-line options.

Right now, it only understands the SCons -Y option, which is the only
one currently used.  It collects the repositories specified by -Y and
searches them, in order, for the pieces of SCons to copy into the local
bootstrap/ subdirectory.

This is essentially a minimal build of SCons to bootstrap ourselves into
executing it for the full build of all the packages, as specified in our
local SConstruct file.

"""

#
# Copyright (c) 2001, 2002 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import os.path
import getopt
import string
import sys

search = ['.']

opts, args = getopt.getopt(sys.argv[1:], "Y:", [])

for o, a in opts:
    if o == '-Y':
        search.append(a)

def find(file, search=search):
    for dir in search:
        f = os.path.join(dir, file)
	if os.path.exists(f):
	    return os.path.normpath(f)
    sys.stderr.write("could not find `%s' in search path:\n" % file)
    sys.stderr.write("\t" + string.join(search, "\n\t") + "\n")
    sys.exit(2)

scons_py = os.path.join('src', 'script', 'scons.py')
src_engine = os.path.join('src', 'engine')
MANIFEST_in = find(os.path.join(src_engine, 'MANIFEST.in'))

files = [ scons_py ] + map(lambda x: os.path.join(src_engine, x[:-1]),
                           open(MANIFEST_in).readlines())

subdir = 'bootstrap'

for file in files:
    src = find(file)
    dst = os.path.join(subdir, file)
    dir, _ = os.path.split(dst)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    contents = open(src, 'rb').read()
    try: os.unlink(dst)
    except: pass
    open(dst, 'wb').write(contents)

args = [ sys.executable, os.path.join(subdir, scons_py) ] + sys.argv[1:]

sys.stdout.write(string.join(args, " ") + '\n')
sys.stdout.flush()

os.environ['SCONS_LIB_DIR'] = os.path.join(subdir, src_engine)

os.execve(sys.executable, args, os.environ)
