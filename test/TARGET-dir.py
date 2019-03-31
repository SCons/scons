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
Test use of ${TARGET.dir} to specify a CPPPATH directory in
combination VariantDirs and a generated .h file.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

build1_foo = test.workpath('build1', 'foo' + _exe)
build2_foo = test.workpath('build2', 'foo' + _exe)

test.subdir('src', 'build1', 'build2')

test.write('SConstruct', """
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())
    f.close()
env = Environment(CPPPATH='${TARGET.dir}')
env.Append(BUILDERS = {'Cat' : Builder(action=cat)})
Export('env')
VariantDir('build1', 'src')
SConscript('build1/SConscript')
VariantDir('build2', 'src')
SConscript('build2/SConscript', duplicate=0)
""")

test.write(['src', 'SConscript'], """
Import('env')
env.Cat('foo.h', 'foo.h.in')
env.Program('foo', ['foo.c'])
""")

test.write(['src', 'foo.h.in'], """\
#define STRING  "foo.h.in\\n"
""")

test.write(['src', 'foo.c'], """\
#include <stdio.h>
#include <stdlib.h>

#include <foo.h>

int
main(int argc, char *argv[])
{
    printf(STRING);
    printf("foo.c\\n");
    exit (0);
}
""")

test.run(arguments = '.')

test.run(program = build1_foo, stdout = "foo.h.in\nfoo.c\n")
test.run(program = build2_foo, stdout = "foo.h.in\nfoo.c\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
