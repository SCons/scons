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
Test for a specific race condition that used to stop a build cold when
a Node's ref_count would get decremented past 0 and "disappear" from
the Taskmaster's walk of the dependency graph.

Note that this test does not fail every time, but would at least fail
more than 60%-70% of the time on the system(s) I tested.

The rather complicated set up here creates a condition where,
after building four "object files" simultaneously while running with
-j4, sets up a race condition amongst the three dependencies of the
c6146/cpumanf.out file, where two of the dependencies are built at the
same time (that is, by the same command) and one is built separately.

We used to detect Nodes that had been started but not finished building
and just set the waiting ref_count to the number of Nodes.  In this case,
if we got unlucky, we'd re-visit the Nodes for the two files first and
set the ref_count to two *before* the command that built individual node
completed and decremented the ref_count from two to one.  Then when the
two files completed, we'd update the ref_count to 1 - 2 = -1, which would
cause the Taskmaster to *not* "wake up" the Node because it's ref_count
hadn't actually reached 0.

(The solution was to not set the ref_count, but to add to it only the
Nodes that were, in fact, added to the waiting_parents lists of various
child Nodes.)
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', """\
import sys
import time
args = sys.argv[1:]
outputs = []
while args:
    if args[0][0] != '-':
        break
    arg = args.pop(0)
    if arg == '-o':
        outputs.append(args.pop(0))
        continue
    if arg == '-s':
        time.sleep(int(args.pop(0)))
contents = ''
for ifile in args:
    with open(ifile, 'r') as ifp:
        contents = contents + ifp.read()
for ofile in outputs:
    with open(ofile, 'w') as ofp:
        ofp.write('%s:  building from %s\\n' % (ofile, " ".join(args)))
        ofp.write(contents)
""")

#
#
#

test.write('SConstruct', """\
env = Environment()
cmd = r'%(_python_)s build.py -o $TARGET $SOURCES'
f1 = env.Command('c6416/cpumanf/file1.obj', 'file1.c', cmd)
f2 = env.Command('c6416/cpumanf/file2.obj', 'file2.c', cmd)
f3 = env.Command('c6416/cpumanf/file3.obj', 'file3.c', cmd)
f4 = env.Command('c6416/cpumanf/file4.obj', 'file4.c', cmd)
f5 = env.Command('c6416/cpumanf/file5.obj', 'file5.c', cmd)
f6 = env.Command('c6416/cpumanf/file6.obj', 'file6.c', cmd)

objs = f1 + f2 + f3 + f4 + f5 + f6

btc = env.Command('build/target/cpumanf.out', 'c6416/cpumanf.out', cmd)

addcheck_obj = env.Command('addcheck.obj', 'addcheck.c', cmd)

addcheck_exe = env.Command('addcheck.exe', addcheck_obj, cmd)

cmd2 = r'%(_python_)s build.py -s 2 -o ${TARGETS[0]} -o ${TARGETS[1]} $SOURCES'

cksums = env.Command(['c6416/cpumanf_pre_cksum.out',
                     'c6416/cpumanf_pre_cksum.map'],
                    objs,
                    cmd2)

cpumanf_out = env.Command('c6416/cpumanf.out',
                          cksums + addcheck_exe,
                          cmd)

cpumanf = env.Alias('cpumanf', objs + btc)

env.Command('after.out', cpumanf, r'%(_python_)s build.py -o $TARGET after.in')
""" % locals())

test.write('file1.c', "file1.c\n")
test.write('file2.c', "file2.c\n")
test.write('file3.c', "file3.c\n")
test.write('file4.c', "file4.c\n")
test.write('file5.c', "file5.c\n")
test.write('file6.c', "file6.c\n")

test.write('addcheck.c', "addcheck.c\n")

test.write('after.in', "after.in\n")

test.run(arguments = '-j4 after.out')

test.must_match('after.out', """\
after.out:  building from after.in
after.in
""", mode='r')

test.write('file5.c', "file5.c modified\n")

test.write('after.in', "after.in modified\n")

test.run(arguments = '-j4 after.out')

test.must_match('after.out', """\
after.out:  building from after.in
after.in modified
""", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
