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
Verify that we don't rebuild things unnecessarily when the order of
signatures changes because an included file shifts from the local sandbox
to a Repository and vice versa.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir('repository', 'work')

repository = test.workpath('repository')
work_foo = test.workpath('work', 'foo' + _exe)
work_foo_h = test.workpath('work', 'foo.h')

test.write(['work', 'SConstruct'], """
Repository(r'%s')
env = Environment(CPPPATH = ['.'])
env.Program(target = 'foo', source = 'foo.c')
""" % repository)

foo_h_contents = """\
#define STRING1 "foo.h"
"""

bar_h_contents = """\
#define STRING2 "bar.h"
"""

test.write(['repository', 'foo.h'], foo_h_contents)

test.write(['repository', 'bar.h'], bar_h_contents)

test.write(['repository', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <foo.h>
#include <bar.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", STRING1);
        printf("%s\n", STRING2);
        printf("repository/foo.c\n");
        exit (0);
}
""")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)



test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""foo.h
bar.h
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')



# Now create the bar.h file locally, and make sure it's still up-to-date.
# This will change the order in which the include files are listed when
# calculating the signature; the old order was something like:
#       /var/tmp/.../bar.h
#       /var/tmp/.../far.h
# and the new order will be:
#       /var/tmp/.../far.h
#       bar.h
# Because we write the same bar.h file contents, this should not cause
# a rebuild (because we sort the resulting signatures).

test.write(['work', 'bar.h'], bar_h_contents)

test.up_to_date(chdir = 'work', arguments = '.')



# And for good measure, write the same foo.h file locally.

test.write(['work', 'foo.h'], foo_h_contents)

test.up_to_date(chdir = 'work', arguments = '.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
