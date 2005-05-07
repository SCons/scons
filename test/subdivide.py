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
Verify that rebuilds do not occur when SConsignFile(None) is used to
put a .sconsign file in each directory, and TargetSignatures('content')
is used to subdivide a dependency tree.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

#if os.path.exists('sconsign.py'):
#    sconsign = 'sconsign.py'
#elif os.path.exists('sconsign'):
#    sconsign = 'sconsign'
#else:
#    print "Can find neither 'sconsign.py' nor 'sconsign' scripts."
#    test.no_result(1)

test.subdir('src', ['src', 'sub'])

test.write('SConstruct', """\
SConsignFile(None)
TargetSignatures('content')
env = Environment()
env.SConscript('src/SConstruct', exports=['env'])
env.Object('foo.c')
""")

test.write(['src', 'SConstruct'], """\
SConsignFile(None)
TargetSignatures('content')
env = Environment()
p = env.Program('prog', ['main.c', '../foo%s', 'sub/bar.c'])
env.Default(p)
""" % TestSCons._obj)

test.write('foo.c', """\
void
foo(void) {
    printf("foo.c\\n");
}
""")

test.write(['src', 'main.c'], """\
extern void foo(void);
extern void bar(void);
int
main(int argc, char *argv[]) {
    foo();
    bar();
    printf("src/main.c\\n");
    exit (0);
}
""")

test.write(['src', 'sub', 'bar.c'], """\
void
bar(void) {
    printf("bar.c\\n");
}
""")

test.run()

test.run(program=test.workpath('src', 'prog'),
         stdout="foo.c\nbar.c\nsrc/main.c\n")

test.up_to_date(chdir='src', arguments = test.workpath())

test.up_to_date(arguments = '.')

test.pass_test()
