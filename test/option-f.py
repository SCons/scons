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

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir')

subdir_BuildThis = os.path.join('subdir', 'Buildthis')

test.write('SConscript', """
import os
print("SConscript " + os.getcwd())
""")

test.write(subdir_BuildThis, """
import os
print("subdir/BuildThis "+ os.getcwd())
""")

test.write('Build2', """
import os
print("Build2 "+ os.getcwd())
""")

wpath = test.workpath()

test.run(arguments = '-f SConscript .',
         stdout = test.wrap_stdout(read_str = 'SConscript %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '-f %s .' % subdir_BuildThis,
         stdout = test.wrap_stdout(read_str = 'subdir/BuildThis %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--file=SConscript .',
         stdout = test.wrap_stdout(read_str = 'SConscript %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--file=%s .' % subdir_BuildThis,
         stdout = test.wrap_stdout(read_str = 'subdir/BuildThis %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--makefile=SConscript .',
         stdout = test.wrap_stdout(read_str = 'SConscript %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--makefile=%s .' % subdir_BuildThis,
         stdout = test.wrap_stdout(read_str = 'subdir/BuildThis %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--sconstruct=SConscript .',
         stdout = test.wrap_stdout(read_str = 'SConscript %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--sconstruct=%s .' % subdir_BuildThis,
         stdout = test.wrap_stdout(read_str = 'subdir/BuildThis %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '-f - .', stdin = """
import os
print("STDIN " + os.getcwd())
""",
         stdout = test.wrap_stdout(read_str = 'STDIN %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

expect = test.wrap_stdout(read_str = 'Build2 %s\nSConscript %s\n' % (wpath, wpath),
                          build_str = "scons: `.' is up to date.\n")
test.run(arguments = '-f Build2 -f SConscript .', stdout=expect)

test.run(arguments = '-f no_such_file .',
         stdout = test.wrap_stdout("scons: `.' is up to date.\n"),
         stderr = None)
expect = """
scons: warning: Calling missing SConscript without error is deprecated.
Transition by adding must_exist=0 to SConscript calls.
Missing SConscript 'no_such_file'"""
stderr = test.stderr()
test.must_contain_all(test.stderr(), expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
