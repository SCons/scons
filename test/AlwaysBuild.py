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

test.subdir('sub')

sub_f3_out = os.path.join('sub', 'f3.out')
_SUBDIR_f3_out = os.path.join('$SUBDIR', 'f3.out')

test.write('SConstruct', """\
def bfunc(target, source, env):
    import shutil
    shutil.copyfile('f2.in', str(target[0]))

B = Builder(action=bfunc)
env = Environment(BUILDERS = { 'B' : B }, SUBDIR='sub')
env.B('f1.out', source='f1.in')
AlwaysBuild('f1.out')

env.B(r'%(sub_f3_out)s', source='f3.in')
env.AlwaysBuild(r'%(_SUBDIR_f3_out)s')

env.Alias('clean1', [], Delete('clean1-target'))
env.AlwaysBuild('clean1')
c2 = env.Alias('clean2', [], [Delete('clean2-t1'), Delete('clean2-t2')])
env.AlwaysBuild(c2)

def dir_build(target, source, env):
    with open('dir_build.txt', 'ab') as f:
        f.write(b'dir_build()\\n')
env.Command(Dir('dir'), None, dir_build)
env.AlwaysBuild('dir')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "1")
test.write('f3.in', "f3.in\n")

test.subdir('dir')

test.run(arguments = ".")
test.must_match('f1.out', '1')
test.must_match(['sub', 'f3.out'], '1')
test.must_match('dir_build.txt', "dir_build()\n")

test.write('f2.in', "2")

test.run(arguments = ".")
test.must_match('f1.out', '2')
test.must_match(['sub', 'f3.out'], '2')
test.must_match('dir_build.txt', "dir_build()\ndir_build()\n")

test.run(arguments = 'clean1', stdout=test.wrap_stdout("""\
Delete("clean1-target")
"""))

test.run(arguments = 'clean2', stdout=test.wrap_stdout("""\
Delete("clean2-t1")
Delete("clean2-t2")
"""))

test.not_up_to_date(arguments = 'dir')

test.must_match('dir_build.txt', "dir_build()\ndir_build()\ndir_build()\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
