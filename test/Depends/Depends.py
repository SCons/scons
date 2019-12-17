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
Verifies basic execution of the Depends() function.
"""

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('subdir', 'sub2')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp:
    for fname in sys.argv[2:]:
        with open(fname, 'rb') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""")

SUBDIR_foo_dep = os.path.join('$SUBDIR', 'foo.dep')
SUBDIR_f3_out = os.path.join('$SUBDIR', 'f3.out')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
Foo = Builder(action = r'%(_python_)s build.py $TARGET $SOURCES subdir/foo.dep')
Bar = Builder(action = r'%(_python_)s build.py $TARGET $SOURCES subdir/bar.dep')
env = Environment(tools=[], BUILDERS = { 'Foo' : Foo, 'Bar' : Bar }, SUBDIR='subdir')
env.Depends(target = ['f1.out', 'f2.out'], dependency = r'%(SUBDIR_foo_dep)s')
env.Depends(target = r'%(SUBDIR_f3_out)s', dependency = 'subdir/bar.dep')
env.Foo(target = 'f1.out', source = 'f1.in')
env.Foo(target = 'f2.out', source = 'f2.in')
env.Bar(target = 'subdir/f3.out', source = 'f3.in')
SConscript('subdir/SConscript', "env")
env.Foo(target = 'f5.out', source = 'f5.in')
env.Bar(target = 'sub2/f6.out', source = 'f6.in')
env.Depends(target = 'f5.out', dependency = 'sub2')
""" % locals())

test.write(['subdir', 'SConscript'], """
Import("env")
Depends(target = 'f4.out', dependency = 'bar.dep')
env.Bar(target = 'f4.out', source = 'f4.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write(['subdir', 'f4.in'], "subdir/f4.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")

test.write(['subdir', 'foo.dep'], "subdir/foo.dep 1\n")
test.write(['subdir', 'bar.dep'], "subdir/bar.dep 1\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1.in\nsubdir/foo.dep 1\n")
test.must_match('f2.out', "f2.in\nsubdir/foo.dep 1\n")
test.must_match(['subdir', 'f3.out'], "f3.in\nsubdir/bar.dep 1\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\nsubdir/bar.dep 1\n")
test.must_match('f5.out', "f5.in\nsubdir/foo.dep 1\n")
test.must_match(['sub2', 'f6.out'], "f6.in\nsubdir/bar.dep 1\n")

#
test.write(['subdir', 'foo.dep'], "subdir/foo.dep 2\n")
test.write(['subdir', 'bar.dep'], "subdir/bar.dep 2\n")
test.write('f6.in', "f6.in 2\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1.in\nsubdir/foo.dep 2\n")
test.must_match('f2.out', "f2.in\nsubdir/foo.dep 2\n")
test.must_match(['subdir', 'f3.out'], "f3.in\nsubdir/bar.dep 2\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\nsubdir/bar.dep 2\n")
test.must_match('f5.out', "f5.in\nsubdir/foo.dep 2\n")
test.must_match(['sub2', 'f6.out'], "f6.in 2\nsubdir/bar.dep 2\n")

#
test.write(['subdir', 'foo.dep'], "subdir/foo.dep 3\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1.in\nsubdir/foo.dep 3\n")
test.must_match('f2.out', "f2.in\nsubdir/foo.dep 3\n")
test.must_match(['subdir', 'f3.out'], "f3.in\nsubdir/bar.dep 2\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\nsubdir/bar.dep 2\n")
test.must_match('f5.out', "f5.in\nsubdir/foo.dep 2\n")
test.must_match(['sub2', 'f6.out'], "f6.in 2\nsubdir/bar.dep 2\n")

#
test.write(['subdir', 'bar.dep'], "subdir/bar.dep 3\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1.in\nsubdir/foo.dep 3\n")
test.must_match('f2.out', "f2.in\nsubdir/foo.dep 3\n")
test.must_match(['subdir', 'f3.out'], "f3.in\nsubdir/bar.dep 3\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\nsubdir/bar.dep 3\n")
test.must_match('f5.out', "f5.in\nsubdir/foo.dep 2\n")
test.must_match(['sub2', 'f6.out'], "f6.in 2\nsubdir/bar.dep 2\n")

#
test.write('f6.in', "f6.in 3\n")

test.run(arguments = '.')

test.must_match('f1.out', "f1.in\nsubdir/foo.dep 3\n")
test.must_match('f2.out', "f2.in\nsubdir/foo.dep 3\n")
test.must_match(['subdir', 'f3.out'], "f3.in\nsubdir/bar.dep 3\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\nsubdir/bar.dep 3\n")
test.must_match('f5.out', "f5.in\nsubdir/foo.dep 3\n")
test.must_match(['sub2', 'f6.out'], "f6.in 3\nsubdir/bar.dep 3\n")

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
