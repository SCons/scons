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
Test that things still work when a .sconsign* file is not writable.
"""

import os
import TestSCons
import TestCmd
import pickle

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.subdir('work1',
            ['work1', 'sub1'],
            ['work1', 'sub2'],
            ['work1', 'sub3'],
            'work2',
            ['work2', 'sub1'],
            ['work2', 'sub2'],
            ['work2', 'sub3'])

database_name = test.get_sconsignname()
work1__sconsign_dblite = test.workpath('work1', database_name + '.dblite')
work2_sub1__sconsign = test.workpath('work2', 'sub1', database_name)
work2_sub2__sconsign = test.workpath('work2', 'sub2', database_name)
work2_sub3__sconsign = test.workpath('work2', 'sub3', database_name)

SConstruct_contents = """\
def build1(target, source, env):
    with open(str(target[0]), 'wb') as fo, open(str(source[0]), 'rb') as fi:
        fo.write(fi.read())
    return None

def build2(target, source, env):
    import os
    import os.path
    with open(str(target[0]), 'wb') as fo, open(str(source[0]), 'rb') as fi:
        fo.write(fi.read())
    dir, file = os.path.split(str(target[0]))
    os.chmod(dir, 0o555)
    return None

B1 = Builder(action = build1)
B2 = Builder(action = build2)
env = Environment(BUILDERS = { 'B1' : B1, 'B2' : B2 })
env.B1(target = 'sub1/foo.out', source = 'foo.in')
env.B2(target = 'sub2/foo.out', source = 'foo.in')
env.B2(target = 'sub3/foo.out', source = 'foo.in')
"""



test.write(['work1', 'SConstruct'], SConstruct_contents)

test.write(['work1', 'foo.in'], "work1/foo.in\n")

test.write(work1__sconsign_dblite, "")

os.chmod(work1__sconsign_dblite, 0o444)

test.run(chdir='work1', arguments='.')



SConstruct_contents = """\
SConsignFile(None)
""" + SConstruct_contents

test.write(['work2', 'SConstruct'], SConstruct_contents)

test.write(['work2', 'foo.in'], "work2/foo.in\n")

with open(work2_sub1__sconsign, 'wb') as p:
    pickle.dump({}, p, 1)
with open(work2_sub2__sconsign, 'wb') as p:
    pickle.dump({}, p, 1)

os.chmod(work2_sub1__sconsign, 0o444)

test.run(chdir='work2', arguments='.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
