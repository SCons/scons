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
Test that the --debug=includes option prints the implicit
dependencies of a target.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(OBJSUFFIX = '.obj',
                  SHOBJSUFFIX = '.shobj',
                  LIBPREFIX = '',
                  LIBSUFFIX = '.lib',
                  SHLIBPREFIX = '',
                  SHLIBSUFFIX = '.shlib',
                  )
env.Program('foo.exe', ['foo.c', 'bar.c'])
env.StaticLibrary('foo', ['foo.c', 'bar.c'])
env.SharedLibrary('foo', ['foo.c', 'bar.c'], no_import_lib=True)
""")

test.write('foo.c', r"""
#include <stdio.h>
#include <stdlib.h>
#include "foo.h"
int main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f1.c\n");
        exit (0);
}
""")

test.write('bar.c', """
#include "bar.h"
int local = 1;
""")

test.write('foo.h', """
#ifndef FOO_H
#define FOO_H
#include "bar.h"
#endif
""")

test.write('bar.h', """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif
""")

includes = """
+-foo.c
  +-foo.h
    +-bar.h
"""
test.run(arguments = "--debug=includes foo.obj")

test.must_contain_all_lines(test.stdout(), [includes])



# In an ideal world, --debug=includes would also work when there's a build
# failure, but this would require even more complicated logic to scan
# all of the intermediate nodes that get skipped when the build failure
# occurs.  On the YAGNI theory, we're just not going to worry about this
# until it becomes an issue that someone actually cares enough about.

#test.write('bar.h', """
##ifndef BAR_H
##define BAR_H
##include "foo.h"
##endif
#THIS SHOULD CAUSE A BUILD FAILURE
#""")

#test.run(arguments = "--debug=includes foo.exe",
#         status = 2,
#         stderr = None)
#test.must_contain_all_lines(test.stdout(), [includes])



# These shouldn't print out anything in particular, but
# they shouldn't crash either:
test.run(arguments = "--debug=includes .")
test.run(arguments = "--debug=includes foo.c")
test.run(arguments = "--debug=includes foo.lib")
test.run(arguments = "--debug=includes foo.shlib")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
