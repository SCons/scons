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
import string
import sys
import TestCmd
import TestSCons

test = TestSCons.TestSCons()

no_such_file = test.workpath("no_such_file")
not_executable = test.workpath("not_executable")

test.write(not_executable, "\n")

test.write("f1.in", "\n")
test.write("f2.in", "\n")
test.write("f3.in", "\n")

test.write('SConstruct1', r"""
bld = Builder(action = '%s $SOURCES $TARGET')
env = Environment(BUILDERS = { 'bld' : bld })
env.bld(target = 'f1', source = 'f1.in')
""" % string.replace(no_such_file, '\\', '\\\\'))

test.run(arguments='-f SConstruct1 .',
	 stdout = test.wrap_stdout("%s f1.in f1\n" % no_such_file, error=1),
         stderr = None,
         status = 2)

bad_command = """\
Bad command or file name
"""

unrecognized = """\
'%s' is not recognized as an internal or external command,
operable program or batch file.
scons: *** [%s] Error 1
"""

unspecified = """\
The name specified is not recognized as an
internal or external command, operable program or batch file.
scons: *** [%s] Error 1
"""

not_found_1 = """
sh: %s: not found
scons: *** [%s] Error 1
"""

not_found_2 = """
sh: %s:  not found
scons: *** [%s] Error 1
"""

No_such = """\
%s: No such file or directory
scons: *** [%s] Error 127
"""

cannot_execute = """\
%s: cannot execute
scons *** [%s] Error 126
"""

Permission_denied = """\
%s: Permission denied
scons: *** [%s] Error 126
"""

permission_denied = """\
%s: permission denied
scons: *** [%s] Error 126
"""

is_a_directory = """\
%s: is a directory
scons: *** [%s] Error 126
"""

test.description_set("Incorrect STDERR:\n%s\n" % test.stderr())
if os.name == 'nt':
    errs = [
        bad_command,
        unrecognized % (no_such_file, 'f1'),
        unspecified % 'f1'
    ]
    test.fail_test(not test.stderr() in errs)
else:
    errs = [
        not_found_1 % (no_such_file, 'f1'),
        not_found_2 % (no_such_file, 'f1'),
        No_such % (no_such_file, 'f1'),
    ]
    error_message_not_found = 1
    for err in errs:
        if string.find(test.stderr(), err) != -1:
            error_message_not_found = None
            break
    test.fail_test(error_message_not_found)

test.write('SConstruct2', r"""
bld = Builder(action = '%s $SOURCES $TARGET')
env = Environment(BUILDERS = { 'bld': bld })
env.bld(target = 'f2', source = 'f2.in')
""" % string.replace(not_executable, '\\', '\\\\'))

test.run(arguments='-f SConstruct2 .',
	 stdout = test.wrap_stdout("%s f2.in f2\n" % not_executable, error=1),
         stderr = None,
         status = 2)

test.description_set("Incorrect STDERR:\n%s\n" % test.stderr())
if os.name == 'nt':
    errs = [
        bad_command,
        unrecognized % (not_executable, 'f2'),
        unspecified % 'f2'
    ]
    test.fail_test(not test.stderr() in errs)
else:
    errs = [
        cannot_execute % (not_executable, 'f2'),
        Permission_denied % (not_executable, 'f2'),
        permission_denied % (not_executable, 'f2'),
    ]
    error_message_not_found = 1
    for err in errs:
        if string.find(test.stderr(), err) != -1:
            error_message_not_found = None
            break
    test.fail_test(error_message_not_found)

test.write('SConstruct3', r"""
bld = Builder(action = '%s $SOURCES $TARGET')
env = Environment(BUILDERS = { 'bld' : bld })
env.bld(target = 'f3', source = 'f3.in')
""" % string.replace(test.workdir, '\\', '\\\\'))

test.run(arguments='-f SConstruct3 .',
	 stdout = test.wrap_stdout("%s f3.in f3\n" % test.workdir, error=1),
         stderr = None,
         status = 2)

test.description_set("Incorrect STDERR:\n%s\n" % test.stderr())
if os.name == 'nt':
    errs = [
        bad_command,
        unrecognized % (test.workdir, 'f3'),
        unspecified % 'f3'
    ]
    test.fail_test(not test.stderr() in errs)
else:
    errs = [
        cannot_execute % (not_executable, 'f3'),
        is_a_directory % (test.workdir, 'f3'),
    ]
    error_message_not_found = 1
    for err in errs:
        if string.find(test.stderr(), err) != -1:
            error_message_not_found = None
            break
    test.fail_test(error_message_not_found)

test.write('SConstruct4', r"""
env = Environment()
env.Command('test.out', 'test.in', Copy('$TARGET', '$SOURCE'))
env.InstallAs('test2.out', 'test.out')
# Mark test2.out as precious so we'll handle the exception in
# FunctionAction() rather than when the target is cleaned before building.
env.Precious('test2.out')
env.Default('test2.out')
""")

test.write('test.in', "test.in 1\n")

test.run(arguments = '-f SConstruct4 .')

test.write('test.in', "test.in 2\n")

test.writable('test2.out', 0)
f = open(test.workpath('test2.out'))

test.run(arguments = '-f SConstruct4 .',
         stderr = None,
         status = 2)

f.close()
test.writable('test2.out', 1)

test.description_set("Incorrect STDERR:\n%s" % test.stderr())
errs = [
    "scons: *** [test2.out] Permission denied\n",
    "scons: *** [test2.out] permission denied\n",
]
test.fail_test(test.stderr() not in errs)

test.pass_test()
