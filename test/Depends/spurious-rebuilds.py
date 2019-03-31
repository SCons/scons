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
After adding some code for reducing the overall memory consumption in
revision b4bc497, a number of spurious rebuilds was observed by different
people. The problem was, that the value of the Node.changed() method got cached
too early for File nodes.

This test verifies that the changed() function works properly, especially
in connection with auto-generated sources, combined with an explicit Depends().  
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
# This tests the too-many-rebuilds problem with SCons 2.3.1 (test)
# Run like this: scons all-defuns.obj

# Test setup (only runs once)
import os.path
if not os.path.exists('mkl'):
  os.mkdir('mkl')
if not os.path.exists('test.c'):
  with open('test.c', 'w') as f:
      f.write('int i;')

env=Environment()
env.SharedObject('all-defuns.obj', 'all-defuns.c')
results = env.Command('all-defuns.c', 'test.c', Copy('$TARGET', '$SOURCE'))
env.Depends(results, '#mkl')
""")

test.run(arguments = 'all-defuns.obj')

test.must_exist('all-defuns.c')
test.must_exist('test.c')
test.must_exist('all-defuns.obj')

test.up_to_date(arguments = 'all-defuns.obj')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
