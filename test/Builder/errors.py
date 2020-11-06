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
Test the ability to catch Builder creation with poorly specified Actions.
"""


import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

sconstruct = """
def buildop(env, source, target):
    with open(str(target[0]), 'wb') as outf, open(str(source[0]), 'r') as infp:
        for line in inpf.readlines():
            if line.find(str(target[0])) == -1:
                outf.write(line)
b1 = Builder(action=buildop, src_suffix='.a', suffix='.b')
%s
env=Environment(tools=[], BUILDERS={'b1':b1, 'b2':b2})
foo_b = env.b1(source='foo.a')
env.b2(source=foo_b)
"""

test.write('foo.a', """\
foo.c
foo.b
built
""")

python_file_line = test.python_file_line(SConstruct_path, 11)

### Gross mistake in Builder spec

test.write(SConstruct_path, sconstruct % '\
b2 = Builder(act__ion=buildop, src_suffix=".b", suffix=".c")')

expect_stderr = """\

scons: *** Builder b2 must have an action to build ['foo.c'].
""" + python_file_line

test.run(arguments='.', stderr=expect_stderr, status = 2)

### Subtle mistake in Builder spec

test.write(SConstruct_path, sconstruct % '\
b2 = Builder(actoin=buildop, src_suffix=".b", suffix=".c")')

expect_stderr="""\

scons: *** Builder b2 must have an action to build ['foo.c'].
""" + python_file_line

test.run(arguments='test2', stderr=expect_stderr, status=2)

### Missing action in Builder spec

test.write(SConstruct_path, sconstruct % '\
b2 = Builder(src_suffix=".b", suffix=".c")')

expect_stderr = """\

scons: *** Builder b2 must have an action to build ['foo.c'].
""" + python_file_line

test.run(arguments='test2', stderr=expect_stderr, status = 2)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
