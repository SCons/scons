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
    test.pass_test(1)

# Test explicit checkouts from local SCCS files.
test.subdir('work1', ['work1', 'sub'])

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work1', file], "work1/%s\n" % file)
    args = "create %s" % file
    test.run(chdir = 'work1', program = sccs, arguments = args, stderr = None)
    test.unlink(['work1', file])
    test.unlink(['work1', ','+file])

test.write(['work1', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
args = "create SConscript"
test.run(chdir = 'work1/sub', program = sccs, arguments = args, stderr = None)
test.unlink(['work1', 'sub', 'SConscript'])
test.unlink(['work1', 'sub', ',SConscript'])

for file in ['ddd.in', 'eee.in', 'fff.in']:
    test.write(['work1', 'sub', file], "work1/sub/%s\n" % file)
    args = "create %s" % file
    test.run(chdir = 'work1/sub', program = sccs, arguments = args, stderr = None)
    test.unlink(['work1', 'sub', file])
    test.unlink(['work1', 'sub', ','+file])

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
SConscript('sub/SConscript', "env")
""")

test.write(['work1', 'bbb.in'], "checked-out work1/bbb.in\n")

test.write(['work1', 'sub', 'eee.in'], "checked-out work1/sub/eee.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
sccs get sub/SConscript
""",
                                   build_str = """\
sccs get aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
sccs get ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
sccs get sub/ddd.in
cat("sub/ddd.out", "sub/ddd.in")
cat("sub/eee.out", "sub/eee.in")
sccs get sub/fff.in
cat("sub/fff.out", "sub/fff.in")
cat("sub/all", ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
"""),
         stderr = """\
sub/SConscript 1.1: 5 lines
aaa.in 1.1: 1 lines
ccc.in 1.1: 1 lines
sub/ddd.in 1.1: 1 lines
sub/fff.in 1.1: 1 lines
""")

test.fail_test(test.read(['work1', 'all']) != "work1/aaa.in\nchecked-out work1/bbb.in\nwork1/ccc.in\n")

# Test transparent checkouts from SCCS files in an SCCS subdirectory.
test.subdir('work2', ['work2', 'SCCS'],
            ['work2', 'sub'], ['work2', 'sub', 'SCCS'])

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work2', file], "work2/%s\n" % file)
    args = "create %s" % file
    test.run(chdir = 'work2', program = sccs, arguments = args, stderr = None)
    test.unlink(['work2', file])
    test.unlink(['work2', ','+file])

test.write(['work2', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
args = "create SConscript"
test.run(chdir = 'work2/sub', program = sccs, arguments = args, stderr = None)
test.unlink(['work2', 'sub', 'SConscript'])
test.unlink(['work2', 'sub', ',SConscript'])

for file in ['ddd.in', 'eee.in', 'fff.in']:
    test.write(['work2', 'sub', file], "work2/sub/%s\n" % file)
    args = "create %s" % file
    test.run(chdir = 'work2/sub', program = sccs, arguments = args, stderr = None)
    test.unlink(['work2', 'sub', file])
    test.unlink(['work2', 'sub', ','+file])

test.write(['work2', 'SConstruct'], """
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
SConscript('sub/SConscript', "env")
""")

test.write(['work2', 'bbb.in'], "checked-out work2/bbb.in\n")

test.write(['work2', 'sub', 'eee.in'], "checked-out work2/sub/eee.in\n")

test.run(chdir = 'work2',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
sccs get sub/SConscript
""",
                                   build_str = """\
sccs get aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
sccs get ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
sccs get sub/ddd.in
cat("sub/ddd.out", "sub/ddd.in")
cat("sub/eee.out", "sub/eee.in")
sccs get sub/fff.in
cat("sub/fff.out", "sub/fff.in")
cat("sub/all", ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
"""),
         stderr = """\
sub/SConscript 1.1: 5 lines
aaa.in 1.1: 1 lines
ccc.in 1.1: 1 lines
sub/ddd.in 1.1: 1 lines
sub/fff.in 1.1: 1 lines
""")

test.fail_test(test.read(['work2', 'all']) != "work2/aaa.in\nchecked-out work2/bbb.in\nwork2/ccc.in\n")

test.pass_test()
