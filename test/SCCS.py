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
Test fetching source files from SCCS.
"""

import TestSCons

test = TestSCons.TestSCons()

sccs = test.where_is('sccs')
if not sccs:
    print "Could not find SCCS, skipping test(s)."
    test.no_result(1)

# Test checkouts from local SCCS files.
test.subdir('work1')

test.preserve()

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work1', file], "work1/%s\n" % file)
    args = "create %s" % file
    test.run(chdir = 'work1', program = sccs, arguments = args, stderr = None)
    test.unlink(['work1', file])
    test.unlink(['work1', ','+file])

test.write(['work1', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.SCCS())
""")

test.write(['work1', 'bbb.in'], "checked-out work1/bbb.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout("""\
sccs get aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
sccs get ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
"""), stderr = """\
aaa.in 1.1: 1 lines
ccc.in 1.1: 1 lines
""")

test.fail_test(test.read(['work1', 'all']) != "work1/aaa.in\nchecked-out work1/bbb.in\nwork1/ccc.in\n")

test.pass_test()
