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
Test that the --debug=memory option works.
"""

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons()

try:
    import resource
except ImportError:
    print "Python version has no `resource' module;"
    print "skipping test of --debug=memory."
    test.pass_test()



test.write('SConstruct', """
def cat(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
env = Environment(BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")



test.run(arguments = '--debug=memory')

lines = string.split(test.stdout(), '\n')

test.fail_test(re.match(r'Memory before reading SConscript files: +\d+', lines[-5]) is None)
test.fail_test(re.match(r'Memory after reading SConscript files: +\d+', lines[-4]) is None)
test.fail_test(re.match(r'Memory before building targets: +\d+', lines[-3]) is None)
test.fail_test(re.match(r'Memory after building targets: +\d+', lines[-2]) is None)



test.run(arguments = '-h --debug=memory')

lines = string.split(test.stdout(), '\n')

test.fail_test(re.match(r'Memory before reading SConscript files: +\d+', lines[-3]) is None)
test.fail_test(re.match(r'Memory after reading SConscript files: +\d+', lines[-2]) is None)



test.pass_test()
