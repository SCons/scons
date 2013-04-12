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
Test that the SConscript() src_dir argument.

Test case contributed by Dobes Vandermeer.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir(['build'],
            ['samples'],
            ['src'])

test.write(['SConstruct'], """\
env = Environment()

for src_dir in ['src','samples']:
    SConscript('build/glob_build.py', 
               src_dir=src_dir,
               variant_dir='build/output/'+src_dir,
               duplicate=0,
               exports=['env'])
""")

test.write(['build', 'glob_build.py'], """\
from glob import glob
from os.path import join
from os.path import basename
Import('env')

sources = list(map(basename, glob(join(str(env.Dir('.').srcnode()),'*.c'))))

# Trivial example; really I read the configuration file
# their build system uses to generate the vcproj files
for source in sources:
    env.Program(source)
""")

test.write(['samples', 'goodbye.c'], """\
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    printf("Goodbye, world!\\n");
    exit(0);
}
""")

test.write(['src', 'hello.c'], """\
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    printf("Hello, world!\\n");
    exit(0);
}
""")

test.run()

goodbye = test.workpath('build', 'output', 'samples', 'goodbye')
hello = test.workpath('build', 'output', 'src', 'hello')

test.run(program = goodbye, stdout = "Goodbye, world!\n")

test.run(program = hello, stdout = "Hello, world!\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
