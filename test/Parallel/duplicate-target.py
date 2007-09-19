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
Verify that, when a file is specified multiple times in a target
list, we still build all of the necessary targets.

This used to cause a target to "disappear" from the DAG when its reference
count dropped below 0, because we were subtracting the duplicated target
mutiple times even though we'd only visit it once.  This was particularly
hard to track down because the DAG itself (when printed with --tree=prune,
for example) doesn't show the duplication in the *target* list.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('work')

tar_output = test.workpath('work.tar')

test.write(['work', 'copy.py'], """\
import sys
import time
time.sleep(int(sys.argv[1]))
open(sys.argv[2], 'wb').write(open(sys.argv[3], 'rb').read())
""")

test.write(['work', 'SConstruct'], """\
env = Environment()
out1 = File('f1.out')
out2 = File('f2.out')
env.Command([out1, out1], 'f1.in', r'%(_python_)s copy.py 3 $TARGET $SOURCE')
env.Command([out2, out2], 'f2.in', r'%(_python_)s copy.py 3 $TARGET $SOURCE')

env.Tar(r'%(tar_output)s', Dir('.'))
""" % locals())

test.write(['work', 'f1.in'], "work/f1.in\n")
test.write(['work', 'f2.in'], "work/f2.in\n")

test.run(chdir = 'work', arguments = tar_output + ' -j2')

test.must_match(['work', 'f1.out'], "work/f1.in\n")
test.must_match(['work', 'f2.out'], "work/f2.in\n")
test.must_exist(tar_output)

test.pass_test()
