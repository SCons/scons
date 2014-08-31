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
Ensures that the Tool gets initialized, even when jar is not directly
found via the PATH variable (issue #2730).
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('myjar.py', r"""
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == 'cf':
        out = args[1]
        args = args[1:]
    else:
        break
    args = args[1:]
outfile = open(out, 'wb')
for file in args:
    infile = open(file, 'rb')
    for l in infile.readlines():
        if l[:7] != '/*jar*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
import os
oldpath = os.environ.get('PATH','')
env = Environment(ENV = {'PATH' : ['.']})
env['ENV']['PATH'] = oldpath
env['JAR'] = r'%(_python_)s ./myjar.py'
env.Jar(target = 'test1.jar', source = 'test1.class')
""" % locals())

test.write('test1.class', """\
test1.class
/*jar*/
line 3
""")

test.run(arguments = '.', stderr = None)

test.must_exist('test1.jar')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
