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
Test fetching source files from RCS.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

rcs = test.where_is('rcs')
if not rcs:
    print "Could not find RCS, skipping test(s)."
    test.no_result(1)

ci = test.where_is('ci')
if not ci:
    print "Could not find `ci' command, skipping test(s)."
    test.no_result(1)

# Test checkouts from local RCS files
test.subdir('work1')

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work1', file], "work1/%s\n" % file)
    args = "-f -t%s %s" % (file, file)
    test.run(chdir = 'work1', program = ci, arguments = args, stderr = None)

test.no_result(os.path.exists(test.workpath('work1', 'aaa.in')))
test.no_result(os.path.exists(test.workpath('work1', 'bbb.in')))
test.no_result(os.path.exists(test.workpath('work1', 'ccc.in')))

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
env.SourceCode('.', env.RCS())
""")

test.write(['work1', 'bbb.in'], "checked-out work1/bbb.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout("""\
co -p aaa.in,v > aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
co -p ccc.in,v > ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
"""),
         stderr = """\
aaa.in,v  -->  standard output
revision 1.1
ccc.in,v  -->  standard output
revision 1.1
""")

test.fail_test(test.read(['work1', 'all']) != "work1/aaa.in\nchecked-out work1/bbb.in\nwork1/ccc.in\n")

# Test RCS checkouts from an RCS subdirectory.
test.subdir('work2', ['work2', 'RCS'])

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work2', file], "work2/%s\n" % file)
    args = "-f -t%s %s" % (file, file)
    test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

test.no_result(os.path.exists(test.workpath('work2', 'aaa.in')))
test.no_result(os.path.exists(test.workpath('work2', 'bbb.in')))
test.no_result(os.path.exists(test.workpath('work2', 'ccc.in')))

test.write(['work2', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  RCSFLAGS='-q')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.RCS())
""")

test.write(['work2', 'bbb.in'], "checked-out work2/bbb.in\n")

test.run(chdir = 'work2',
         arguments = '.',
         stdout = test.wrap_stdout("""\
co -q -p aaa.in,v > aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
co -q -p ccc.in,v > ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
"""))

test.fail_test(test.read(['work2', 'all']) != "work2/aaa.in\nchecked-out work2/bbb.in\nwork2/ccc.in\n")

test.pass_test()
