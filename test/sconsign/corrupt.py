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
Test that we get proper warnings when .sconsign* files are corrupt.
"""

import TestSCons
import TestCmd
import re

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.subdir('work1', ['work1', 'sub'],
            'work2', ['work2', 'sub'])

database_name = test.get_sconsignname()
database_filename = database_name + ".dblite"

# for test1 we're using the default database filename
work1__sconsign_dblite = test.workpath('work1', database_filename)
# for test 2 we have an explicit hardcode to .sconsign
work2_sub__sconsign = test.workpath('work2', 'sub', database_name)

SConstruct_contents = """\
def build1(target, source, env):
    with open(str(target[0]), 'wb') as ofp, open(str(source[0]), 'rb') as ifp:
        ofp.write(ifp.read())
    return None

B1 = Builder(action = build1)
env = Environment(BUILDERS = { 'B1' : B1})
env.B1(target = 'sub/foo.out', source = 'foo.in')
"""



test.write(['work1', 'SConstruct'], SConstruct_contents)

test.write(['work1', 'foo.in'], "work1/foo.in\n")

stderr = r'''
scons: warning: Ignoring corrupt .sconsign file: {}
.*
'''.format(re.escape(database_filename))

stdout = test.wrap_stdout(r'build1\(\["sub.foo\.out"\], \["foo\.in"\]\)' + '\n')

test.write(work1__sconsign_dblite, 'not:a:sconsign:file')
test.run(chdir='work1', arguments='.', stderr=stderr, stdout=stdout)

test.write(work1__sconsign_dblite, '\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
test.run(chdir='work1', arguments='.', stderr=stderr, stdout=stdout)



# Test explicitly using a .sconsign file in each directory.

SConstruct_contents = """\
SConsignFile(None)
""" + SConstruct_contents

test.write(['work2', 'SConstruct'], SConstruct_contents)

test.write(['work2', 'foo.in'], "work2/foo.in\n")

stderr = r'''
scons: warning: Ignoring corrupt .sconsign file: sub.{}
.*
'''.format(database_name)

stdout = test.wrap_stdout(r'build1\(\["sub.foo\.out"\], \["foo\.in"\]\)' + '\n')

test.write(work2_sub__sconsign, 'not:a:sconsign:file')
test.run(chdir='work2', arguments='.', stderr=stderr, stdout=stdout)

test.write(work2_sub__sconsign, '\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
test.run(chdir='work2', arguments='.', stderr=stderr, stdout=stdout)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
