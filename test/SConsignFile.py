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

import TestSCons
import os.path

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('work1', ['work1', 'subdir'])
test.subdir('work2', ['work2', 'subdir'])

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

#
test.write(['work1', 'SConstruct'], """
SConsignFile()
B = Builder(action = "%s ../build.py $TARGETS $SOURCES")
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
env.B(target = 'subdir/f3.out', source = 'subdir/f3.in')
env.B(target = 'subdir/f4.out', source = 'subdir/f4.in')
""" % python)

test.write(['work1', 'f1.in'], "work1/f1.in\n")
test.write(['work1', 'f2.in'], "work1/f2.in\n")
test.write(['work1', 'subdir', 'f3.in'], "work1/subdir/f3.in\n")
test.write(['work1', 'subdir', 'f4.in'], "work1/subdir/f4.in\n")

test.run(chdir = 'work1')

def any_dbm_file(prefix):
    return os.path.exists(prefix) \
           or os.path.exists(prefix + '.dat') \
           or os.path.exists(prefix + '.dir')

test.fail_test(not any_dbm_file(test.workpath('work1', '.sconsign.dbm')))
test.must_not_exist(test.workpath('work1', '.sconsign'))
test.must_not_exist(test.workpath('work1', 'subdir', '.sconsign'))
  
test.must_match(['work1', 'f1.out'], "work1/f1.in\n")
test.must_match(['work1', 'f2.out'], "work1/f2.in\n")
test.must_match(['work1', 'subdir', 'f3.out'], "work1/subdir/f3.in\n")
test.must_match(['work1', 'subdir', 'f4.out'], "work1/subdir/f4.in\n")

test.up_to_date(chdir = 'work1', arguments = '.')

test.fail_test(not any_dbm_file(test.workpath('work1', '.sconsign.dbm')))
test.must_not_exist(test.workpath('work1', '.sconsign'))
test.must_not_exist(test.workpath('work1', 'subdir', '.sconsign'))

#
test.write(['work2', 'SConstruct'], """
e = Environment(XXX = 'scons')
e.SConsignFile('my_${XXX}ign')
B = Builder(action = "%s ../build.py $TARGETS $SOURCES")
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'f5.out', source = 'f5.in')
env.B(target = 'f6.out', source = 'f6.in')
env.B(target = 'subdir/f7.out', source = 'subdir/f7.in')
env.B(target = 'subdir/f8.out', source = 'subdir/f8.in')
""" % python)

test.write(['work2', 'f5.in'], "work2/f5.in\n")
test.write(['work2', 'f6.in'], "work2/f6.in\n")
test.write(['work2', 'subdir', 'f7.in'], "work2/subdir/f7.in\n")
test.write(['work2', 'subdir', 'f8.in'], "work2/subdir/f8.in\n")

test.run(chdir = 'work2')

test.fail_test(not any_dbm_file(test.workpath('work2', 'my_sconsign')))
test.fail_test(any_dbm_file(test.workpath('work2', '.sconsign.dbm')))
test.must_not_exist(test.workpath('work2', '.sconsign'))
test.must_not_exist(test.workpath('work2', 'subdir', '.sconsign'))

test.must_match(['work2', 'f5.out'], "work2/f5.in\n")
test.must_match(['work2', 'f6.out'], "work2/f6.in\n")
test.must_match(['work2', 'subdir', 'f7.out'], "work2/subdir/f7.in\n")
test.must_match(['work2', 'subdir', 'f8.out'], "work2/subdir/f8.in\n")

test.up_to_date(chdir = 'work2', arguments = '.')

test.fail_test(not any_dbm_file(test.workpath('work2', 'my_sconsign')))
test.fail_test(any_dbm_file(test.workpath('work2', '.sconsign.dbm')))
test.must_not_exist(test.workpath('work2', '.sconsign'))
test.must_not_exist(test.workpath('work2', 'subdir', '.sconsign'))

test.pass_test()
