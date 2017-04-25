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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('succeed.py', r"""
import sys
file = open(sys.argv[1], 'w')
file.write("succeed.py: %s\n" % sys.argv[1])
file.close()
sys.exit(0)
""")

test.write('fail.py', r"""
import sys
sys.exit(1)
""")

test.write('SConstruct', """
Succeed = Builder(action = r'%(_python_)s succeed.py $TARGETS')
Fail = Builder(action = r'%(_python_)s fail.py $TARGETS')
env = Environment(BUILDERS = { 'Succeed' : Succeed, 'Fail' : Fail })
env.Fail(target = 'aaa.1', source = 'aaa.in')
env.Succeed(target = 'aaa.out', source = 'aaa.1')
env.Fail(target = 'bbb.1', source = 'bbb.in')
env.Succeed(target = 'bbb.out', source = 'bbb.1')
""" % locals())

test.write('aaa.in', "aaa.in\n")
test.write('bbb.in', "bbb.in\n")

test.run(arguments = 'aaa.1 aaa.out bbb.1 bbb.out',
         stderr = 'scons: *** [aaa.1] Error 1\n',
         status = 2)

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(os.path.exists(test.workpath('aaa.out')))
test.fail_test(os.path.exists(test.workpath('bbb.1')))
test.fail_test(os.path.exists(test.workpath('bbb.out')))

test.run(arguments = '-i aaa.1 aaa.out bbb.1 bbb.out',
         stderr =
         'scons: *** [aaa.1] Error 1\n'
         'scons: *** [bbb.1] Error 1\n')
         
test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(test.read('aaa.out',mode='r') != "succeed.py: aaa.out\n")
test.fail_test(os.path.exists(test.workpath('bbb.1')))
test.fail_test(test.read('bbb.out',mode='r') != "succeed.py: bbb.out\n")

test.unlink("aaa.out")
test.unlink("bbb.out")

test.run(arguments='--ignore-errors aaa.1 aaa.out bbb.1 bbb.out',
         stderr='scons: *** [aaa.1] Error 1\n'
         'scons: *** [bbb.1] Error 1\n')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(test.read('aaa.out', mode='r') != "succeed.py: aaa.out\n")
test.fail_test(os.path.exists(test.workpath('bbb.1')))
test.fail_test(test.read('bbb.out', mode='r') != "succeed.py: bbb.out\n")

test.pass_test()
 

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
