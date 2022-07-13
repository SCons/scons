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

import re

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

SConstruct_path = test.workpath('SConstruct')

test.write(SConstruct_path, """\
def func(source = None, target = None, env = None):
    raise Exception("func exception")
B = Builder(action=func)
env = Environment(BUILDERS={'B': B})
env.B(target='foo.out', source='foo.in')
""")

test.write('foo.in', "foo.in\n")

expected_stderr = r"""scons: \*\*\* \[foo.out\] Exception : func exception
Traceback \(most recent call last\):
(  File ".+", line \d+, in \S+
    [^\n]+
    [^\n]+
)*(  File ".+", line \d+, in \S+
)*(  File ".+", line \d+, in \S+
    [^\n]+
)*  File "%s", line 2, in func
    raise Exception\("func exception"\)
Exception: func exception
""" % re.escape(SConstruct_path)

test.run(arguments="foo.out", stderr=expected_stderr, status=2)
test.run(arguments="-j2 foo.out", stderr=expected_stderr, status=2)

# Verify that exceptions caused by exit values of builder actions are
# correctly signalled, for both Serial and Parallel jobs.

test.write('myfail.py', r"""\
import sys
sys.exit(1)
""")

test.write(SConstruct_path, """
Fail = Builder(action=r'%(_python_)s myfail.py $TARGETS $SOURCE')
env = Environment(BUILDERS={'Fail': Fail})
env.Fail(target='out.f1', source='in.f1')
""" % locals())

test.write('in.f1', "in.f1\n")

expected_stderr = "scons: \\*\\*\\* \\[out.f1\\] Error 1\n"

test.run(arguments='.', status=2, stderr=expected_stderr)
test.run(arguments='-j2 .', status=2, stderr=expected_stderr)

# Verify that all exceptions from simultaneous tasks are reported,
# even if the exception is raised during the Task.prepare()
# [Node.prepare()]

test.write(SConstruct_path, """
Fail = Builder(action=r'%(_python_)s myfail.py $TARGETS $SOURCE')
env = Environment(BUILDERS={'Fail': Fail})
env.Fail(target='out.f1', source='in.f1')
env.Fail(target='out.f2', source='in.f2')
env.Fail(target='out.f3', source='in.f3')
""" % locals())

# in.f2 is not created to cause a Task.prepare exception
test.write('in.f1', 'in.f1\n')
test.write('in.f3', 'in.f3\n')

# In Serial task mode, get the first exception and stop
test.run(arguments='.', status=2, stderr=expected_stderr)

# In Parallel task mode, we will get all three exceptions.

expected_stderr_list = [
    "scons: *** [out.f1] Error 1\n",
    "scons: *** [out.f2] Source `in.f2' not found, needed by target `out.f2'.\n",
    "scons: *** [out.f3] Error 1\n",
]

# To get all three exceptions simultaneously, we execute -j7 to create
# one thread each for the SConstruct file and {in,out}.f[123].  Note that
# it's important that the input (source) files sort earlier alphabetically
# than the output files, so they're visited first in the dependency graph
# walk of '.' and are already considered up-to-date when we kick off the
# "simultaneous" builds of the output (target) files.

test.run(arguments='-j7 -k .', status=2, stderr=None)
test.must_contain_all_lines(test.stderr(), expected_stderr_list)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
