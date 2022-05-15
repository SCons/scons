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
Test JavaH without calling the tool
Split from rest of test to allow these to run if real javah skipped.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('myjavah.py', r"""
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == '-d':
        outdir = args[1]
        args = args[1:]
    elif a == '-o':
        outfile = open(args[1], 'w')
        args = args[1:]
    elif a == '-classpath':
        args = args[1:]
    elif a == '-sourcepath':
        args = args[1:]
    else:
        break
    args = args[1:]
for file in args:
    infile = open(file, 'r')
    for l in infile.readlines():
        if l[:9] != '/*javah*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['javah'], JAVAH=r'%(_python_)s myjavah.py')
env.JavaH(target=File('test1.h'), source='test1.java')
""" % locals())

test.write('test1.java', """\
test1.java
/*javah*/
line 3
""")

test.run(arguments='.', stderr=None)
test.must_match('test1.h', "test1.java\nline 3\n", mode='r')

if os.path.normcase('.java') == os.path.normcase('.JAVA'):
    test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=['javah'], JAVAH=r'%(_python_)s myjavah.py')
env.JavaH(target=File('test2.h'), source='test2.JAVA')
""" % locals())

    test.write('test2.JAVA', """\
test2.JAVA
/*javah*/
line 3
""")

    test.run(arguments='.', stderr=None)
    test.must_match('test2.h', "test2.JAVA\nline 3\n", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
