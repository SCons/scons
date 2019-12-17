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
Verify that $SOURCES attributes work even when there is no
sources list in the builder call.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
with open(sys.argv[1], 'wb') as ofp:
    for infile in sys.argv[2:]:
      with open(infile, 'rb') as ifp:
          ofp.write(ifp.read())
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(CATCOM=r'%(_python_)s cat.py $TARGET ${SOURCES.posix} $FILES')
env['BUILDERS']['Cat'] = Builder(action='$CATCOM')
env.Cat('out1', ['file1', 'file2', 'file3'])
env.Cat('out2', [], FILES=['file1', 'file2', 'file3'])
""" % locals())

test.write('file1', "file1\n")
test.write('file2', "file2\n")
test.write('file3', "file3\n")

test.run(arguments = '.')

test.must_match('out1', "file1\nfile2\nfile3\n")
test.must_match('out2', "file1\nfile2\nfile3\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
