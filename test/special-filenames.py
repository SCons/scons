#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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

import os
import string
import sys

import TestSCons

test = TestSCons.TestSCons()

file_names = [ 
    'File with spaces',
    'File"with"double"quotes',
    "File'with'single'quotes",
    "File\nwith\nnewlines",
    "File\\with\\backslashes",
    "File;with;semicolons",
    "File<with>redirect",
    "File|with|pipe",
    "File*with*asterisk",
    "File&with&ampersand",
    "File?with?question",
    "File\twith\ttab",
    "File$with$dollar",
    "Combination '\"\n\\;<>?|*\t&"
    ]

if os.name == 'nt':
    # Windows only supports spaces.
    file_names = file_names[0:1]

test.write("cat.py", """\
import sys
open(sys.argv[1], 'wb').write(open(sys.argv[2], 'rb').read())
""")

for fn in file_names:
    test.write(fn + '.in', fn + '\n')

def buildFileStr(fn):
    return "env.Build(source=r\"\"\"%s.in\"\"\", target=r\"\"\"%s.out\"\"\")" % ( fn, fn )

test.write("SConstruct", """
env=Environment(BUILDERS = {'Build' : Builder(action = '%s cat.py $TARGET $SOURCE')})

%s
""" % (TestSCons.python, string.join(map(buildFileStr, file_names), '\n')))

test.run(arguments='.')

for fn in file_names:
    test.fail_test(test.read(fn + '.out') != fn + '\n')

test.pass_test()
