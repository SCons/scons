#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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
This test verifies:
    1)  that we don't build files when we use the -n, --no-exec,
        --just-print, --dry-run, and --recon options;
    2)  that we don't remove built files when -n is used in
        conjunction with -c;
    3)  that files installed by the Install() method don't get
        installed when -n is used;
    4)  that source files don't get duplicated in a BuildDir
        when -n is used.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('build', 'src')

test.write('build.py', r"""
import sys
file = open(sys.argv[1], 'wb')
file.write("build.py: %s\n" % sys.argv[1])
file.close()
""")

test.write('SConstruct', """
MyBuild = Builder(action = r'%s build.py $TARGETS')
env = Environment(BUILDERS = { 'MyBuild' : MyBuild })
env.MyBuild(target = 'f1.out', source = 'f1.in')
env.MyBuild(target = 'f2.out', source = 'f2.in')
env.Install('install', 'f3.in')
BuildDir('build', 'src', duplicate=1)
SConscript('build/SConscript', "env")
""" % python)

test.write(['src', 'SConscript'], """
Import("env")
env.MyBuild(target = 'f4.out', source = 'f4.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write(['src', 'f4.in'], "src/f4.in\n")

args = 'f1.out f2.out'
expect = test.wrap_stdout("""\
%s build.py f1.out
%s build.py f2.out
""" % (python, python))

test.run(arguments = args, stdout = expect)
test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

test.unlink('f1.out')
test.unlink('f2.out')

test.run(arguments = '-n ' + args, stdout = expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments = '--no-exec ' + args, stdout = expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments = '--just-print ' + args, stdout = expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments = '--dry-run ' + args, stdout = expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments = '--recon ' + args, stdout = expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments = args)
test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

expect = test.wrap_stdout("Removed f1.out\nRemoved f2.out\n")

test.run(arguments = '-n -c ' + args, stdout = expect)

test.run(arguments = '-c -n ' + args, stdout = expect)

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

#
install_f3_in = os.path.join('install', 'f3.in')
expect = test.wrap_stdout('Install file: "f3.in" as "%s"\n' % install_f3_in)

test.run(arguments = '-n install', stdout = expect)
test.fail_test(os.path.exists(test.workpath('install', 'f3.in')))

test.run(arguments = 'install', stdout = expect)
test.fail_test(not os.path.exists(test.workpath('install', 'f3.in')))

test.write('f3.in', "f3.in again\n")

test.run(arguments = '-n install', stdout = expect)
test.fail_test(not os.path.exists(test.workpath('install', 'f3.in')))

# Make sure duplicate source files in a BuildDir aren't created
# when the -n option is used.
test.run(arguments = '-n build')
test.fail_test(os.path.exists(test.workpath('build', 'f4.in')))

test.pass_test()

