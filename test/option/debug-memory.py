#!/usr/bin/env python
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
#

"""
Test that the --debug=memory option works.
"""

import re

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

if not IS_WINDOWS:
    try:
        import resource  # noqa: F401
    except ImportError:
        x = "Python version has no 'resource' skipping tests.\n"
        test.skip_test(x)


test.write('SConstruct', """
DefaultEnvironment(tools=[])
def cat(target, source, env):
    with open(str(target[0]), 'wb') as f, open(str(source[0]), 'rb') as ifp:
        f.write(ifp.read())
env = Environment(tools=[], BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")



test.run(arguments = '--debug=memory')

lines = test.stdout().split('\n')

test.fail_test(re.match(r'Memory before reading SConscript files: +\d+', lines[-5]) is None)
test.fail_test(re.match(r'Memory after reading SConscript files: +\d+', lines[-4]) is None)
test.fail_test(re.match(r'Memory before building targets: +\d+', lines[-3]) is None)
test.fail_test(re.match(r'Memory after building targets: +\d+', lines[-2]) is None)



test.run(arguments = '-h --debug=memory')

lines = test.stdout().split('\n')

test.fail_test(re.match(r'Memory before reading SConscript files: +\d+', lines[-3]) is None)
test.fail_test(re.match(r'Memory after reading SConscript files: +\d+', lines[-2]) is None)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
