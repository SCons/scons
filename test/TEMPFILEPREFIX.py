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
Verify that setting the $TEMPFILEPREFIX variable will append to the
beginning of the TEMPFILE invocation of a long command line.
"""

import os
import stat

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

test.write('echo.py', """\
#!/usr/bin/env python
import sys
print sys.argv
""")

echo_py = test.workpath('echo.py')

st = os.stat(echo_py)
os.chmod(echo_py, st[stat.ST_MODE]|0111)

test.write('SConstruct', """
import os
env = Environment(
    BUILDCOM = '${TEMPFILE("xxx.py $TARGET $SOURCES")}',
    MAXLINELENGTH = 16,
    TEMPFILEPREFIX = '-via',
)
env.AppendENVPath('PATH', os.curdir)
env.Command('foo.out', 'foo.in', '$BUILDCOM')
""")

test.write('foo.in', "foo.in\n")

test.run(arguments = '-n -Q .',
         stdout = """\
Using tempfile \\S+ for command line:
xxx.py foo.out foo.in
xxx.py -via\\S+
""")

test.pass_test()
