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

import os
import string
import sys
import TestSCons

python = TestSCons.python
_exe   = TestSCons._exe

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

ranlib = test.detect('RANLIB', 'ranlib')

test.no_result(not ranlib)

test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

test.write('SConstruct', """
foo = Environment(LIBS = ['foo'], LIBPATH = ['.'])
bar = Environment(LIBS = ['bar'], LIBPATH = ['.'], RANLIB = '',
                  RANLIBFLAGS = foo.subst(r'%s wrapper.py $RANLIB $RANLIBFLAGS'))
foo.Library(target = 'foo', source = 'foo.c')
bar.Library(target = 'bar', source = 'bar.c')

main = foo.Object('main', 'main.c')

foo.Program(target = 'f', source = main)
bar.Program(target = 'b', source = main)
""" % python)

test.write('foo.c', r"""
void
library_function(void)
{
	printf("foo.c\n");
}
""")

test.write('bar.c', r"""
void
library_function(void)
{
	printf("bar.c\n");
}
""")

test.write('main.c', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	library_function();
	exit (0);
}
""")


test.run(arguments = 'f' + _exe, stderr=TestSCons.noisy_ar)

test.fail_test(os.path.exists(test.workpath('wrapper.out')))

test.run(arguments = 'b' + _exe, stderr=TestSCons.noisy_ar)

test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

test.pass_test()
