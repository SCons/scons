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
Verify that setting exitstatfunc on an Action works as advertised.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
def always_succeed(s):
    # Always return 0, which indicates success.
    return 0

def copy_fail(target, source, env):
    with open(str(source[0]), 'rb') as infp, open(str(target[0]), 'wb') as f:
        f.write(infp.read())
    return 2

a = Action(copy_fail, exitstatfunc=always_succeed)
Alias('test1', Command('test1.out', 'test1.in', a))

def fail(target, source, env):
    return 2

t2 = Command('test2.out', 'test2.in', Copy('$TARGET', '$SOURCE'))
AddPostAction(t2, Action(fail, exitstatfunc=always_succeed))
Alias('test2', t2)
""")

test.write('test1.in', "test1.in\n")
test.write('test2.in', "test2.in\n")

test.run(arguments = 'test1')

test.must_match('test1.out', "test1.in\n")

test.run(arguments = 'test2')

test.must_match('test2.out', "test2.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
