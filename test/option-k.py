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

import os.path
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('work1', 'work2')



test.write('succeed.py', r"""
import sys
file = open(sys.argv[1], 'wb')
file.write("succeed.py: %s\n" % sys.argv[1])
file.close()
sys.exit(0)
""")

test.write('fail.py', r"""
import sys
sys.exit(1)
""")

test.write(['work1', 'SConstruct'], """\
Succeed = Builder(action = r'%s ../succeed.py $TARGETS')
Fail = Builder(action = r'%s ../fail.py $TARGETS')
env = Environment(BUILDERS = { 'Succeed' : Succeed, 'Fail' : Fail })
env.Fail(target = 'aaa.1', source = 'aaa.in')
env.Succeed(target = 'aaa.out', source = 'aaa.1')
env.Succeed(target = 'bbb.out', source = 'bbb.in')
""" % (python, python))

test.write(['work1', 'aaa.in'], "aaa.in\n")
test.write(['work1', 'bbb.in'], "bbb.in\n")

test.run(chdir = 'work1',
         arguments = 'aaa.out bbb.out',
         stderr = 'scons: *** [aaa.1] Error 1\n',
         status = 2)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_not_exist(test.workpath('work1', 'bbb.out'))

test.run(chdir = 'work1',
         arguments = '-k aaa.out bbb.out',
         stderr = 'scons: *** [aaa.1] Error 1\n',
         status = 2)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_match(['work1', 'bbb.out'], "succeed.py: bbb.out\n")

test.unlink(['work1', 'bbb.out'])

test.run(chdir = 'work1',
         arguments = '--keep-going aaa.out bbb.out',
         stderr = 'scons: *** [aaa.1] Error 1\n',
         status = 2)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_match(['work1', 'bbb.out'], "succeed.py: bbb.out\n")



test.write(['work2', 'SConstruct'], """\
Succeed = Builder(action = r'%s ../succeed.py $TARGETS')
Fail = Builder(action = r'%s ../fail.py $TARGETS')
env = Environment(BUILDERS = { 'Succeed' : Succeed, 'Fail' : Fail })
env.Fail('aaa.out', 'aaa.in')
env.Succeed('bbb.out', 'aaa.out')
env.Succeed('ccc.out', 'ccc.in')
env.Succeed('ddd.out', 'ccc.in')
""" % (python, python))

test.write(['work2', 'aaa.in'], "aaa.in\n")
test.write(['work2', 'ccc.in'], "ccc.in\n")

test.run(chdir = 'work2',
         arguments = '-k .',
         status = 2,
         stderr = None,
         stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
%s ../fail.py aaa.out
%s ../succeed.py ccc.out
%s ../succeed.py ddd.out
scons: done building targets (errors occurred during build).
""" % (python, python, python))

test.must_not_exist(['work2', 'aaa.out'])
test.must_not_exist(['work2', 'bbb.out'])
test.must_match(['work2', 'ccc.out'], "succeed.py: ccc.out\n")
test.must_match(['work2', 'ddd.out'], "succeed.py: ddd.out\n")



test.pass_test()
