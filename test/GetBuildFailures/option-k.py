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

"""
Verify that a failed build action with -k works as expected.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_python_ = TestSCons._python_

try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

contents = r"""\
import sys
if 'mypass.py' in sys.argv[0]:
    with open(sys.argv[3], 'wb') as ofp, open(sys.argv[4], 'rb') as ifp:
        ofp.write(ifp.read())
    exit_value = 0
elif 'myfail.py' in sys.argv[0]:
    exit_value = 1
sys.exit(exit_value)
"""

test.write('mypass.py', contents)
test.write('myfail.py', contents)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
Command('f3', 'f3.in', r'@%(_python_)s mypass.py -  f3 $TARGET $SOURCE')
Command('f4', 'f4.in', r'@%(_python_)s myfail.py f3 f4 $TARGET $SOURCE')
Command('f5', 'f5.in', r'@%(_python_)s myfail.py f4 f5 $TARGET $SOURCE')
Command('f6', 'f6.in', r'@%(_python_)s mypass.py f5 -  $TARGET $SOURCE')

def print_build_failures():
    from SCons.Script import GetBuildFailures
    for bf in sorted(GetBuildFailures(), key=lambda a: a.filename or 'None'):
        print("%%s failed:  %%s" %% (bf.node, bf.errstr))

import atexit
atexit.register(print_build_failures)
""" % locals())

test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")

expect_stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
scons: done building targets (errors occurred during build).
f4 failed:  Error 1
f5 failed:  Error 1
""" % locals()

expect_stderr = """\
scons: *** [f4] Error 1
scons: *** [f5] Error 1
"""

test.run(arguments = '-k .', status = 2, stdout=None, stderr=None)
test.must_contain_exactly_lines(test.stdout(), expect_stdout, title='stdout')
test.must_contain_exactly_lines(test.stderr(), expect_stderr, title='stderr')

test.must_match(test.workpath('f3'), 'f3.in\n')
test.must_not_exist(test.workpath('f4'))
test.must_not_exist(test.workpath('f5'))
test.must_match(test.workpath('f6'), 'f6.in\n') 


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
