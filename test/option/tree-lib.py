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
Make sure that --tree=derived output with a library dependency shows
the dependency on the library.  (On earlier versions of the Microsoft
toolchain this wouldn't show up unless the library already existed
on disk.)

Issue 1363: https://github.com/SCons/scons/issues/1363
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(LIBPREFIX='',
                  LIBSUFFIX='.lib',
                  OBJSUFFIX='.obj',
                  EXESUFFIX='.exe')
env.AppendENVPath('PATH', '.')
l = env.Library( 'util.lib', 'util.c' )
p = env.Program( 'test_tree_lib.exe', 'main.c', LIBS=l )
env.Command( 'foo.h', p, '$SOURCE > $TARGET')
""")

test.write('main.c', """\
#include <stdlib.h>
#include <stdio.h>
int
main(int argc, char **argv)
{
    printf("#define	FOO_H	\\"foo.h\\"\\n");
    return (0);
}
""")

test.write('util.c', """\
void
util(void)
{
    ;
}
""")

expect = """
  +-test_tree_lib.exe
    +-main.obj
    +-util.lib
      +-util.obj
"""

test.run(arguments = '--tree=derived foo.h')
test.must_contain_all_lines(test.stdout(), [expect])

test.up_to_date(arguments = 'foo.h')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
