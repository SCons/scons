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

import sys

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

# Writing this to accommodate both our in-line tool chain and the
# MSVC command lines is too hard, and will be completely unnecessary
# some day when we separate our tests.  Punt for now.
if sys.platform == 'win32':
    test.skip_test('Skipping on win32.\n')

if sys.platform == 'win32':
    test.file_fixture('mylink_win32.py', 'mylink.py')
else:
     test.file_fixture('mylink.py')

test.file_fixture('mygcc.py')


test.write('SConstruct', """
env = Environment(CPPFLAGS = '-x',
                  LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  CC = r'%(_python_)s mygcc.py cc',
                  CXX = r'%(_python_)s mygcc.py c++',
                  CXXFLAGS = [],
                  FORTRAN = r'%(_python_)s mygcc.py g77',
                  OBJSUFFIX = '.obj',
                  PROGSUFFIX = '.exe')
env.Program(target = 'foo', source = Split('test1.c test2.cpp test3.F'))
""" % locals())

test.write('test1.c', r"""test1.c
#cc
#link
""")

test.write('test2.cpp', r"""test2.cpp
#c++
#link
""")

test.write('test3.F', r"""test3.F
#g77
#link
""")

test.run(arguments = '.', stderr=None)

test.must_match('test1.obj', "test1.c\n#link\n")
test.must_match('test2.obj', "test2.cpp\n#link\n")
test.must_match('test3.obj', "test3.F\n#link\n")
test.must_match('foo.exe',   "test1.c\ntest2.cpp\ntest3.F\n")
if TestSCons.case_sensitive_suffixes('.F', '.f'):
    test.must_match('mygcc.out', "cc\nc++\ng77\n")
else:
    test.must_match('mygcc.out', "cc\nc++\n")   

test.write('SConstruct', """
env = Environment(CPPFLAGS = '-x',
                  SHLINK = r'%(_python_)s mylink.py',
                  SHLINKFLAGS = [],
                  CC = r'%(_python_)s mygcc.py cc',
                  CXX = r'%(_python_)s mygcc.py c++',
                  CXXFLAGS = [],
                  FORTRAN = r'%(_python_)s mygcc.py g77',
                  OBJSUFFIX = '.obj',
                  SHOBJPREFIX = '',
                  SHOBJSUFFIX = '.shobj',
                  PROGSUFFIX = '.exe')
env.SharedLibrary(target = File('foo.bar'),
                  source = Split('test1.c test2.cpp test3.F'))
""" % locals())

test.write('test1.c', r"""test1.c
#cc
#link
""")

test.write('test2.cpp', r"""test2.cpp
#c++
#link
""")

test.write('test3.F', r"""test3.F
#g77
#link
""")

test.unlink('mygcc.out')
test.unlink('test1.obj')
test.unlink('test2.obj')
test.unlink('test3.obj')

test.run(arguments = '.', stderr = None)

test.must_match('test1.shobj', "test1.c\n#link\n")
test.must_match('test2.shobj', "test2.cpp\n#link\n")
test.must_match('test3.shobj', "test3.F\n#link\n")
test.must_match('foo.bar',        "test1.c\ntest2.cpp\ntest3.F\n")
if TestSCons.case_sensitive_suffixes('.F', '.f'):
    test.must_match('mygcc.out', "cc\nc++\ng77\n")
else:
    test.must_match('mygcc.out', "cc\nc++\n")   

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
