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
Test the SHELL construction variable.
"""

import os
import sys


import TestSCons

python = TestSCons.python
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

if sys.platform == 'win32':
    msg = 'Cannot set SHELL separately from other variables on Windows.\n'
    test.skip_test(msg)

my_shell = test.workpath('my_shell.py')

test.write(my_shell, """\
#!%(python)s
import os
import sys
cmd = sys.argv[2]
def stripquote(s):
    if s[0] == '"' and s[-1] == '"' or \
       s[0] == "'" and s[-1] == "'":
        s = s[1:-1]
    return s
args = stripquote(sys.argv[2]).split()
args = list(map(stripquote, args))
with open(args[2], 'wb') as ofp:
    for f in args[3:] + ['extra.txt']:
        with open(f, 'rb') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""" % locals())

os.chmod(my_shell, 0o755)

test.write('SConstruct', """\
env = Environment(SHELL = r'%(my_shell)s')
env.Command('file.out', 'file.in',
            'r%(_python_)s fake_cat_program $TARGET $SOURCES')
""" % locals())

test.write('file.in', "file.in\n")
test.write('extra.txt', "extra.txt\n")

test.run()

test.must_match('file.out', "file.in\nextra.txt\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
