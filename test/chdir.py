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

"""
Test that the chdir argument to Builder creation, Action creation,
Command() calls and execution work1s correctly.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('other1',
            'other2',
            'other3',
            'other4',
            'other5',
            'other6',
            'other7',
            'other8',
            'other9',
            'work1',
            ['work1', 'sub1'],
            ['work1', 'sub2'],
            ['work1', 'sub3'],
            ['work1', 'sub4'],
            ['work1', 'sub5'],
            ['work1', 'sub6'],
            ['work1', 'sub7'],
            ['work1', 'sub8'],
            ['work1', 'sub9'],
            ['work1', 'sub20'],
            ['work1', 'sub21'],
            ['work1', 'sub22'],
            ['work1', 'sub23'])

cat_py = test.workpath('cat.py')

other1 = test.workpath('other1')
other1_f11_out = test.workpath('other1', 'f11.out')
other1_f11_in = test.workpath('other1', 'f11.in')
other2 = test.workpath('other2')
other2_f12_out = test.workpath('other2', 'f12.out')
other2_f12_in = test.workpath('other2', 'f12.in')
other3 = test.workpath('other3')
other3_f13_out = test.workpath('other3', 'f13.out')
other3_f13_in = test.workpath('other3', 'f13.in')
other4 = test.workpath('other4')
other4_f14_out = test.workpath('other4', 'f14.out')
other4_f14_in = test.workpath('other4', 'f14.in')
other5 = test.workpath('other5')
other5_f15_out = test.workpath('other5', 'f15.out')
other5_f15_in = test.workpath('other5', 'f15.in')
other6 = test.workpath('other6')
other6_f16_out = test.workpath('other6', 'f16.out')
other6_f16_in = test.workpath('other6', 'f16.in')
other7 = test.workpath('other7')
other7_f17_out = test.workpath('other7', 'f17.out')
other7_f17_in = test.workpath('other7', 'f17.in')
other8 = test.workpath('other8')
other8_f18_out = test.workpath('other8', 'f18.out')
other8_f18_in = test.workpath('other8', 'f18.in')
other9 = test.workpath('other9')
other9_f19_out = test.workpath('other9', 'f19.out')
other9_f19_in = test.workpath('other9', 'f19.in')

test.write(cat_py, """\
import sys
with open(sys.argv[1], 'wb') as ofp:
    for f in sys.argv[2:]:
        with open(f, 'rb') as ifp:
            ofp.write(ifp.read())
""")

test.write(['work1', 'SConstruct'], """
cat_command = r'%(_python_)s %(cat_py)s ${TARGET.file} ${SOURCE.file}'

no_chdir_act = Action(cat_command)
chdir_sub4_act = Action(cat_command, chdir=1)
chdir_sub5_act = Action(cat_command, chdir='sub5')
chdir_sub6_act = Action(cat_command, chdir=Dir('sub6'))

env = Environment(BUILDERS = {
    'Chdir4' : Builder(action = chdir_sub4_act),
    'Chdir5' : Builder(action = chdir_sub5_act),
    'Chdir6' : Builder(action = chdir_sub6_act),
    'Chdir7' : Builder(action = no_chdir_act, chdir=1),
    'Chdir8' : Builder(action = no_chdir_act, chdir='sub8'),
    'Chdir9' : Builder(action = no_chdir_act, chdir=Dir('sub9')),
})

env.Command('f0.out', 'f0.in', cat_command)

env.Command('sub1/f1.out', 'sub1/f1.in', cat_command,
            chdir=1)
env.Command('sub2/f2.out', 'sub2/f2.in', cat_command,
            chdir='sub2')
env.Command('sub3/f3.out', 'sub3/f3.in', cat_command,
            chdir=Dir('sub3'))

env.Chdir4('sub4/f4.out', 'sub4/f4.in')
env.Chdir5('sub5/f5.out', 'sub5/f5.in')
env.Chdir6('sub6/f6.out', 'sub6/f6.in')

