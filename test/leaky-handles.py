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
Verify that file handles aren't leaked to child processes
"""

import sys

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'linux':
    msg = "Skipping fork leak test on non-linux platforms\n"
    test.skip_test(msg)

_python_ = TestSCons._python_

# Let the child process itself report any handle on /dev/null it inherited.
# Looking at '/proc/$$/fd' from a shell pipeline instead would be racy: $$ is
# the shell, whose handles transiently include the pipe ends it has not closed
# yet, so such a check intermittently sees one or two extra handles when the
# shell and the command contend for a cpu.
test.write('fdcheck.py', """\
import os

leaks = []
for name in os.listdir('/proc/self/fd'):
    try:
        target = os.readlink('/proc/self/fd/' + name)
    except OSError:  # handle already gone, e.g. the one os.listdir used
        continue
    if int(name) > 2 and target == '/dev/null':
        leaks.append(int(name))
print('leaked fds: %s' % sorted(leaks))
""")

test.write('SConstruct', """
import os

# Leave a file handle open when invoking a command. Two details matter here:
# an os-level handle is used because a file object bound to an SConscript
# global is garbage collected (and so closed) before the build phase runs,
# and it is marked inheritable because handles are close-on-exec by default
# since Python 3.4 (PEP 446) and so could not leak whatever SCons did.
leaked = os.open('/dev/null', os.O_RDONLY)
os.set_inheritable(leaked, True)

# Check it doesn't get passed on when an external command is forked off:
test2 = Command('test2', [], '@%(_python_)s fdcheck.py')
""" % locals())

test.run(arguments='-Q', stdout='leaked fds: []\n')

test.pass_test()
