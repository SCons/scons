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
Test fetching source files from CVS.
"""

import os
import os.path
import stat

import TestSCons

test = TestSCons.TestSCons()

cvs = test.where_is('cvs')
if not cvs:
    print "Could not find CVS, skipping test(s)."
    test.pass_test(1)

def is_writable(file):
    mode = os.stat(file)[stat.ST_MODE]
    return mode & stat.S_IWUSR

test.subdir('CVS', 'import', ['import', 'sub'], 'work1', 'work2')

foo_aaa_in = os.path.join('foo', 'aaa.in')
foo_bbb_in = os.path.join('foo', 'bbb.in')
foo_ccc_in = os.path.join('foo', 'ccc.in')
foo_sub_ddd_in = os.path.join('foo', 'sub', 'ddd.in')
foo_sub_ddd_out = os.path.join('foo', 'sub', 'ddd.out')
foo_sub_eee_in = os.path.join('foo', 'sub', 'eee.in')
foo_sub_eee_out = os.path.join('foo', 'sub', 'eee.out')
foo_sub_fff_in = os.path.join('foo', 'sub', 'fff.in')
foo_sub_fff_out = os.path.join('foo', 'sub', 'fff.out')
foo_sub_all = os.path.join('foo', 'sub', 'all')

sub_SConscript = os.path.join('sub', 'SConscript')
sub_ddd_in = os.path.join('sub', 'ddd.in')
sub_ddd_out = os.path.join('sub', 'ddd.out')
sub_eee_in = os.path.join('sub', 'eee.in')
sub_eee_out = os.path.join('sub', 'eee.out')
sub_fff_in = os.path.join('sub', 'fff.in')
sub_fff_out = os.path.join('sub', 'fff.out')
sub_all = os.path.join('sub', 'all')

# Set up the CVS repository.
cvsroot = test.workpath('CVS')

os.environ['CVSROOT'] = cvsroot
test.run(program = cvs, arguments = 'init')

test.write(['import', 'aaa.in'], "import/aaa.in\n")
test.write(['import', 'bbb.in'], "import/bbb.in\n")
test.write(['import', 'ccc.in'], "import/ccc.in\n")

test.write(['import', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")

test.write(['import', 'sub', 'ddd.in'], "import/sub/ddd.in\n")
test.write(['import', 'sub', 'eee.in'], "import/sub/eee.in\n")
test.write(['import', 'sub', 'fff.in'], "import/sub/fff.in\n")

test.run(chdir = 'import',
         program = cvs,
         arguments = '-q import -m import foo v v-r')

# Test the most straightforward CVS checkouts, using the module name.
test.write(['work1', 'SConstruct'], """
import os
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(ENV = { 'PATH' : os.environ['PATH'] },
                  BUILDERS={'Cat':Builder(action=cat)})
env.Prepend(CVSFLAGS='-Q ')
env.Cat('aaa.out', 'foo/aaa.in')
env.Cat('bbb.out', 'foo/bbb.in')
env.Cat('ccc.out', 'foo/ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.CVS(r'%s'))
SConscript('foo/sub/SConscript', "env")
""" % cvsroot)

test.subdir(['work1', 'foo'])
test.write(['work1', 'foo', 'bbb.in'], "work1/foo/bbb.in\n")

test.subdir(['work1', 'foo', 'sub',])
test.write(['work1', 'foo', 'sub', 'eee.in'], "work1/foo/sub/eee.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
cvs -Q -d %s co foo/sub/SConscript
""" % (cvsroot),
                                   build_str = """\
cvs -Q -d %s co foo/aaa.in
cat("aaa.out", "%s")
cat("bbb.out", "%s")
cvs -Q -d %s co foo/ccc.in
cat("ccc.out", "%s")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
cvs -Q -d %s co foo/sub/ddd.in
cat("%s", "%s")
cat("%s", "%s")
cvs -Q -d %s co foo/sub/fff.in
cat("%s", "%s")
cat("%s", ["%s", "%s", "%s"])
""" % (cvsroot,
       foo_aaa_in,
       foo_bbb_in,
       cvsroot,
       foo_ccc_in,
       cvsroot,
       foo_sub_ddd_out, foo_sub_ddd_in,
       foo_sub_eee_out, foo_sub_eee_in,
       cvsroot,
       foo_sub_fff_out, foo_sub_fff_in,
       foo_sub_all, foo_sub_ddd_out, foo_sub_eee_out, foo_sub_fff_out)))

