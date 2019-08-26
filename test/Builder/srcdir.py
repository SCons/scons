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
Verify that specifying a srcdir when calling a Builder correctly
prefixes each relative-path string with the specified srcdir.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('src', ['src', 'foo'])

file3 = test.workpath('file3')

test.write(['src', 'cat.py'], """\
import sys
with open(sys.argv[1], 'wb') as o:
    for f in sys.argv[2:]:
        with open(f, 'rb') as i:
            o.write(i.read())
""")

test.write(['src', 'SConstruct'], """\
DefaultEnvironment(tools=[])

Command('output',
        ['file1', File('file2'), r'%(file3)s', 'file4'],
        r'%(_python_)s cat.py $TARGET $SOURCES',
        srcdir='foo')
""" % locals())

test.write(['src', 'foo', 'file1'],     "file1\n")

test.write(['src', 'file2'],            "file2\n")

test.write(file3,                       "file3\n")

test.write(['src', 'foo', 'file4'],     "file4\n")

test.run(chdir = 'src', arguments = '.')

expected = """\
file1
file2
file3
file4
"""

test.must_match(['src', 'output'],  expected)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
