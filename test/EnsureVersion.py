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

import TestSCons

test = TestSCons.TestSCons()

import SCons

if SCons.__version__ == "__VERSION__":

    test.write('SConstruct', """
import sys
EnsurePythonVersion(0,0)
sys.exit(0)
""")

    test.run()

    test.write('SConstruct', """
import sys
EnsurePythonVersion(2000,0)
sys.exit(0)
""")

    test.run(status=2)

else:
    test.write('SConstruct', """
import sys
env = Environment()
EnsurePythonVersion(0,0)
env.EnsureSConsVersion(0,0)
sys.exit(0)
""")

    test.run()

    test.write('SConstruct', """
import sys
env = Environment()
env.EnsurePythonVersion(0,0)
EnsureSConsVersion(2000,0)
sys.exit(0)
""")

    test.run(status=2)

    test.write('SConstruct', """
import sys
EnsurePythonVersion(2000,0)
EnsureSConsVersion(2000,0)
sys.exit(0)
""")

    test.run(status=2)

test.write('SConstruct', """\
import sys
try:
    delattr(sys, 'version_info')
except AttributeError:
    pass
sys.version = '2.3b1 (#0, Feb 24 2003, 19:13:11)\\n'
EnsurePythonVersion(1,3)
sys.exit(0)
""")

test.run()

test.write('SConstruct', """\
import sys
try:
    delattr(sys, 'version_info')
except AttributeError:
    pass
sys.version = '2.3+ (#0, Feb 24 2003, 19:13:11)\\n'
EnsurePythonVersion(2,2)
sys.exit(0)
""")

test.run()

test.write('SConstruct', """\
import sys
try:
    delattr(sys, 'version_info')
except AttributeError:
    pass
sys.version = '2.3b1 (#0, Feb 24 2003, 19:13:11)\\n'
EnsurePythonVersion(2,3)
sys.exit(0)
""")

test.run()

test.write('SConstruct', """\
import sys
try:
    delattr(sys, 'version_info')
except AttributeError:
    pass
sys.version = '2.3b1 (#0, Feb 24 2003, 19:13:11)\\n'
EnsurePythonVersion(2,4)
sys.exit(0)
""")

test.run(status=2)



test.pass_test()
