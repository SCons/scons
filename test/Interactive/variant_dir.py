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
XXX Put a description of the test here.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('markers',
            'work',
            ['work', 'sub1'])

marker_1 = test.workpath('markers', '1')
marker_2 = test.workpath('markers', '2')

test.write(['work', 'SConstruct'], """\
# build the plugin binaries
basepath = str(Dir('#').get_abspath())
env = Environment()
env.Append(BASEPATH=basepath)
env.Append(ENV = {'BASEPATH' : str(Dir('#').get_abspath())})
SConscript( 'sub1/SConscript',
            variant_dir = 'build', 
            duplicate=False, 
            exports='env')
Command(r'%(marker_1)s', [], Touch('$TARGET'))
Command(r'%(marker_2)s', [], Touch('$TARGET'))
""" % locals())

test.write(['work', 'sub1', 'SConscript'], """\
Import('env')
env.Program('hello.c')
""")

test.write(['work', 'sub1', 'hello.c'], """\
#include <stdio.h>
#include <stdlib.h>
int main( int iArgC, char *cpArgV[] )
{
    printf("hello\\n");
    exit (0);
}
""")



# The "chdir =" keyword argument in the test.start() call has no effect.
# Work around it for now.
import os
os.chdir('work/sub1')
scons = test.start(chdir = 'work/sub1', arguments = '-Q -u --interactive')

scons.send("build\n")

scons.send("build %s\n" % marker_1)

test.wait_for(marker_1)

test.run(program = test.workpath('work/build/hello'), stdout="hello\n")



test.write(['work', 'sub1', 'hello.c'], """\
#include <stdio.h>
#include <stdlib.h>
int main( int iArgC, char *cpArgV[] )
{
    printf("hello 2\\n");
    exit (0);
}
""")

scons.send("build\n")

scons.send("build %s\n" % marker_2)

test.wait_for(marker_2)

test.run(program = test.workpath('work/build/hello'), stdout="hello 2\n")



test.finish(scons)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
