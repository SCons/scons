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
import stat

import TestSCons

test = TestSCons.TestSCons()

rcs = test.where_is('rcs')
if not rcs:
    print "Could not find RCS, skipping test(s)."
    test.pass_test(1)

ci = test.where_is('ci')
if not ci:
    print "Could not find `ci' command, skipping test(s)."
    test.pass_test(1)

def is_writable(file):
    mode = os.stat(file)[stat.ST_MODE]
    return mode & stat.S_IWUSR



# Test explicit checkouts from local RCS files.
test.subdir('work1', ['work1', 'sub'])

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work1', file], "work1/%s\n" % file)
    args = "-f -t%s %s" % (file, file)
    test.run(chdir = 'work1', program = ci, arguments = args, stderr = None)

test.write(['work1', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
args = "-f -tsub/SConscript sub/SConscript"
test.run(chdir = 'work1', program = ci, arguments = args, stderr = None)

for file in ['ddd.in', 'eee.in', 'fff.in']:
    test.write(['work1', 'sub', file], "work1/sub/%s\n" % file)
    args = "-f -tsub/%s sub/%s" % (file, file)
    test.run(chdir = 'work1', program = ci, arguments = args, stderr = None)

test.no_result(os.path.exists(test.workpath('work1', 'aaa.in')))
test.no_result(os.path.exists(test.workpath('work1', 'bbb.in')))
test.no_result(os.path.exists(test.workpath('work1', 'ccc.in')))

test.no_result(os.path.exists(test.workpath('work1', 'sub', 'SConscript')))

test.no_result(os.path.exists(test.workpath('work1', 'sub', 'ddd.in')))
test.no_result(os.path.exists(test.workpath('work1', 'sub', 'eee.in')))
test.no_result(os.path.exists(test.workpath('work1', 'sub', 'fff.in')))

test.write(['work1', 'SConstruct'], """
import os
ENV = {'PATH' : os.environ['PATH']}
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(ENV=ENV,
                  BUILDERS={'Cat':Builder(action=cat)},
                  RCS_COFLAGS='-q')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.RCS())
SConscript('sub/SConscript', "env")
""")

test.write(['work1', 'bbb.in'], "checked-out work1/bbb.in\n")

test.write(['work1', 'sub', 'eee.in'], "checked-out work1/sub/eee.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
co -q sub/SConscript
""",
                                   build_str = """\
co -q aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
co -q ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
co -q sub/ddd.in
cat(["sub/ddd.out"], ["sub/ddd.in"])
cat(["sub/eee.out"], ["sub/eee.in"])
co -q sub/fff.in
cat(["sub/fff.out"], ["sub/fff.in"])
cat(["sub/all"], ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
"""))

test.must_match(['work1', 'all'], "work1/aaa.in\nchecked-out work1/bbb.in\nwork1/ccc.in\n")

test.must_match(['work1', 'sub', 'all'], "work1/sub/ddd.in\nchecked-out work1/sub/eee.in\nwork1/sub/fff.in\n")

test.fail_test(is_writable(test.workpath('work1', 'sub', 'SConscript')))
test.fail_test(is_writable(test.workpath('work1', 'aaa.in')))
test.fail_test(is_writable(test.workpath('work1', 'ccc.in')))
test.fail_test(is_writable(test.workpath('work1', 'sub', 'ddd.in')))
test.fail_test(is_writable(test.workpath('work1', 'sub', 'fff.in')))



# Test transparent RCS checkouts from an RCS subdirectory.
test.subdir('work2', ['work2', 'RCS'],
            ['work2', 'sub'], ['work2', 'sub', 'RCS'])

for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(['work2', file], "work2/%s\n" % file)
    args = "-f -t%s %s" % (file, file)
    test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

for file in ['ddd.in', 'eee.in', 'fff.in']:
    test.write(['work2', 'sub', file], "work2/sub/%s\n" % file)
    args = "-f -tsub/%s sub/%s" % (file, file)
    test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

test.write(['work2', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
args = "-f -tsub/SConscript sub/SConscript"
test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

test.no_result(os.path.exists(test.workpath('work2', 'aaa.in')))
test.no_result(os.path.exists(test.workpath('work2', 'bbb.in')))
test.no_result(os.path.exists(test.workpath('work2', 'ccc.in')))

test.no_result(os.path.exists(test.workpath('work2', 'sub', 'SConscript')))

test.no_result(os.path.exists(test.workpath('work2', 'sub', 'aaa.in')))
test.no_result(os.path.exists(test.workpath('work2', 'sub', 'bbb.in')))
test.no_result(os.path.exists(test.workpath('work2', 'sub', 'ccc.in')))

test.write(['work2', 'SConstruct'], """
import os
ENV = { 'PATH' : os.environ['PATH'] }
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
DefaultEnvironment()['RCS_COFLAGS'] = '-l'
env = Environment(ENV=ENV, BUILDERS={'Cat':Builder(action=cat)})
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
co -l sub/SConscript
""",
                                   build_str = """\
co -l aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
co -l ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
co -l sub/ddd.in
cat(["sub/ddd.out"], ["sub/ddd.in"])
cat(["sub/eee.out"], ["sub/eee.in"])
co -l sub/fff.in
cat(["sub/fff.out"], ["sub/fff.in"])
cat(["sub/all"], ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
"""),
         stderr = """\
sub/RCS/SConscript,v  -->  sub/SConscript
revision 1.1 (locked)
done
RCS/aaa.in,v  -->  aaa.in
revision 1.1 (locked)
done
RCS/ccc.in,v  -->  ccc.in
revision 1.1 (locked)
done
sub/RCS/ddd.in,v  -->  sub/ddd.in
revision 1.1 (locked)
done
sub/RCS/fff.in,v  -->  sub/fff.in
revision 1.1 (locked)
done
""")

test.must_match(['work2', 'all'], "work2/aaa.in\nchecked-out work2/bbb.in\nwork2/ccc.in\n")

test.must_match(['work2', 'sub', 'all'], "work2/sub/ddd.in\nchecked-out work2/sub/eee.in\nwork2/sub/fff.in\n")

test.fail_test(not is_writable(test.workpath('work2', 'sub', 'SConscript')))
test.fail_test(not is_writable(test.workpath('work2', 'aaa.in')))
test.fail_test(not is_writable(test.workpath('work2', 'ccc.in')))
test.fail_test(not is_writable(test.workpath('work2', 'sub', 'ddd.in')))
test.fail_test(not is_writable(test.workpath('work2', 'sub', 'fff.in')))



# Test transparent RCS checkouts of implicit dependencies.
test.subdir('work3', ['work3', 'RCS'])

test.write(['work3', 'foo.c'], """\
#include "foo.h"
int
main(int argc, char *argv[]) {
    printf(STR);
    printf("work3/foo.c\\n");
}
""")
test.run(chdir = 'work3',
         program = ci,
         arguments = "-f -tfoo.c foo.c",
         stderr = None)

test.write(['work3', 'foo.h'], """\
#define STR     "work3/foo.h\\n"
""")
test.run(chdir = 'work3',
         program = ci,
         arguments = "-f -tfoo.h foo.h",
         stderr = None)

test.write(['work3', 'SConstruct'], """
env = Environment()
env.Program('foo.c')
""")

test.run(chdir='work3', stderr="""\
RCS/foo.c,v  -->  foo.c
revision 1.1
done
RCS/foo.h,v  -->  foo.h
revision 1.1
done
""")



#
test.pass_test()
