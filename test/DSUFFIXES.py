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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mydc.py', r"""
import sys
def do_file(outf, inf):
    with open(inf, 'rb') as ifp:
        for line in ifp.readlines():
            if line[:7] == b'import ':
                do_file(outf, line[7:-2] + b'.d')
            else:
                outf.write(line)
with open(sys.argv[1], 'wb') as outf:
    for f in sys.argv[2:]:
        do_file(outf, f)
sys.exit(0)
""")

test.write('SConstruct', """
# Force the 'dmd' tool to get added to the Environment, even if it's not
# installed, so we get its definition of variables to deal with turning
# '.d' suffix files into objects.
env = Environment()
Tool('dmd')(env)
# Now replace those suffixes with our fake-D things.
env.Replace(DPATH = ['.'],
            DC = r'%(_python_)s mydc.py',
            DFLAGS = [],
            DCOM = '$DC $TARGET $SOURCES',
            OBJSUFFIX = '.o')
env.Append(CPPSUFFIXES = ['.x'])
env.Object(target = 'test1', source = 'test1.d')
env.InstallAs('test1_d', 'test1.d')
env.InstallAs('test2_d', 'test2.d')
env.InstallAs('test3_d', 'test3.d')
""" % locals())

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

expect = test.wrap_stdout("""\
%(_python_)s mydc.py test1.o test1.d
Install file: "test1.d" as "test1_d"
Install file: "test2.d" as "test2_d"
Install file: "test3.d" as "test3_d"
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('test1.o', """\
test1.d 1
test2.d 1
foo.d 1
test3.d 1
foo.d 1
""")

test.up_to_date(arguments='.')

test.write('foo.d', "foo.d 2\n")

expect = test.wrap_stdout("""\
%(_python_)s mydc.py test1.o test1.d
""" % locals())

test.run(arguments='.', stdout=expect)

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

expect = test.wrap_stdout("""\
%(_python_)s mydc.py test1.o test1.d
Install file: "test3.d" as "test3_d"
""" % locals())

test.run(arguments='.', stdout=expect)

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

expect = test.wrap_stdout("""\
%(_python_)s mydc.py test1.o test1.d
Install file: "test2.d" as "test2_d"
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('test1.o', """\
test1.d 1
test2.d 2
foo.d 2
test3.d 2
foo.d 2
""")

test.up_to_date(arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
