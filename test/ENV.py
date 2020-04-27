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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

bin1_build_py = test.workpath('bin1', 'build.py')
bin2_build_py = test.workpath('bin2', 'build.py')

test.write('SConstruct', """
import os
Bld = Builder(action = r'%(_python_)s build.py $TARGET $SOURCES')
env1 = Environment(BUILDERS = { 'Bld' : Bld })
env2 = Environment(BUILDERS = { 'Bld' : Bld })
env1['ENV']['X'] = 'env1'
env2['ENV']['X'] = 'env2'
env1.Bld(target = 'env1.out', source = 'input')
env2.Bld(target = 'env2.out', source = 'input')
""" % locals())

test.write('build.py',
r"""\
import os
import sys
with open(sys.argv[2], 'r') as f:
    contents = f.read()
with open(sys.argv[1], 'w') as f:
    f.write("build.py %s\n%s" % (os.environ['X'], contents))
""")

test.write('input', "input file\n")

test.run(arguments = '.')

test.must_match('env1.out', "build.py env1\ninput file\n", mode='r')
test.must_match('env2.out', "build.py env2\ninput file\n", mode='r')


test.write('SConstruct', """
env = Environment()
foo = env.Command('foo', [], r'%(_python_)s build.py $TARGET')
env['ENV']['LIST'] = [foo, 'bar']
env['ENV']['FOO'] = foo
""" % locals())

test.write('build.py', r"""
import os
print('LIST:', os.environ['LIST'])
print('FOO:', os.environ['FOO'])
""")

test.run()

expect = [
    "LIST: foo%sbar" % os.pathsep,
    "FOO: foo",
]

test.must_contain_all_lines(test.stdout(), expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
