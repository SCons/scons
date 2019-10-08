#!/usr/bin/env python
#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Verify that use of a Scanner that searches a *PATH list doesn't create
nodes for directories that don't exist, so they don't get picked up
by DirScanner.

Under the covers, this tests the behavior of the SCons.Node.FS.find_file()
utility function that is used by the Scanner.Classic class to search
directories in variables such as $CPPPATH.
"""

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

subdir_SConscript = os.path.join('subdir', 'SConscript')
subdir_foo        = os.path.join('subdir', 'foo')
subdir_foo_k      = os.path.join('subdir', 'foo.k')

test.subdir('subdir', 'inc1', 'inc2')

inc2_include_h = test.workpath('inc2', 'include.h')

test.write('build.py', r"""
import os.path
import sys
path = sys.argv[1].split()

def find_file(f):
    if os.path.isabs(f):
        return open(f, 'r')
    for dir in path:
        p = dir + os.sep + f
        if os.path.exists(p):
            return open(p, 'r')
    return None

def process(infp, outfp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            fname = line[8:-1]
            with find_file(fname) as f:
                process(f, outfp)
        else:
            outfp.write(line)

with open(sys.argv[2], 'r') as ifp, open(sys.argv[3], 'w') as ofp:
    process(ifp, ofp)

sys.exit(0)
""")

test.write('SConstruct', """\
def foo(target, source, env):
    fp = open(str(target[0]), 'w')
    for c in sorted(source[0].children(), key=lambda t: t.name):
        fp.write('%s\\n' % c)
    fp.close()
Command('list.out', 'subdir', foo, source_scanner = DirScanner)
SConscript('subdir/SConscript')
""")

test.write(['subdir', 'SConscript'], r"""
import SCons.Scanner
kscan = SCons.Scanner.Classic(name = 'kfile',
                              suffixes = ['.k'],
                              path_variable = 'KPATH',
                              regex = r'^include\s+(\S+)$')

env = Environment(KPATH=['.', '..'])
env.Append(SCANNERS = kscan)

env.Command('foo', 'foo.k', r'%(_python_)s build.py "$KPATH" $SOURCES $TARGET')
""" % locals())

test.write(['subdir', 'foo.k'], """\
subdir/foo.k
include inc1/include.h
include %(inc2_include_h)s
""" % locals())

test.write(['inc1', 'include.h'], """\
inc1/include.h
""")

test.write(['inc2', 'include.h'], """\
inc2/include.h
""")

test.run(arguments = '.')

test.must_match('subdir/foo', """\
subdir/foo.k
inc1/include.h
inc2/include.h
""", mode='r')

test.must_match('list.out', """\
%(subdir_SConscript)s
%(subdir_foo)s
%(subdir_foo_k)s
""" % locals(), mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
