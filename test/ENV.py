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

import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

bin1_build_py = test.workpath('bin1', 'build.py')
bin2_build_py = test.workpath('bin2', 'build.py')

test.write('SConstruct', """
import os
Bld = Builder(action = r"%s build.py $TARGET $SOURCES")
env1 = Environment(ENV = {'X' : 'env1'}, BUILDERS = { 'Bld' : Bld })
env2 = Environment(ENV = {'X' : 'env2'}, BUILDERS = { 'Bld' : Bld })
env1.Bld(target = 'env1.out', source = 'input')
env2.Bld(target = 'env2.out', source = 'input')
""" % python)

test.write('build.py',
r"""#!/usr/bin/env python
import os
import sys
contents = open(sys.argv[2], 'rb').read()
open(sys.argv[1], 'wb').write("build.py %s\n%s" % (os.environ['X'], contents))
""")

test.write('input', "input file\n")

test.run(arguments = '.')

test.fail_test(test.read('env1.out') != "build.py env1\ninput file\n")
test.fail_test(test.read('env2.out') != "build.py env2\ninput file\n")

test.pass_test()
