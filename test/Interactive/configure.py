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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mycc.py', r"""
import sys
outfile = open(sys.argv[1], 'wb')
infile = open(sys.argv[2], 'rb')
for l in [l for l in infile.readlines() if l[:7] != '/*c++*/']:
    outfile.write(l)
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
    
conf = Configure(env, 
                 custom_tests = {'CheckMyCC' : CheckMyCC})
                 
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

expect_stdout = r"""scons>>> .*foo\.cpp.*
scons>>> .*foo\.cpp.*
scons>>> scons: `foo.obj' is up to date.
scons>>> scons: `foo.obj' is up to date.
scons>>>\s*
"""

test.finish(scons, stdout = expect_stdout, match=TestSCons.match_re)

test.pass_test()

actual_output_to_be_handled="""
Actual output
python3.6 ~/devel/scons/hg/scons/src/script/scons.py -Q --interactive
scons>>> build foo.obj
/opt/local/bin/python3.6 mycc.py foo.obj foo.cpp
scons>>> build foo.obj
scons: `foo.obj' is up to date.
scons>>> b foo.obj
/opt/local/bin/python3.6 mycc.py foo.obj foo.cpp
scons>>> build foo.obj
scons: `foo.obj' is up to date.
scons>>>
"""

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
