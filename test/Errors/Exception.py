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

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConstruct', """\
def foo(env, target, source):
    print(str(target[0]))
    with open(str(target[0]), 'wt') as f:
        f.write('foo')

def exit(env, target, source):
    raise Exception('exit')

env = Environment(BUILDERS = { 'foo'  : Builder(action=foo),
                               'exit' : Builder(action=exit) })

env.foo('foo.out', 'foo.in')
env.exit('exit.out', 'exit.in')
""")

test.write('foo.in', 'foo\n')

test.write('exit.in', 'exit\n')

# print_exception doesn't always show a source line if the source file
# no longer exists or that line in the source file no longer exists,
# so make sure the proper variations are supported in the following
# regexp.
expect = r"""scons: \*\*\* \[exit.out\] Exception : exit
Traceback \((most recent call|innermost) last\):
(  File ".+", line \d+, in \S+
    [^\n]+
)*(  File ".+", line \d+, in \S+
)*(  File ".+", line \d+, in \S+
    [^\n]+
)*\S.+
"""

# Build foo.out first, and expect an error when we try to build exit.out.
test.run(arguments='foo.out exit.out', stderr=expect, status=2)

# Rebuild.  foo.out should be up to date, and we should get the
# expected error building exit.out.
test.run(arguments='foo.out exit.out', stderr=expect, status=2)

stdout = test.stdout()

expect = "scons: `foo.out' is up to date."
test.must_contain_all_lines(test.stdout(), [expect])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
