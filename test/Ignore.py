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

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('build.py', r"""
import sys
with open(sys.argv[2], 'rb') as afp2, open(sys.argv[3], 'rb') as afp3:
    contents = afp2.read() + afp3.read()
with open(sys.argv[1], 'wb') as f:
    for arg in sys.argv[2:]:
        with open(arg, 'rb') as ifp:
            f.write(ifp.read())
""")

SUBDIR_f3_out = os.path.join('$SUBDIR', 'f3.out')
SUBDIR_f3b_in = os.path.join('$SUBDIR', 'f3b.in')

test.write('SConstruct', """\
Foo = Builder(action = r'%(_python_)s build.py $TARGET $SOURCES')
Bar = Builder(action = r'%(_python_)s build.py $TARGET $SOURCES')
env = Environment(BUILDERS = { 'Foo' : Foo, 'Bar' : Bar }, SUBDIR='subdir')
env.Foo(target = 'f1.out', source = ['f1a.in', 'f1b.in'])
Ignore(target = 'f1.out', dependency = 'f1b.in')
SConscript('subdir/SConscript', "env")
env.Foo(target = 'subdir/f3.out', source = ['subdir/f3a.in', 'subdir/f3b.in'])
env.Ignore(target = r'%(SUBDIR_f3_out)s', dependency = r'%(SUBDIR_f3b_in)s')
""" % locals())

test.write(['subdir', 'SConscript'], """
Import("env")
env.Bar(target = 'f2.out', source = ['f2a.in', 'f2b.in'])
env.Ignore('f2.out', 'f2a.in')
""")

test.write('f1a.in', "f1a.in\n")
test.write('f1b.in', "f1b.in\n")

test.write(['subdir', 'f2a.in'], "subdir/f2a.in\n")
test.write(['subdir', 'f2b.in'], "subdir/f2b.in\n")

test.write(['subdir', 'f3a.in'], "subdir/f3a.in\n")
test.write(['subdir', 'f3b.in'], "subdir/f3b.in\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1a.in\nf1b.in\n")
test.must_match(['subdir', 'f2.out'], "subdir/f2a.in\nsubdir/f2b.in\n")
test.must_match(['subdir', 'f3.out'], "subdir/f3a.in\nsubdir/f3b.in\n")

test.up_to_date(arguments = '.')

test.write('f1b.in', "f1b.in 2\n")
test.write(['subdir', 'f2a.in'], "subdir/f2a.in 2\n")
test.write(['subdir', 'f3b.in'], "subdir/f3b.in 2\n")

test.up_to_date(arguments = '.')

test.must_match('f1.out', "f1a.in\nf1b.in\n")
test.must_match(['subdir', 'f2.out'], "subdir/f2a.in\nsubdir/f2b.in\n")
test.must_match(['subdir', 'f3.out'], "subdir/f3a.in\nsubdir/f3b.in\n")

test.write('f1a.in', "f1a.in 2\n")
test.write(['subdir', 'f2b.in'], "subdir/f2b.in 2\n")
test.write(['subdir', 'f3a.in'], "subdir/f3a.in 2\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1a.in 2\nf1b.in 2\n")
test.must_match(['subdir', 'f2.out'], "subdir/f2a.in 2\nsubdir/f2b.in 2\n")
test.must_match(['subdir', 'f3.out'], "subdir/f3a.in 2\nsubdir/f3b.in 2\n")

test.up_to_date(arguments = '.')

#
test.write('SConstruct', """\
env = Environment()
file1 = File('file1')
file2 = File('file2')
env.Ignore(file1, [[file2, 'file3']])
""")

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
