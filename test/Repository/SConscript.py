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

import sys
import TestSCons

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

test = TestSCons.TestSCons()

#
test.subdir('work',
            ['work', 'src'],
            'repository',
            ['repository', 'src'])

#
workpath_repository = test.workpath('repository')
work_src_foo = test.workpath('work', 'src', 'foo' + _exe)

#
test.write(['work', 'SConstruct'], """
Repository(r'%s')
SConscript('src/SConscript')
""" % workpath_repository)

test.write(['repository', 'src', 'SConscript'], """
env = Environment()
env.Program(target = 'foo', source = ['aaa.c', 'bbb.c', 'main.c'])
""")

test.write(['repository', 'src', 'aaa.c'], r"""
void
aaa(void)
{
	printf("repository/src/aaa.c\n");
}
""")

test.write(['repository', 'src', 'bbb.c'], r"""
void
bbb(void)
{
	printf("repository/src/bbb.c\n");
}
""")

test.write(['repository', 'src', 'main.c'], r"""
extern void aaa(void);
extern void bbb(void);

int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	aaa();
	bbb();
	printf("repository/src/main.c\n");
	exit (0);
}
""")

# Make the repository non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', arguments = ".")

test.run(program = work_src_foo, stdout =
"""repository/src/aaa.c
repository/src/bbb.c
repository/src/main.c
""")

test.up_to_date(chdir = 'work', arguments = ".")

#
test.pass_test()
