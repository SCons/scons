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
Test fetching source files from Subversion.
"""

import TestSCons

test = TestSCons.TestSCons()

svn = test.where_is('svn')
if not svn:
    print "Could not find Subversion, skipping test(s)."
    test.pass_test(1)

svnadmin = test.where_is('svnadmin')
if not svn:
    print "Could not find Subversion, skipping test(s)."
    test.pass_test(1)

print "Short-circuiting this test until we support Subversion"
test.pass_test()

test.subdir('Subversion', 'import', ['import', 'sub'], 'work1', 'work2')

# Set up the Subversion repository.
svnrootpath = test.workpath('Subversion')
svnrooturl = 'file://' + svnrootpath

test.run(program = svnadmin, arguments = 'create %s' % svnrootpath)

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
         program = svn,
         arguments = 'import %s . foo -m"import foo"' % svnrooturl)

# Test the most straightforward Subversion checkouts, using the module name.
test.write(['work1', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'foo/aaa.in')
env.Cat('bbb.out', 'foo/bbb.in')
env.Cat('ccc.out', 'foo/ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.Subversion(r'%s'))
SConscript('foo/sub/SConscript', "env")
""" % svnrooturl)

test.subdir(['work1', 'foo'])
test.write(['work1', 'foo', 'bbb.in'], "work1/foo/bbb.in\n")

test.subdir(['work1', 'foo', 'sub'])
test.write(['work1', 'foo', 'sub', 'eee.in'], "work1/foo/sub/eee.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
svn cat %s/foo/sub/SConscript > foo/sub/SConscript
""" % (svnrooturl),
                                   build_str = """\
svn cat %s/foo/aaa.in > foo/aaa.in
cat("aaa.out", "foo/aaa.in")
cat("bbb.out", "foo/bbb.in")
svn cat %s/foo/ccc.in > foo/ccc.in
cat("ccc.out", "foo/ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
svn cat %s/foo/sub/ddd.in > foo/sub/ddd.in
cat("foo/sub/ddd.out", "foo/sub/ddd.in")
cat("foo/sub/eee.out", "foo/sub/eee.in")
svn cat %s/foo/sub/fff.in > foo/sub/fff.in
cat("foo/sub/fff.out", "foo/sub/fff.in")
cat("foo/sub/all", ["foo/sub/ddd.out", "foo/sub/eee.out", "foo/sub/fff.out"])
""" % (svnrooturl, svnrooturl, svnrooturl, svnrooturl)))

test.fail_test(test.read(['work1', 'all']) != "import/aaa.in\nwork1/foo/bbb.in\nimport/ccc.in\n")

test.fail_test(test.read(['work1', 'foo', 'sub', 'all']) != "import/sub/ddd.in\nwork1/foo/sub/eee.in\nimport/sub/fff.in\n")

# Test Subversion checkouts when the module name is specified.
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
env.SourceCode('.', env.Subversion(r'%s', 'foo'))
SConscript('sub/SConscript', "env")
""" % svnrooturl)

test.write(['work2', 'bbb.in'], "work2/bbb.in\n")

test.subdir(['work2', 'sub'])
test.write(['work2', 'sub', 'eee.in'], "work2/sub/eee.in\n")

test.run(chdir = 'work2',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
svn cat %s/foo/sub/SConscript > sub/SConscript
""" % (svnrooturl),
                                   build_str = """\
svn cat %s/foo/aaa.in > aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
svn cat %s/foo/ccc.in > ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
svn cat %s/foo/sub/ddd.in > sub/ddd.in
cat("sub/ddd.out", "sub/ddd.in")
cat("sub/eee.out", "sub/eee.in")
svn cat %s/foo/sub/fff.in > sub/fff.in
cat("sub/fff.out", "sub/fff.in")
cat("sub/all", ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
""" % (svnrooturl, svnrooturl, svnrooturl, svnrooturl)))

test.fail_test(test.read(['work2', 'all']) != "import/aaa.in\nwork2/bbb.in\nimport/ccc.in\n")

test.fail_test(test.read(['work2', 'sub', 'all']) != "import/sub/ddd.in\nwork2/sub/eee.in\nimport/sub/fff.in\n")

test.pass_test()
