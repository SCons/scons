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

"""
Verify basic operation of the --interactive command line option to build
a target, while using a Configure context within the environment.

Also tests that "b" can be used as a synonym for "build".
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import TestCmd
import re

# The order of the statements in the expected stdout is unreliable.

# case 1
# scons>>> .*foo\.cpp.*
# scons>>> scons: `foo.obj' is up to date.
# scons>>> .*foo\.cpp.*
# scons>>> scons: `foo.obj' is up to date.
# scons>>>\s*

# case 2
# scons>>> .*foo\.cpp.*
# scons>>> .*foo\.cpp.*
# scons>>> scons: `foo.obj' is up to date.
# scons>>> scons: `foo.obj' is up to date.
# scons>>>\s*

# The order of this list is related to the order of the counts below
expected_patterns = [
    re.compile(r"^scons>>> .*foo\.cpp.*$"),
    re.compile(r"^scons>>> scons: `foo.obj' is up to date\.$"),
    re.compile(r"^scons>>>\s*$"),
]

# The order of this list is related to the order of the regular expressions above
expected_counts = [
    [2,2,1], # case 1 and 2
]

# This is used for the diff output when the test fails and to distinguish between
# stdout and stderr in the match function below.
expect_stdout = r"""scons>>> .*foo\.cpp.*
scons>>> .*foo\.cpp.*
scons>>> scons: `foo.obj' is up to date.
scons>>> scons: `foo.obj' is up to date.
scons>>>\s*
"""

def match_custom(lines, expect):

    if expect != expect_stdout:
        # stderr
        if lines == expect:
            return 1
        return None

    # taken directly from TestCmd
    if not TestCmd.is_List(lines):
        # CRs mess up matching (Windows) so split carefully
        lines = re.split('\r?\n', lines)

    # record number of matches for each regex
    n_actual = [0] * len(expected_patterns)
    for line in lines:
        for i, regex in enumerate(expected_patterns):
            if regex.search(line):
                n_actual[i] += 1
                break

    # compare actual counts to expected counts
    for n_expect in expected_counts:
        if n_actual == n_expect:
            return 1

    return None

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mycc.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    for l in [l for l in ifp.readlines() if l[:7] != '/*c++*/']:
        ofp.write(l)
sys.exit(0)
""")

test.write('SConstruct', """\
env = Environment(CXXCOM = r'%(_python_)s mycc.py $TARGET $SOURCE',
                  OBJSUFFIX='.obj')

# Ensure that our 'compiler' works...
def CheckMyCC(context):
    context.Message('Checking for MyCC compiler...')
    result = context.TryBuild(context.env.Object,
                              'int main(void) {return 0;}',
                              '.cpp')
    context.Result(result)
    return result

conf = Configure(env, custom_tests = {'CheckMyCC' : CheckMyCC})

if conf.CheckMyCC():
    pass # build succeeded
else:
    Exit(1)
conf.Finish()

env.Object('foo.obj','foo.cpp')
""" % locals())

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
scons.send("build foo.obj\n")

test.wait_for(test.workpath('foo.obj'))
# Update without any changes -> no action
scons.send("build foo.obj\n")
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
scons.send("b foo.obj\n")

scons.send("build foo.obj\n")

test.finish(scons, stdout = expect_stdout, stderr = '', match = match_custom)

test.pass_test()


# not used: just record here to help debugging the expect_stdout pattern
actual_output_to_be_handled="""
scons>>> build foo.obj
/usr/bin/python3 mycc.py foo.obj foo.cpp
scons>>> build foo.obj
scons: `foo.obj' is up to date.
scons>>> b foo.obj
/usr/bin/python3 mycc.py foo.obj foo.cpp
scons>>> build foo.obj
scons: `foo.obj' is up to date.
scons>>>
"""

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