# Checking things back out of CVS apparently messes with the line
# endings, so read the result files in non-binary mode.

test.fail_test(test.read(['work1', 'all'], 'r') != "import/aaa.in\nwork1/foo/bbb.in\nimport/ccc.in\n")

test.fail_test(test.read(['work1', 'foo', 'sub', 'all'], 'r') != "import/sub/ddd.in\nwork1/foo/sub/eee.in\nimport/sub/fff.in\n")

test.fail_test(not is_writable(test.workpath('work1', 'foo', 'sub', 'SConscript')))
test.fail_test(not is_writable(test.workpath('work1', 'foo', 'aaa.in')))
test.fail_test(not is_writable(test.workpath('work1', 'foo', 'ccc.in')))
test.fail_test(not is_writable(test.workpath('work1', 'foo', 'sub', 'ddd.in')))
test.fail_test(not is_writable(test.workpath('work1', 'foo', 'sub', 'fff.in')))

# Test CVS checkouts when the module name is specified.
test.write(['work2', 'SConstruct'], """
import os
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(ENV = { 'PATH' : os.environ['PATH'] },
                  BUILDERS={'Cat':Builder(action=cat)})
env.Prepend(CVSFLAGS='-q ')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.CVS(r'%s', 'foo'))
SConscript('sub/SConscript', "env")
""" % cvsroot)

test.write(['work2', 'bbb.in'], "work2/bbb.in\n")

test.subdir(['work2', 'sub'])
test.write(['work2', 'sub', 'eee.in'], "work2/sub/eee.in\n")

test.run(chdir = 'work2',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
cvs -q -d %s co -p foo/sub/SConscript > %s
""" % (cvsroot, sub_SConscript),
                                   build_str = """\
cvs -q -d %s co -p foo/aaa.in > aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
cvs -q -d %s co -p foo/ccc.in > ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
cvs -q -d %s co -p foo/sub/ddd.in > %s
cat("%s", "%s")
cat("%s", "%s")
cvs -q -d %s co -p foo/sub/fff.in > %s
cat("%s", "%s")
cat("%s", ["%s", "%s", "%s"])
""" % (cvsroot,
       cvsroot,
       cvsroot, sub_ddd_in,
       sub_ddd_out, sub_ddd_in,
       sub_eee_out, sub_eee_in,
       cvsroot, sub_fff_in,
       sub_fff_out, sub_fff_in,
       sub_all, sub_ddd_out, sub_eee_out, sub_fff_out)))

# Checking things back out of CVS apparently messes with the line
# endings, so read the result files in non-binary mode.

test.fail_test(test.read(['work2', 'all'], 'r') != "import/aaa.in\nwork2/bbb.in\nimport/ccc.in\n")

test.fail_test(test.read(['work2', 'sub', 'all'], 'r') != "import/sub/ddd.in\nwork2/sub/eee.in\nimport/sub/fff.in\n")

test.fail_test(not is_writable(test.workpath('work2', 'sub', 'SConscript')))
test.fail_test(not is_writable(test.workpath('work2', 'aaa.in')))
test.fail_test(not is_writable(test.workpath('work2', 'ccc.in')))
test.fail_test(not is_writable(test.workpath('work2', 'sub', 'ddd.in')))
test.fail_test(not is_writable(test.workpath('work2', 'sub', 'fff.in')))

# Test CVS checkouts from a remote server (SourceForge).
test.subdir(['work3'])

test.write(['work3', 'SConstruct'], """\
import os
env = Environment(ENV = { 'PATH' : os.environ['PATH'] })
env.SourceCode('.', env.CVS(':pserver:anonymous:@cvs.sourceforge.net:/cvsroot/scons'))
env.Install('install', 'scons/SConstruct')
""")

test.run(chdir = 'work3', arguments = '.')

test.fail_test(not os.path.exists(test.workpath('work3', 'install', 'SConstruct')))


test.pass_test()
