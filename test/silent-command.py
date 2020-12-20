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

"""
Test the use of a preceding @ to suppress printing a command.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"


import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('build', 'src')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as fp:
    for f in sys.argv[2:]:
        with open(f, 'rb') as ifp:
            fp.write(ifp.read())
""")

test.write('SConstruct', """\
env = Environment()
env.Command('f1.out', 'f1.in', r'%(_python_)s build.py $TARGET $SOURCE')
env.Command('f2.out', 'f2.in', r'@%(_python_)s build.py $TARGET $SOURCE')
env.Command('f3.out', 'f3.in', r'@ %(_python_)s build.py $TARGET $SOURCE')
env.Command('f4.out', 'f4.in', r'@-%(_python_)s build.py $TARGET $SOURCE')
env.Command('f5.out', 'f5.in', r'@- %(_python_)s build.py $TARGET $SOURCE')
env.Command('f6.out', 'f6.in', r'-@%(_python_)s build.py $TARGET $SOURCE')
env.Command('f7.out', 'f7.in', r'-@ %(_python_)s build.py $TARGET $SOURCE')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")
test.write('f7.in', "f7.in\n")

expect = test.wrap_stdout("""\
%(_python_)s build.py f1.out f1.in
""" % locals())

test.run(arguments = '.', stdout = expect)

test.must_match('f1.out', "f1.in\n")
test.must_match('f2.out', "f2.in\n")
test.must_match('f3.out', "f3.in\n")
test.must_match('f4.out', "f4.in\n")
test.must_match('f5.out', "f5.in\n")
test.must_match('f6.out', "f6.in\n")
test.must_match('f7.out', "f7.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
