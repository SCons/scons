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
Test that the $SHCCCOMSTR construction variable allows you to customize
the shared object C compilation output.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

if os.path.normcase('.c') == os.path.normcase('.C'):
    alt_c_suffix = '.C'
else:
    alt_c_suffix = '.c'

test.write('SConstruct', """
env = Environment(SHCCCOM = r'%(_python_)s mycompile.py cc $TARGET $SOURCE',
                  SHCCCOMSTR = 'Building $TARGET from $SOURCE',
                  SHOBJPREFIX='',
                  SHOBJSUFFIX='.obj')
env.SharedObject(target = 'test1', source = 'test1.c')
env.SharedObject(target = 'test2', source = 'test2%(alt_c_suffix)s')
""" % locals())

test.write('test1.c', 'test1.c\n/*cc*/\n')

test.write('test2'+alt_c_suffix, """\
test2.C
/*cc*/
""")

test.run(stdout = test.wrap_stdout("""\
Building test1.obj from test1.c
Building test2.obj from test2%(alt_c_suffix)s
""" % locals()))

test.must_match('test1.obj', "test1.c\n")
test.must_match('test2.obj', "test2.C\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
