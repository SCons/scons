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
Verify that calling normal Builders from an actual Configure
context environment works correctly.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mycommand.py', r"""
import sys
sys.stderr.write( 'Hello World on stderr\n' )
sys.stdout.write( 'Hello World on stdout\n' )
with open(sys.argv[1], 'w') as f:
    f.write( 'Hello World\n' )
""")

test.write('SConstruct', """\
env = Environment()
def CustomTest(*args):
    return 0
conf = env.Configure(custom_tests = {'MyTest' : CustomTest})
if not conf.MyTest():
    env.Command("hello", [], r'%(_python_)s mycommand.py $TARGET')
env = conf.Finish()
""" % locals())

test.run(stderr="Hello World on stderr\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
