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
This verifies the --interactive command line option's ability to
rebuild a target when an implicit dependency (include line) is
added to the source file.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('foo.h.in', """
#define FOO_STRING "foo.h.in"
""")

test.write('foo.c', """
#include <stdio.h>

int main(void)
{
    printf("foo.c\\n");
    return 0;
}
""")

test.write('SConstruct', """
env = Environment(CPPPATH=['.'])
env.Command('foo.h', ['foo.h.in'], Copy('$TARGET', '$SOURCE'))
env.Program('foo', ['foo.c'])
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
Command('3', [], Touch('$TARGET'))
""")

foo_exe     = test.workpath('foo' + TestSCons._exe)



# Start scons, to build "foo"
scons = test.start(arguments = '--interactive')

scons.send("build %(foo_exe)s 1\n" % locals())

test.wait_for(test.workpath('1'), popen=scons)

test.run(program = foo_exe, stdout = 'foo.c\n')




# Update foo.c
# We add a new #include line, to make sure that scons notices
# the new implicit dependency and builds foo.h first.
test.write('foo.c', """
#include <foo.h>

#include <stdio.h>

int main(void)
{
    printf("%s\\n", FOO_STRING);
    return 0;
}
""")

scons.send("build %(foo_exe)s 2\n" % locals())

test.wait_for(test.workpath('2'))

# Run foo, and make sure it prints correctly
test.run(program = foo_exe, stdout = 'foo.h.in\n')



test.write('foo.h.in', """
#define FOO_STRING "foo.h.in 3"
""")



scons.send("build %(foo_exe)s 3\n" % locals())

test.wait_for(test.workpath('3'))

# Run foo, and make sure it prints correctly
test.run(program = foo_exe, stdout = 'foo.h.in 3\n')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
