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

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as infp:
    f.write(infp.read())
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
SetOption('md5_chunksize', 128)
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(tools=[], BUILDERS = { 'B' : B })
f1 = env.B(target = 'f1.out', source = 'f1.in')
f2 = env.B(target = 'f2.out', source = 'f2.in')
Requires(f2, f1)
""" % locals())

test.write('f1.in', str(list(range(10))))
test.write('f2.in', str(list(range(100000))))

expected_stdout = test.wrap_stdout("""\
%(_python_)s build.py f1.out f1.in
%(_python_)s build.py f2.out f2.in
""" % locals())

#
# Test with SetOption('md5_chunksize')
#
test.run(arguments = '.',
         stdout=expected_stdout,
         stderr='')
test.must_exist('f1.out')
test.must_exist('f2.out')

test.run(arguments = '-c .')
test.must_not_exist('f1.out')
test.must_not_exist('f2.out')

#
# Test with --md5-chunksize
#
test.run(arguments = '--md5-chunksize=128 .',
         stdout=expected_stdout,
         stderr='')
test.must_exist('f1.out')
test.must_exist('f2.out')

test.run(arguments = '--md5-chunksize=128 -c .')
test.must_not_exist('f1.out')
test.must_not_exist('f2.out')

test.pass_test()

#
# Big-file test
#
test2 = TestSCons.TestSCons()

if sys.platform.find('linux') == -1:
    test2.skip_test("skipping test on non-Linux platform '%s'\n" % sys.platform)

dd = test2.where_is('dd')

if not dd:
    test2.skip_test('dd not found; skipping test\n')

expected_stdout = test2.wrap_stdout("""\
dd if=/dev/zero of=test.big seek=100 bs=1M count=0 2>/dev/null
get_stat(["test.stat"], ["test.big"])
""")

test2.write('SConstruct', """
DefaultEnvironment(tools=[])
import os
def get_stat(target, source, env):
    stat = os.stat(source[0].get_abspath())
    with open(target[0].get_abspath(),'w') as dest:
        dest.write(str(stat))
env = Environment(tools=[])
env.Command('test.big', 'SConstruct', 'dd if=/dev/zero of=test.big seek=100 bs=1M count=0 2>/dev/null')
env.AlwaysBuild('test.big')
env.Command('test.stat', 'test.big', Action(get_stat))
""")

test2.run(arguments='--md5-chunksize=128', stdout=expected_stdout, stderr='')
test2.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