env.Chdir7('sub7/f7.out', 'sub7/f7.in')
env.Chdir8('sub8/f8.out', 'sub8/f8.in')
env.Chdir9('sub9/f9.out', 'sub9/f9.in')

env.Command(r'%(other1_f11_out)s', r'%(other1_f11_in)s', cat_command,
            chdir=1)
env.Command(r'%(other2_f12_out)s', r'%(other2_f12_in)s', cat_command,
            chdir=r'%(other2)s')
env.Command(r'%(other3_f13_out)s', r'%(other3_f13_in)s', cat_command,
            chdir=Dir(r'%(other3)s'))

env.Chdir4(r'%(other4_f14_out)s', r'%(other4_f14_in)s')
env.Chdir5(r'%(other5_f15_out)s', r'%(other5_f15_in)s',
           chdir=r'%(other5)s')
env.Chdir6(r'%(other6_f16_out)s', r'%(other6_f16_in)s',
           chdir=Dir(r'%(other6)s'))

env.Chdir7(r'%(other7_f17_out)s', r'%(other7_f17_in)s')
env.Chdir8(r'%(other8_f18_out)s', r'%(other8_f18_in)s',
           chdir=r'%(other8)s')
env.Chdir9(r'%(other9_f19_out)s', r'%(other9_f19_in)s',
           chdir=Dir(r'%(other9)s'))

Command('f20.out', 'f20.in', cat_command)

Command('sub21/f21.out', 'sub21/f21.in', cat_command,
        chdir=1)
Command('sub22/f22.out', 'sub22/f22.in', cat_command,
        chdir='sub22')
Command('sub23/f23.out', 'sub23/f23.in', cat_command,
        chdir=Dir('sub23'))
