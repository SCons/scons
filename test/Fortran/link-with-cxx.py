#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Verify the smart_link() warning messages used when attempting to link
C++ and Fortran object files, and the ability to suppress them with the
right --warn= options.
"""

import re

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons(match = TestSCons.match_re)


test.write('test_linker.py', """\
import sys

if sys.argv[1] == '-o':
    with open(sys.argv[2], 'wb') as ofp:
        for infile in sys.argv[3:]:
            with open(infile, 'rb') as ifp:
                ofp.write(ifp.read())
elif sys.argv[1][:5] == '/OUT:':
    with open(sys.argv[1][5:], 'wb') as ofp:
        for infile in sys.argv[2:]:
            with open(infile, 'rb') as ifp:
                ofp.write(ifp.read())
sys.exit(0)
""")

test.write('test_fortran.py', """\
import sys

with open(sys.argv[2], 'wb') as ofp:
    for infile in sys.argv[4:]:
        with open(infile, 'rb') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""")

test.write('SConstruct', """
import SCons.Tool.link

def copier(target, source, env):
    s = str(source[0])
    t = str(target[0])
    with open(t, 'wb') as ofp, open(s, 'rb') as ifp:
        ofp.write(ifp.read())

env = Environment(
    CXX=r'%(_python_)s test_linker.py',
    CXXCOM=Action(copier),
    SMARTLINK=SCons.Tool.link.smart_link,
    LINK=r'$SMARTLINK',
    LINKFLAGS='',
    # We want to re-define this as follows (so as to
    # not rely on a real Fortran compiler) but can't
    # because $FORTRANCOM is defined with an extra space
    # so it ends up as a CommandAction, not a LazyAction.
    # Must look into changing that after 1.0 is out.
    # FORTRANCOM = Action(copier))
    FORTRAN=r'%(_python_)s test_fortran.py',
)
env.Program('prog1.exe', ['f1.cpp', 'f2.f'])
env.Program('prog2.exe', ['f1.cpp', 'f2.f'])
if ARGUMENTS.get('NO_LINK'):
    SetOption('warn', ['no-link'])
if ARGUMENTS.get('NO_MIX'):
    SetOption('warn', ['no-fortran-cxx-mix'])
""" % locals())

test.write('f1.cpp', "f1.cpp\n")
test.write('f2.f', "f2.f\n")

expect = ("""
scons: warning: Using \\$CXX to link Fortran and C\\+\\+ code together.
    This may generate a buggy executable if the '%s test_linker.py'
    compiler does not know how to deal with Fortran runtimes.
""" % re.escape(_python_)) + TestSCons.file_expr

test.run(arguments = '.', stderr=expect)
test.must_match('prog1.exe', "f1.cpp\nf2.f\n")
test.must_match('prog2.exe', "f1.cpp\nf2.f\n")

test.run(arguments = '-c .', stderr=expect)
test.must_not_exist('prog1.exe')
test.must_not_exist('prog2.exe')

test.run(arguments = '--warning=no-link .')
test.must_match('prog1.exe', "f1.cpp\nf2.f\n")
test.must_match('prog2.exe', "f1.cpp\nf2.f\n")

test.run(arguments = '-c .', stderr=expect)
test.must_not_exist('prog1.exe')
test.must_not_exist('prog2.exe')

test.run(arguments = '--warning=no-fortran-cxx-mix .')
test.must_match('prog1.exe', "f1.cpp\nf2.f\n")
test.must_match('prog2.exe', "f1.cpp\nf2.f\n")

test.run(arguments = '-c .', stderr=expect)
test.must_not_exist('prog1.exe')
test.must_not_exist('prog2.exe')

test.run(arguments = 'NO_LINK=1 .')
test.must_match('prog1.exe', "f1.cpp\nf2.f\n")
test.must_match('prog2.exe', "f1.cpp\nf2.f\n")

test.run(arguments = '-c .', stderr=expect)
test.must_not_exist('prog1.exe')
test.must_not_exist('prog2.exe')

test.run(arguments = 'NO_MIX=1 .')
test.must_match('prog1.exe', "f1.cpp\nf2.f\n")
test.must_match('prog2.exe', "f1.cpp\nf2.f\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
