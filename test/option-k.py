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

test.subdir('work1', 'work2', 'work3')



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


#
# Test: work1
# 

test.write(['work1', 'SConstruct'], """\
DefaultEnvironment(tools=[])
Succeed = Builder(action=r'%(_python_)s ../succeed.py $TARGETS')
Fail = Builder(action=r'%(_python_)s ../fail.py $TARGETS')
env = Environment(BUILDERS={'Succeed': Succeed, 'Fail': Fail}, tools=[])
env.Fail(target='aaa.1', source='aaa.in')
env.Succeed(target='aaa.out', source='aaa.1')
env.Succeed(target='bbb.out', source='bbb.in')
""" % locals())

test.write(['work1', 'aaa.in'], "aaa.in\n")
test.write(['work1', 'bbb.in'], "bbb.in\n")

test.run(chdir='work1',
         arguments='aaa.out bbb.out',
         stderr='scons: *** [aaa.1] Error 1\n',
         status=2)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_not_exist(test.workpath('work1', 'bbb.out'))

test.run(chdir='work1',
         arguments='-k aaa.out bbb.out',
         stderr='scons: *** [aaa.1] Error 1\n',
         status=2)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_match(['work1', 'bbb.out'], "succeed.py: bbb.out\n", mode='r')

test.unlink(['work1', 'bbb.out'])

test.run(chdir = 'work1',
         arguments='--keep-going aaa.out bbb.out',
         stderr='scons: *** [aaa.1] Error 1\n',
         status=2)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_match(['work1', 'bbb.out'], "succeed.py: bbb.out\n", mode='r')

expect = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Cleaning targets ...
Removed bbb.out
scons: done cleaning targets.
"""

test.run(chdir='work1',
         arguments='--clean --keep-going aaa.out bbb.out',
         stdout=expect)

test.must_not_exist(test.workpath('work1', 'aaa.1'))
test.must_not_exist(test.workpath('work1', 'aaa.out'))
test.must_not_exist(test.workpath('work1', 'bbb.out'))



#
# Test: work2
# 

test.write(['work2', 'SConstruct'], """\
DefaultEnvironment(tools=[])
Succeed = Builder(action=r'%(_python_)s ../succeed.py $TARGETS')
Fail = Builder(action=r'%(_python_)s ../fail.py $TARGETS')
env = Environment(BUILDERS={'Succeed': Succeed, 'Fail': Fail}, tools=[])
env.Fail('aaa.out', 'aaa.in')
env.Succeed('bbb.out', 'aaa.out')
env.Succeed('ccc.out', 'ccc.in')
env.Succeed('ddd.out', 'ccc.in')
""" % locals())

test.write(['work2', 'aaa.in'], "aaa.in\n")
test.write(['work2', 'ccc.in'], "ccc.in\n")

test.run(chdir='work2',
         arguments='-k .',
         status=2,
         stderr=None,
         stdout="""\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
%(_python_)s ../fail.py aaa.out
%(_python_)s ../succeed.py ccc.out
%(_python_)s ../succeed.py ddd.out
scons: done building targets (errors occurred during build).
""" % locals())

test.must_not_exist(['work2', 'aaa.out'])
test.must_not_exist(['work2', 'bbb.out'])
test.must_match(['work2', 'ccc.out'], "succeed.py: ccc.out\n", mode='r')
test.must_match(['work2', 'ddd.out'], "succeed.py: ddd.out\n", mode='r')



#
# Test: work3
#
# Check that the -k (keep-going) switch works correctly when the Nodes
# forms a DAG. The test case is the following
#
#               all
#                |
#          +-----+-----+-------------+
#          |           |             |
#         a1           a2           a3
#          |           |             |
#          +       +---+---+     +---+---+ 
#          \       |      /      |       |
#           \   bbb.out  /      a4    ccc.out
#            \          /       /        
#             \        /       /  
#              \      /       /  
#              aaa.out (fails)
#

test.write(['work3', 'SConstruct'], """\
DefaultEnvironment(tools=[])
Succeed = Builder(action = r'%(_python_)s ../succeed.py $TARGETS')
Fail = Builder(action = r'%(_python_)s ../fail.py $TARGETS')
env = Environment(BUILDERS = {'Succeed': Succeed, 'Fail': Fail}, tools=[])
a = env.Fail('aaa.out', 'aaa.in')
b = env.Succeed('bbb.out', 'bbb.in')
c = env.Succeed('ccc.out', 'ccc.in')

a1 = Alias( 'a1', a )
a2 = Alias( 'a2', a+b) 
a4 = Alias( 'a4', c) 
a3 = Alias( 'a3', a4+c) 

Alias('all', a1+a2+a3)
""" % locals())

test.write(['work3', 'aaa.in'], "aaa.in\n")
test.write(['work3', 'bbb.in'], "bbb.in\n")
test.write(['work3', 'ccc.in'], "ccc.in\n")


# Test tegular build (i.e. without -k)
test.run(chdir = 'work3',
         arguments = '.',
         status = 2,
         stderr = None,
         stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
%(_python_)s ../fail.py aaa.out
scons: building terminated because of errors.
""" % locals())

test.must_not_exist(['work3', 'aaa.out'])
test.must_not_exist(['work3', 'bbb.out'])
test.must_not_exist(['work3', 'ccc.out'])


test.run(chdir = 'work3',
         arguments = '-c .')
test.must_not_exist(['work3', 'aaa.out'])
test.must_not_exist(['work3', 'bbb.out'])
test.must_not_exist(['work3', 'ccc.out'])


# Current directory
test.run(chdir = 'work3',
         arguments = '-k .',
         status = 2,
         stderr = None,
         stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
%(_python_)s ../fail.py aaa.out
%(_python_)s ../succeed.py bbb.out
%(_python_)s ../succeed.py ccc.out
scons: done building targets (errors occurred during build).
""" % locals())

test.must_not_exist(['work3', 'aaa.out'])
test.must_exist(['work3', 'bbb.out'])
test.must_exist(['work3', 'ccc.out'])


test.run(chdir = 'work3',
         arguments = '-c .')
test.must_not_exist(['work3', 'aaa.out'])
test.must_not_exist(['work3', 'bbb.out'])
test.must_not_exist(['work3', 'ccc.out'])


# Single target
test.run(chdir = 'work3',
         arguments = '--keep-going all',
         status = 2,
         stderr = None,
         stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
%(_python_)s ../fail.py aaa.out
%(_python_)s ../succeed.py bbb.out
%(_python_)s ../succeed.py ccc.out
scons: done building targets (errors occurred during build).
""" % locals())

test.must_not_exist(['work3', 'aaa.out'])
test.must_exist(['work3', 'bbb.out'])
test.must_exist(['work3', 'ccc.out'])


test.run(chdir = 'work3',
         arguments = '-c .')
test.must_not_exist(['work3', 'aaa.out'])
test.must_not_exist(['work3', 'bbb.out'])
test.must_not_exist(['work3', 'ccc.out'])


# Separate top-level targets
test.run(chdir = 'work3',
         arguments = '-k a1 a2 a3',
         status = 2,
         stderr = None,
         stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
%(_python_)s ../fail.py aaa.out
%(_python_)s ../succeed.py bbb.out
%(_python_)s ../succeed.py ccc.out
scons: done building targets (errors occurred during build).
""" % locals())

test.must_not_exist(['work3', 'aaa.out'])
test.must_exist(['work3', 'bbb.out'])
test.must_exist(['work3', 'ccc.out'])


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
