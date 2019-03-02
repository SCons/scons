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
Test that multiple target files get retrieved from a CacheDir correctly.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('cache', 'multiple')

cache = test.workpath('cache')

multiple_bar = test.workpath('multiple', 'bar')
multiple_foo = test.workpath('multiple', 'foo')

test.write(['multiple', 'SConstruct'], """\
DefaultEnvironment(tools=[])
def touch(env, source, target):
    with open('foo', 'w') as f:
        f.write("")
    with open('bar', 'w') as f:
        f.write("")
CacheDir(r'%(cache)s')
env = Environment(tools=[])
env.Command(['foo', 'bar'], ['input'], touch)
""" % locals())

test.write(['multiple', 'input'], "multiple/input\n")

test.run(chdir = 'multiple')

test.must_exist(multiple_foo)
test.must_exist(multiple_bar)

test.run(chdir = 'multiple', arguments = '-c')

test.must_not_exist(multiple_foo)
test.must_not_exist(multiple_bar)

test.run(chdir = 'multiple')

test.must_exist(multiple_foo)
test.must_exist(multiple_bar)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