""" % locals())

test.write(['work1', 'f0.in'], "work1/f0.in\n")

test.write(['work1', 'sub1', 'f1.in'], "work1/sub1/f1.in\n")
test.write(['work1', 'sub2', 'f2.in'], "work1/sub2/f2.in\n")
test.write(['work1', 'sub3', 'f3.in'], "work1/sub3/f3.in\n")
test.write(['work1', 'sub4', 'f4.in'], "work1/sub4/f4.in\n")
test.write(['work1', 'sub5', 'f5.in'], "work1/sub5/f5.in\n")
test.write(['work1', 'sub6', 'f6.in'], "work1/sub6/f6.in\n")
test.write(['work1', 'sub7', 'f7.in'], "work1/sub7/f7.in\n")
test.write(['work1', 'sub8', 'f8.in'], "work1/sub8/f8.in\n")
test.write(['work1', 'sub9', 'f9.in'], "work1/sub9/f9.in\n")

test.write(['other1', 'f11.in'], "other1/f11.in\n")
test.write(['other2', 'f12.in'], "other2/f12.in\n")
test.write(['other3', 'f13.in'], "other3/f13.in\n")
test.write(['other4', 'f14.in'], "other4/f14.in\n")
test.write(['other5', 'f15.in'], "other5/f15.in\n")
test.write(['other6', 'f16.in'], "other6/f16.in\n")
test.write(['other7', 'f17.in'], "other7/f17.in\n")
test.write(['other8', 'f18.in'], "other8/f18.in\n")
test.write(['other9', 'f19.in'], "other9/f19.in\n")

test.write(['work1', 'f20.in'], "work1/f20.in\n")

test.write(['work1', 'sub21', 'f21.in'], "work1/sub21/f21.in\n")
test.write(['work1', 'sub22', 'f22.in'], "work1/sub22/f22.in\n")
test.write(['work1', 'sub23', 'f23.in'], "work1/sub23/f23.in\n")

test.run(chdir='work1', arguments='..')

test.must_match(['work1', 'f0.out'], "work1/f0.in\n")

test.must_match(['work1', 'sub1', 'f1.out'], "work1/sub1/f1.in\n")
test.must_match(['work1', 'sub2', 'f2.out'], "work1/sub2/f2.in\n")
test.must_match(['work1', 'sub3', 'f3.out'], "work1/sub3/f3.in\n")
test.must_match(['work1', 'sub4', 'f4.out'], "work1/sub4/f4.in\n")
test.must_match(['work1', 'sub5', 'f5.out'], "work1/sub5/f5.in\n")
test.must_match(['work1', 'sub6', 'f6.out'], "work1/sub6/f6.in\n")
test.must_match(['work1', 'sub7', 'f7.out'], "work1/sub7/f7.in\n")
test.must_match(['work1', 'sub8', 'f8.out'], "work1/sub8/f8.in\n")
test.must_match(['work1', 'sub9', 'f9.out'], "work1/sub9/f9.in\n")

test.must_match(['other1', 'f11.out'], "other1/f11.in\n")
test.must_match(['other2', 'f12.out'], "other2/f12.in\n")
test.must_match(['other3', 'f13.out'], "other3/f13.in\n")
test.must_match(['other4', 'f14.out'], "other4/f14.in\n")
test.must_match(['other5', 'f15.out'], "other5/f15.in\n")
test.must_match(['other6', 'f16.out'], "other6/f16.in\n")
test.must_match(['other7', 'f17.out'], "other7/f17.in\n")
test.must_match(['other8', 'f18.out'], "other8/f18.in\n")
test.must_match(['other9', 'f19.out'], "other9/f19.in\n")

test.must_match(['work1', 'f20.out'], "work1/f20.in\n")

test.must_match(['work1', 'sub21', 'f21.out'], "work1/sub21/f21.in\n")
test.must_match(['work1', 'sub22', 'f22.out'], "work1/sub22/f22.in\n")
test.must_match(['work1', 'sub23', 'f23.out'], "work1/sub23/f23.in\n")



test.subdir('work2',
            ['work2', 'sub'])

work2 = repr(test.workpath('work2'))
work2_sub_f1_out = test.workpath('work2', 'sub', 'f1.out')
work2_sub_f2_out = test.workpath('work2', 'sub', 'f2.out')

test.write(['work2', 'SConstruct'], """\
cat_command = r'%(_python_)s %(cat_py)s ${TARGET.file} ${SOURCE.file}'
env = Environment()
env.Command('sub/f1.out', 'sub/f1.in', cat_command,
            chdir=1)
env.Command('sub/f2.out', 'sub/f2.in',
            [
              r'%(_python_)s %(cat_py)s .temp ${SOURCE.file}',
              r'%(_python_)s %(cat_py)s ${TARGET.file} .temp',
            ],
            chdir=1)
""" % locals())

test.write(['work2', 'sub', 'f1.in'], "work2/sub/f1.in")
test.write(['work2', 'sub', 'f2.in'], "work2/sub/f2.in")

expect = test.wrap_stdout("""\
os.chdir('sub')
%(_python_)s %(cat_py)s f1.out f1.in
os.chdir(%(work2)s)
os.chdir('sub')
%(_python_)s %(cat_py)s .temp f2.in
os.chdir(%(work2)s)
os.chdir('sub')
%(_python_)s %(cat_py)s f2.out .temp
os.chdir(%(work2)s)
""" % locals())

test.run(chdir='work2', arguments='-n .', stdout=expect)

test.must_not_exist(work2_sub_f1_out)
test.must_not_exist(work2_sub_f2_out)

test.run(chdir='work2', arguments='.', stdout=expect)

test.must_match(work2_sub_f1_out, "work2/sub/f1.in")
test.must_match(work2_sub_f2_out, "work2/sub/f2.in")

test.run(chdir='work2', arguments='-c .')

test.must_not_exist(work2_sub_f1_out)
test.must_not_exist(work2_sub_f2_out)

test.run(chdir='work2', arguments='-s .', stdout="")

test.must_match(work2_sub_f1_out, "work2/sub/f1.in")
test.must_match(work2_sub_f2_out, "work2/sub/f2.in")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
