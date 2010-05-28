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

"""
Test explicit checkouts from local RCS files.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConscript', """
Environment(tools = ['RCS']).RCS()
""")

msg_rcs = """The RCS() factory is deprecated and there is no replacement."""
warn_rcs = test.deprecated_fatal('deprecated-build-dir', msg_rcs)
msg_sc = """SourceCode() has been deprecated and there is no replacement.
\tIf you need this function, please contact dev@scons.tigris.org."""
warn_sc = test.deprecated_wrap(msg_sc)

rcs = test.where_is('rcs')
if not rcs:
    test.skip_test("Could not find 'rcs'; skipping test(s).\n")

ci = test.where_is('ci')
if not ci:
    test.skip_test("Could not find `ci' command, skipping test(s).\n")

co = test.where_is('co')
if not co:
    test.skip_test("Could not find `co' command, skipping test(s).\n")


main_cpp_contents = """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
    printf("main.c %s\\n");
    exit (0);
}
"""

test.write('main.c', main_cpp_contents % 1)

test.run(program = ci, arguments = '-f -tmain.c main.c', stderr = None)


test.write('SConstruct', """
SetOption('warn', 'deprecated-source-code')
import os
for key in ['LOGNAME', 'USERNAME', 'USER']:
    logname = os.environ.get(key)
    if logname: break
ENV = {'PATH' : os.environ['PATH'],
       'LOGNAME' : logname}
env = Environment(ENV=ENV, RCS_COFLAGS='-q')
env.SourceCode('main.c', env.RCS())
env2 = env.Clone()
env2.Program('main.exe', 'main.c')
""")

test.run(stderr = warn_rcs + warn_sc)

test.run(program = test.workpath('main.exe'), stdout = "main.c 1\n")

test.run(program = co, arguments = '-l main.c', stderr = None)


test.write('main.c', main_cpp_contents % 2)

test.not_up_to_date(arguments = 'main.exe', stderr = warn_rcs + warn_sc)

test.run(program = test.workpath('main.exe'), stdout = "main.c 2\n")


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
