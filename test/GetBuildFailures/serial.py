#!/usr/bin/env python
#
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

"""
Verify that the GetBuildFailures() function returns a list of
BuildError exceptions.  Also verify printing the BuildError
attributes we expect to be most commonly used.
"""

import TestSCons
import re

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
Command('f03', 'f03.in', r'@%(_python_)s mypass.py -   f03 $TARGET $SOURCE')
Command('f04', 'f04.in', r'@%(_python_)s myfail.py f03 f04 $TARGET $SOURCE')
Command('f05', 'f05.in', r'@%(_python_)s myfail.py f04 f05 $TARGET $SOURCE')
Command('f06', 'f06.in', r'@%(_python_)s mypass.py f05 -   $TARGET $SOURCE')
Command('f07', 'f07.in', r'@%(_python_)s mypass.py f07 -   $TARGET $SOURCE')

import SCons.Errors
def raiseExcAction(exc):
    def action(env, target, source, exc=exc):
        raise exc
    return action
def returnExcAction(exc):
    def action(env, target, source, exc=exc):
        return exc
    return action
class MyBuildError(SCons.Errors.BuildError):
   pass

Command('f08', 'f08.in', raiseExcAction(SCons.Errors.UserError("My User Error")))
Command('f09', 'f09.in', returnExcAction(SCons.Errors.UserError("My User Error")))
Command('f10', 'f10.in', raiseExcAction(MyBuildError(errstr="My Build Error", status=7)))
Command('f11', 'f11.in', returnExcAction(MyBuildError(errstr="My Build Error", status=7)))
Command('f12', 'f12.in', raiseExcAction(OSError(123, "My SConsEnvironmentError", "f12")))
Command('f13', 'f13.in', returnExcAction(OSError(123, "My SConsEnvironmentError", "f13")))
Command('f14', 'f14.in', raiseExcAction(SCons.Errors.InternalError("My InternalError")))
Command('f15', 'f15.in', returnExcAction(SCons.Errors.InternalError("My InternalError")))

def print_build_failures():
    from SCons.Script import GetBuildFailures
    for bf in sorted(GetBuildFailures(), key=lambda t: str(t.node)):
        assert( isinstance(bf, SCons.Errors.BuildError) )
        print("BF: %%s failed (%%s):  %%s" %% (bf.node, bf.status, bf.errstr))
        if bf.command:
            print("BF:    %%s" %% " ".join(Flatten(bf.command)))

import atexit
atexit.register(print_build_failures)
""" % locals())

test.write('f03.in', "f03.in\n")
test.write('f04.in', "f04.in\n")
test.write('f05.in', "f05.in\n")
test.write('f06.in', "f06.in\n")
# f07.in is intentionally missing...
test.write('f08.in', "f08.in\n")
test.write('f09.in', "f09.in\n")
test.write('f10.in', "f10.in\n")
test.write('f11.in', "f11.in\n")
test.write('f12.in', "f12.in\n")
test.write('f13.in', "f13.in\n")
test.write('f14.in', "f14.in\n")
test.write('f15.in', "f15.in\n")

expect_stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
scons: building terminated because of errors.
BF: f04 failed (1):  Error 1
BF:    %(_python_)s myfail.py f03 f04 "f04" "f04.in"
""" % locals()

expect_stderr = """\
scons: *** [f04] Error 1
"""

test.run(arguments = '.',
         status = 2,
         stdout = expect_stdout,
         stderr = expect_stderr)

test.must_match(test.workpath('f03'), 'f03.in\n')
test.must_not_exist(test.workpath('f04'))
test.must_not_exist(test.workpath('f05'))
test.must_not_exist(test.workpath('f06'))
test.must_not_exist(test.workpath('f07'))
test.must_not_exist(test.workpath('f08'))
test.must_not_exist(test.workpath('f09'))
test.must_not_exist(test.workpath('f10'))
test.must_not_exist(test.workpath('f11'))
test.must_not_exist(test.workpath('f12'))
test.must_not_exist(test.workpath('f13'))
test.must_not_exist(test.workpath('f14'))
test.must_not_exist(test.workpath('f15'))


expect_stdout = re.escape("""\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
action(["f08"], ["f08.in"])
action(["f09"], ["f09.in"])
action(["f10"], ["f10.in"])
action(["f11"], ["f11.in"])
action(["f12"], ["f12.in"])
action(["f13"], ["f13.in"])
action(["f14"], ["f14.in"])
action(["f15"], ["f15.in"])
scons: done building targets (errors occurred during build).
BF: f04 failed (1):  Error 1
BF:    %(_python_)s myfail.py f03 f04 "f04" "f04.in"
BF: f05 failed (1):  Error 1
BF:    %(_python_)s myfail.py f04 f05 "f05" "f05.in"
BF: f07 failed (2):  Source `f07.in' not found, needed by target `f07'.
BF: f08 failed (2):  My User Error
BF:    action(["f08"], ["f08.in"])
BF: f09 failed (2):  My User Error
BF:    action(["f09"], ["f09.in"])
BF: f10 failed (7):  My Build Error
BF:    action(["f10"], ["f10.in"])
BF: f11 failed (7):  My Build Error
BF:    action(["f11"], ["f11.in"])
BF: f12 failed (123):  My SConsEnvironmentError
BF:    action(["f12"], ["f12.in"])
BF: f13 failed (123):  My SConsEnvironmentError
BF:    action(["f13"], ["f13.in"])
BF: f14 failed (2):  InternalError : My InternalError
BF:    action(["f14"], ["f14.in"])
BF: f15 failed (2):  InternalError : My InternalError
BF:    action(["f15"], ["f15.in"])
""" % locals())

expect_stderr = re.escape("""\
scons: *** [f04] Error 1
scons: *** [f05] Error 1
scons: *** [f07] Source `f07.in' not found, needed by target `f07'.
scons: *** [f08] My User Error
scons: *** [f09] My User Error
scons: *** [f10] My Build Error
scons: *** [f11] My Build Error
scons: *** [f12] f12: My SConsEnvironmentError
scons: *** [f13] f13: My SConsEnvironmentError
scons: *** [f14] InternalError : My InternalError
""") + \
r"""Traceback \(most recent call last\):
(  File ".+", line \d+, in \S+
    [^\n]+
)*(  File ".+", line \d+, in \S+
)*(  File ".+", line \d+, in \S+
    [^\n]+
)*\S.+
""" + \
re.escape("""\
scons: *** [f15] InternalError : My InternalError
""")

test.run(arguments = '-k .',
         status = 2,
         stdout = expect_stdout,
         stderr = expect_stderr,
         match = TestSCons.match_re_dotall)

test.must_match(test.workpath('f03'), 'f03.in\n')
test.must_not_exist(test.workpath('f04'))
test.must_not_exist(test.workpath('f05'))
test.must_match(test.workpath('f06'), 'f06.in\n')
test.must_not_exist(test.workpath('f07'))
test.must_not_exist(test.workpath('f08'))
test.must_not_exist(test.workpath('f09'))
test.must_not_exist(test.workpath('f10'))
test.must_not_exist(test.workpath('f11'))
test.must_not_exist(test.workpath('f12'))
test.must_not_exist(test.workpath('f13'))
test.must_not_exist(test.workpath('f14'))
test.must_not_exist(test.workpath('f15'))


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
