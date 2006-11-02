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

import os
import re
import string
import sys
import TestSCons
import TestCmd

_python_ = TestSCons._python_

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

SConstruct_path = test.workpath('SConstruct')

test.write(SConstruct_path, """\
def func(source = None, target = None, env = None):
    raise "func exception"
B = Builder(action = func)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""")

test.write('foo.in', "foo.in\n")

expected_stderr = """scons: \*\*\* \[foo.out\] Exception
Traceback \((most recent call|innermost) last\):
(  File ".+", line \d+, in \S+
    [^\n]+
)*(  File ".+", line \d+, in \S+
)*(  File ".+", line \d+, in \S+
    [^\n]+
)*  File "%s", line 2, in func
    raise "func exception"
func exception
""" % re.escape(SConstruct_path)

test.run(arguments = "foo.out", stderr = expected_stderr, status = 2)

test.run(arguments = "-j2 foo.out", stderr = expected_stderr, status = 2)


# Verify that exceptions caused by exit values of builder actions are
# correectly signalled, for both Serial and Parallel jobs.

test.write('myfail.py', r"""\
import sys
sys.exit(1)
""")

test.write(SConstruct_path, """
Fail = Builder(action = r'%(_python_)s myfail.py $TARGETS $SOURCE')
env = Environment(BUILDERS = { 'Fail' : Fail })
env.Fail(target = 'f1', source = 'f1.in')
""" % locals())

test.write('f1.in', "f1.in\n")

expected_stderr = "scons: \*\*\* \[f1\] Error 1\n"

test.run(arguments = '.', status = 2, stderr = expected_stderr)
test.run(arguments = '-j2 .', status = 2, stderr = expected_stderr)


# Verify that all exceptions from simultaneous tasks are reported,
# even if the exception is raised during the Task.prepare()
# [Node.prepare()]

test.write(SConstruct_path, """
Fail = Builder(action = r'%(_python_)s myfail.py $TARGETS $SOURCE')
env = Environment(BUILDERS = { 'Fail' : Fail })
env.Fail(target = 'f1', source = 'f1.in')
env.Fail(target = 'f2', source = 'f2.in')
env.Fail(target = 'f3', source = 'f3.in')
""" % locals())

# f2.in is not created to cause a Task.prepare exception
test.write('f3.in', 'f3.in\n')

# In Serial task mode, get the first exception and stop
test.run(arguments = '.', status = 2, stderr = expected_stderr)

# In Parallel task mode, we will get all three exceptions.

expected_stderr_list = [
  expected_stderr,
  "scons: \*\*\* Source `f2\.in' not found, needed by target `f2'\.  Stop\.\n",
  string.replace(expected_stderr, 'f1', 'f3')
  ]
  
# Unfortunately, we aren't guaranteed what order we will get the
# exceptions in...
orders = [ (1,2,3), (1,3,2), (2,1,3), (2,3,1), (3,1,2), (3,2,1) ]
otexts = []
for A,B,C in orders:
    otexts.append("%s%s%s"%(expected_stderr_list[A-1],
                            expected_stderr_list[B-1],
                            expected_stderr_list[C-1]))
                           
                      
expected_stderrs = "(" + string.join(otexts, "|") + ")"

test.run(arguments = '-j3 .', status = 2, stderr = expected_stderrs)


test.pass_test()
