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
Test the SPAWN construction variable.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
ofp = open(sys.argv[1], 'wb')
for s in sys.argv[2:]:
    ofp.write(open(s, 'rb').read())
ofp.close()
""")

test.write('SConstruct', """
import os
import string
def my_spawn(sh, escape, cmd, args, env):
    os.system(string.join(args + ['extra.txt']))
env = Environment(SPAWN = my_spawn)
env.Command('file.out', 'file.in', "%(python)s cat.py $TARGET $SOURCES")
env = Environment()
""" % locals())

test.write('file.in', "file.in\n")
test.write('extra.txt', "extra.txt\n")

test.run(arguments = '.')

test.must_match('file.out', "file.in\nextra.txt\n")

test.pass_test()
