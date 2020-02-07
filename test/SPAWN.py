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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
with open(sys.argv[1], 'wb') as ofp:
    for s in sys.argv[2:]:
        with open(s, 'rb') as ifp:
            ofp.write(ifp.read())
""")

test.write('SConstruct', """
import subprocess
import sys

def my_spawn1(sh, escape, cmd, args, env):
    s = " ".join(args + ['extra1.txt'])
    cp = subprocess.run(s, shell=True)
    return cp.returncode

def my_spawn2(sh, escape, cmd, args, env):
    s = " ".join(args + ['extra2.txt'])
    cp = subprocess.run(s, shell=True)
    return cp.returncode

env = Environment(MY_SPAWN1 = my_spawn1,
                  MY_SPAWN2 = my_spawn2,
                  COMMAND = r'%(_python_)s cat.py $TARGET $SOURCES')
env1 = env.Clone(SPAWN = my_spawn1)
env1.Command('file1.out', 'file1.in', '$COMMAND')

env2 = env.Clone(SPAWN = '$MY_SPAWN2')
env2.Command('file2.out', 'file2.in', '$COMMAND')

env3 = env.Clone(SPAWN = '${USE_TWO and MY_SPAWN2 or MY_SPAWN1}')
env3.Command('file3.out', 'file3.in', '$COMMAND', USE_TWO=0)
env3.Command('file4.out', 'file4.in', '$COMMAND', USE_TWO=1)
""" % locals())

test.write('file1.in', "file1.in\n")
test.write('file2.in', "file2.in\n")
test.write('file3.in', "file3.in\n")
test.write('file4.in', "file4.in\n")
test.write('extra1.txt', "extra1.txt\n")
test.write('extra2.txt', "extra2.txt\n")

test.run(arguments = '.')

test.must_match('file1.out', "file1.in\nextra1.txt\n")
test.must_match('file2.out', "file2.in\nextra2.txt\n")
test.must_match('file3.out', "file3.in\nextra1.txt\n")
test.must_match('file4.out', "file4.in\nextra2.txt\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
