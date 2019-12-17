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
Verify use of $CHANGED_SOURCES with batch builders correctly decides
to rebuild if any sources of changed, and specifies only the sources
on the rebuild.
"""

import TestSCons

test = TestSCons.TestSCons()

_python_ = TestSCons._python_

test.write('batch_build.py', """\
import os
import sys
dir = sys.argv[1]
for infile in sys.argv[2:]:
    inbase = os.path.splitext(os.path.split(infile)[1])[0]
    outfile = os.path.join(dir, inbase+'.out')
    with open(outfile, 'wb') as f, open(infile, 'rb') as infp:
            f.write(infp.read())
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment()
env['BATCH_BUILD'] = 'batch_build.py'
env['BATCHCOM'] = r'%(_python_)s $BATCH_BUILD ${TARGET.dir} $CHANGED_SOURCES'
bb = Action('$BATCHCOM', batch_key=True, targets='CHANGED_TARGETS')
env['BUILDERS']['Batch'] = Builder(action=bb)
env1 = env.Clone()
env1.Batch('out1/f1a.out', 'f1a.in')
env1.Batch('out1/f1b.out', 'f1b.in')
env2 = env.Clone()
env2.Batch('out2/f2a.out', 'f2a.in')
env3 = env.Clone()
env3.Batch('out3/f3a.out', 'f3a.in')
env3.Batch('out3/f3b.out', 'f3b.in')
""" % locals())

test.write('f1a.in', "f1a.in\n")
test.write('f1b.in', "f1b.in\n")
test.write('f2a.in', "f2a.in\n")
test.write('f3a.in', "f3a.in\n")
test.write('f3b.in', "f3b.in\n")

expect = test.wrap_stdout("""\
%(_python_)s batch_build.py out1 f1a.in f1b.in
%(_python_)s batch_build.py out2 f2a.in
%(_python_)s batch_build.py out3 f3a.in f3b.in
""" % locals())

test.run(stdout = expect)

test.must_match(['out1', 'f1a.out'], "f1a.in\n")
test.must_match(['out1', 'f1b.out'], "f1b.in\n")
test.must_match(['out2', 'f2a.out'], "f2a.in\n")
test.must_match(['out3', 'f3a.out'], "f3a.in\n")
test.must_match(['out3', 'f3b.out'], "f3b.in\n")



test.write('f1b.in', "f1b.in 2\n")

expect = test.wrap_stdout("""\
%(_python_)s batch_build.py out1 f1b.in
""" % locals())

test.run(stdout = expect)

test.must_match(['out1', 'f1a.out'], "f1a.in\n")
test.must_match(['out1', 'f1b.out'], "f1b.in 2\n")
test.must_match(['out2', 'f2a.out'], "f2a.in\n")
test.must_match(['out3', 'f3a.out'], "f3a.in\n")
test.must_match(['out3', 'f3b.out'], "f3b.in\n")



test.write('f3a.in', "f3a.in 2\n")

expect = test.wrap_stdout("""\
%(_python_)s batch_build.py out3 f3a.in
""" % locals())

test.run(stdout = expect)

test.must_match(['out1', 'f1a.out'], "f1a.in\n")
test.must_match(['out1', 'f1b.out'], "f1b.in 2\n")
test.must_match(['out2', 'f2a.out'], "f2a.in\n")
test.must_match(['out3', 'f3a.out'], "f3a.in 2\n")
test.must_match(['out3', 'f3b.out'], "f3b.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
