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
Verify the exit status and error output if variable expansion
throws a TypeError.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)



expect_build = r"""scons: \*\*\*%s TypeError `(unsubscriptable object|'NoneType' object is (not |un)subscriptable|'NoneType' object has no attribute '__getitem__')' trying to evaluate `%s'
"""

expect_read = "\n" + expect_build + TestSCons.file_expr

# Type errors at SConscript read time:
test.write('SConstruct', """\
env = Environment(NONE = None)
env.subst('${NONE[0]}')
""")

test.run(status=2, stderr=expect_read % ('', r'\$\{NONE\[0\]\}'))

# Type errors at build time:
test.write('SConstruct', """\
env = Environment(NONE = None)
env.Command('foo.bar', [], '${NONE[0]}')
""")

expect = expect_build % (r' \[foo\.bar\]', r'\$\{NONE\[0\]\}')

test.run(status=2, stderr=expect)

expect_build = r"""scons: \*\*\*%s TypeError `(not enough arguments; expected 3, got 1|func\(\) takes exactly 3 arguments \(1 given\)|func\(\) missing 2 required positional arguments: 'b' and 'c')' trying to evaluate `%s'
"""

expect_read = "\n" + expect_build + TestSCons.file_expr

# Type errors at SConscript read time:
test.write('SConstruct', """\
def func(a, b, c):
    pass
env = Environment(func = func)
env.subst('${func(1)}')
""")

test.run(status=2, stderr=expect_read % ('', r'\$\{func\(1\)\}'))

# Type errors at build time:
test.write('SConstruct', """\
def func(a, b, c):
    pass
env = Environment(func = func)
env.Command('foo.bar', [], '${func(1)}')
""")

expect = expect_build % (r' \[foo\.bar\]', r'\$\{func\(1\)\}')

test.run(status=2, stderr=expect)

# callable exceptions:
test.write('foo.c', """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo.c");
        exit (0);
}
""")

test.write('SConstruct', """\

class TestCallable(object):
    def __init__(self, thing, makePathsRelative = True, debug = False):
        pass
    def __call__(self, target, source, env, for_signature):
       raise TypeError("User callable exception")

env = Environment()
env["TESTCLASS"] = TestCallable
env["CCCOM"] = "$CC $_CCCOMCOM $CCFLAGS -o ${TESTCLASS('$TARGET')} -c ${TESTCLASS('$SOURCES')}"

env.Program(target='foo', source='foo.c')
""")

test.run(status=2, stderr=r'.*TypeError\s:\sUser\scallable\sexception.*')
print(test.stdout())
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
