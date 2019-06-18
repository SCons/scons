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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
import SCons.Defaults
B = Builder(action=r'%(_python_)s build.py $TARGET $SOURCES')
env = Environment(tools=[])
env['BUILDERS']['B'] = B
env.B(target = 'sub1/foo.out', source = 'sub1/foo.in')
Export('env')
SConscript('sub1/SConscript')
SConscript('sub2/SConscript')
""" % locals())

test.write(['sub1', 'SConscript'], """
Import('env')
env.B(target = 'foo.out', source = 'foo.in')
Default('.')
""")

test.write(['sub1', 'foo.in'], "sub1/foo.in")

test.write(['sub2', 'SConscript'], """
Import('env')
env.Alias('bar', env.B(target = 'bar.out', source = 'bar.in'))
Default('.')

""")

test.write(['sub2', 'bar.in'], "sub2/bar.in")

test.run(arguments = '-D', chdir = 'sub1')

test.must_match(['sub1', 'foo.out'], "sub1/foo.in")
test.must_match(['sub2', 'bar.out'], "sub2/bar.in")

test.unlink(['sub1', 'foo.out'])
test.unlink(['sub2', 'bar.out'])

test.run(arguments = '-D bar', chdir = 'sub1')

test.must_not_exist(test.workpath('sub1', 'foo.out'))
test.must_exist(test.workpath('sub2', 'bar.out'))


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
