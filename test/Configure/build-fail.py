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
Verify that Configure tests work even after an earlier test fails.

This was broken in 0.98.3 because we'd mark the /usr/bin/g++ compiler
as having failed (because it was on the candidates list as the implicit
command dependency for both the object file and executable generated
for the configuration test) and then avoid trying to rebuild anything
else that used the "failed" Node.

Thanks to Ben Webb for the test case.
"""

import os
import re

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.subdir('a', 'b')

a_boost_hpp = os.path.join('..', 'a', 'boost.hpp')
b_boost_hpp = os.path.join('..', 'b', 'boost.hpp')

test.write('SConstruct', """\
import os
def _check(context):
    for dir in ['a', 'b']:
        inc = os.path.join('..', dir, 'boost.hpp')
        result = context.TryRun('''
        #include "%s"

        int main(void) { return 0; }
        ''' % inc, '.cpp')[0]
        if result:
            import sys
            sys.stdout.write('%s: ' % inc)
            break
    context.Result(result)
    return result
env = Environment()
conf = env.Configure(custom_tests={'CheckBoost':_check})
conf.CheckBoost()
conf.Finish()
""")

test.write(['b', 'boost.hpp'], """#define FILE "b/boost.hpp"\n""")

expect = test.wrap_stdout(read_str = "%s: yes\n" % re.escape(b_boost_hpp),
                          build_str = "scons: `.' is up to date.\n")

test.run(arguments='--config=force', stdout=expect)

expect = test.wrap_stdout(read_str = "%s: yes\n" % re.escape(a_boost_hpp),
                          build_str = "scons: `.' is up to date.\n")

test.write(['a', 'boost.hpp'], """#define FILE "a/boost.hpp"\n""")

test.run(arguments='--config=force', stdout=expect)

test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
