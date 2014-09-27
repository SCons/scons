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
Verify basic operation of the --interactive command line option to build
a target, while using a Configure context within the environment.

Also tests that "b" can be used as a synonym for "build".
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import sys

env = Environment()

conf = Configure(env)
if not conf.CheckCXX():
    sys.exit(1)
conf.Finish()

env.Program('foo','foo.cpp')
""")

test.write('foo.cpp', """\
#include <stdio.h>

int main (int argc, char *argv[])
{
    printf("Hello, World!");
    return 0;
}
""")


scons = test.start(arguments = '-Q --interactive')
# Initial build
scons.send("build foo\n")

test.wait_for(test.workpath('foo'))
# Update without any changes -> no action
scons.send("build foo\n")
# Changing the source file
test.write('foo.cpp', """\
#include <stdio.h>

void foo()
{
  ;
}

int main (int argc, char *argv[])
{
    printf("Hello, World!");
    return 0;
}
""")

# Verify that "b" can be used as a synonym for the "build" command.
scons.send("b foo\n")

scons.send("build foo\n")

expect_stdout = r"""scons>>> .*foo\.cpp.*
.*foo.*
scons>>> .*foo\.cpp.*
.*foo.*
scons>>> scons: `foo' is up to date.
scons>>> scons: `foo' is up to date.
scons>>>\s*
"""

test.finish(scons, stdout = expect_stdout, match=TestSCons.match_re)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
