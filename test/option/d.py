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
Verify that the -d option is ignored.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', "DefaultEnvironment(tools=[])\n")

test.run(arguments = '-d .',
         stderr = "Warning:  ignoring -d option\n")

test.pass_test()

#

test.subdir('subdir')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment()
env.Program(target = 'aaa', source = 'aaa.c')
env.Program(target = 'bbb', source = 'bbb.c')
SConscript('subdir/SConscript')
""")

test.write(['subdir', 'SConscript'], """
env = Environment()
env.Program(target = 'ccc', source = 'ccc.c')
env.Program(target = 'ddd', source = 'ddd.c')
""")

test.write('aaa.c', """
int
main(int argc, char *argv)
{
        argv[argc++] = "--";
        printf("aaa.c\n");
        exit (0);
}
""")

test.write('bbb.c', """
int
main(int argc, char *argv)
{
        argv[argc++] = "--";
        printf("bbb.c\n");
        exit (0);
}
""")

test.write(['subdir', 'ccc.c'], """
int
main(int argc, char *argv)
{
        argv[argc++] = "--";
        printf("subdir/ccc.c\n");
        exit (0);
}
""")

test.write(['subdir', 'ddd.c'], """
int
main(int argc, char *argv)
{
        argv[argc++] = "--";
        printf("subdir/ddd.c\n");
        exit (0);
}
""")

test.run(arguments = '-d .', stdout = """
Target aaa: aaa.o
Checking aaa
  Checking aaa.o
    Checking aaa.c
  Rebuilding aaa.o: out of date.
cc -c -o aaa.o aaa.c
Rebuilding aaa: out of date.
cc -o aaa aaa.o
Target aaa.o: aaa.c
Target bbb: bbb.o
Checking bbb
  Checking bbb.o
    Checking bbb.c
  Rebuilding bbb.o: out of date.
cc -c -o bbb.o bbb.c
Rebuilding bbb: out of date.
cc -o bbb bbb.o
Target bbb.o: bbb.c
Target subdir/ccc/g: subdir/ccc.o
Checking subdir/ccc/g
  Checking subdir/ccc/g.o
    Checking subdir/ccc/g.c
  Rebuilding subdir/ccc/g.o: out of date.
cc -c -o subdir/ccc/g.o subdir/ccc.c
Rebuilding subdir/ccc/g: out of date.
cc -o subdir/ccc/g subdir/ccc.o
Target subdir/ccc/g.o: subdir/ccc.c
Target subdir/ddd/g: subdir/ddd.o
Checking subdir/ddd/g
  Checking subdir/ddd/g.o
    Checking subdir/ddd/g.c
  Rebuilding subdir/ddd/g.o: out of date.
cc -c -o subdir/ddd/g.o subdir/ddd.c
Rebuilding subdir/ddd/g: out of date.
cc -o subdir/ddd/g subdir/ddd.o
Target subdir/ddd/g.o: subdir/ddd.c
""")

test.run(program = test.workpath('aaa'), stdout = "aaa.c\n")
test.run(program = test.workpath('bbb'), stdout = "bbb.c\n")
test.run(program = test.workpath('subdir/ccc'), stdout = "subdir/ccc.c\n")
test.run(program = test.workpath('subdir/ddd'), stdout = "subdir/ddd.c\n")

test.pass_test()
 

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
