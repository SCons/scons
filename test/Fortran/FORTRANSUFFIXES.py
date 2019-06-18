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
Test the ability to scan additional filesuffixes added to $FORTRANSUFFIXES.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('myfc.py', r"""
import sys
def do_file(outf, inf):
    with open(inf, 'rb') as inf:
        for line in inf.readlines():
            if line[:15] == b"      INCLUDE '":
                do_file(outf, line[15:-2])
            else:
                outf.write(line)
with open(sys.argv[1], 'wb') as outf:
    for f in sys.argv[2:]:
        do_file(outf, f)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(FORTRANPATH = ['.'],
                  FORTRAN = r'%(_python_)s myfc.py',
                  FORTRANCOM = '$FORTRAN $TARGET $SOURCES',
                  OBJSUFFIX = '.o')
env.Append(FORTRANSUFFIXES = ['.x'])
env.Object(target = 'test1', source = 'test1.f')
env.InstallAs('test1_f', 'test1.f')
env.InstallAs('test1_x', 'test1.x')
env.InstallAs('test2_f', 'test2.f')
""" % locals())

test.write('test1.f', """\
      test1.f 1
      INCLUDE 'test2.f'
      INCLUDE 'test1.x'
""")

test.write('test2.f', """\
      test2.f 1
      INCLUDE 'foo.f'
""")

test.write('test1.x', """\
      test1.x 1
      INCLUDE 'foo.f'
""")

test.write('foo.f', """\
      foo.f 1
""")

expect = test.wrap_stdout("""\
%(_python_)s myfc.py test1.o test1.f
Install file: "test1.f" as "test1_f"
Install file: "test1.x" as "test1_x"
Install file: "test2.f" as "test2_f"
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('test1.o', """\
      test1.f 1
      test2.f 1
      foo.f 1
      test1.x 1
      foo.f 1
""")

test.up_to_date(arguments='.')

test.write('foo.f', """\
      foo.f 2
""")

expect = test.wrap_stdout("""\
%(_python_)s myfc.py test1.o test1.f
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('test1.o', """\
      test1.f 1
      test2.f 1
      foo.f 2
      test1.x 1
      foo.f 2
""")

test.up_to_date(arguments='.')

test.write('test1.x', """\
      test1.x 2
      INCLUDE 'foo.f'
""")

expect = test.wrap_stdout("""\
%(_python_)s myfc.py test1.o test1.f
Install file: "test1.x" as "test1_x"
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('test1.o', """\
      test1.f 1
      test2.f 1
      foo.f 2
      test1.x 2
      foo.f 2
""")

test.up_to_date(arguments='.')

test.write('test2.f', """\
      test2.f 2
      INCLUDE 'foo.f'
""")

expect = test.wrap_stdout("""\
%(_python_)s myfc.py test1.o test1.f
Install file: "test2.f" as "test2_f"
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('test1.o', """\
      test1.f 1
      test2.f 2
      foo.f 2
      test1.x 2
      foo.f 2
""")

test.up_to_date(arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
