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
Test the ability to scan additional filesuffixes added to $DSUFFIXES.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('mydc.py', r"""
import string
import sys
def do_file(outf, inf):
    for line in open(inf, 'rb').readlines():
        if line[:7] == 'import ':
            do_file(outf, line[7:-2]+'.d')
        else:
            outf.write(line)
outf = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    do_file(outf, f)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(DPATH = ['.'],
                  DC = r'%s mydc.py',
                  DFLAGS = [],
                  DCOM = '$DC $TARGET $SOURCES',
                  OBJSUFFIX = '.o')
env.Append(CPPSUFFIXES = ['.x'])
env.Object(target = 'test1', source = 'test1.d')
env.InstallAs('test1_d', 'test1.d')
env.InstallAs('test2_d', 'test2.d')
env.InstallAs('test3_d', 'test3.d')
""" % (python,))

test.write('test1.d', """\
test1.d 1
import test2;
import test3;
""")

test.write('test2.d', """\
test2.d 1
import foo;
""")

test.write('test3.d', """\
test3.d 1
import foo;
""")

test.write('foo.d', "foo.d 1\n")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mydc.py test1.o test1.d
Install file: "test1.d" as "test1_d"
Install file: "test2.d" as "test2_d"
Install file: "test3.d" as "test3_d"
""" % (python,)))

test.must_match('test1.o', """\
test1.d 1
test2.d 1
foo.d 1
test3.d 1
foo.d 1
""")

test.up_to_date(arguments='.')

test.write('foo.d', "foo.d 2\n")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mydc.py test1.o test1.d
""" % (python,)))

test.must_match('test1.o', """\
test1.d 1
test2.d 1
foo.d 2
test3.d 1
foo.d 2
""")

test.up_to_date(arguments='.')

test.write('test3.d', """\
test3.d 2
import foo;
""")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mydc.py test1.o test1.d
Install file: "test3.d" as "test3_d"
""" % (python,)))

test.must_match('test1.o', """\
test1.d 1
test2.d 1
foo.d 2
test3.d 2
foo.d 2
""")

test.up_to_date(arguments='.')

test.write('test2.d', """\
test2.d 2
import foo;
""")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mydc.py test1.o test1.d
Install file: "test2.d" as "test2_d"
""" % (python,)))

test.must_match('test1.o', """\
test1.d 1
test2.d 2
foo.d 2
test3.d 2
foo.d 2
""")

test.up_to_date(arguments='.')

test.pass_test()
