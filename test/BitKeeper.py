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
Test fetching source files from BitKeeper.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

bk = test.where_is('bk')
if not bk:
    print "Could not find BitKeeper, skipping test(s)."
    test.no_result(1)

try:
    login = os.getlogin()
except AttributeError:
    try:
        login = os.environ['USER']
    except KeyError:
        login = 'USER'

host = os.uname()[1]

email = "%s@%s" % (login, host)

test.subdir('BitKeeper', 'import', 'work1', 'work2', 'work3')

# Set up the BitKeeper repository.
bkroot = test.workpath('BitKeeper')
bk_conf = test.workpath('bk.conf')

# BitKeeper's licensing restrictions require a configuration file that
# specifies you're not using it multi-user.  This seems to be the
# minimal configuration that satisfies these requirements.
test.write(bk_conf, """\
description:test project 'foo'
logging:none
email:%s
single_user:%s
single_host:%s
""" % (email, login, host))

# Plus, we need to set the external environment variable that gets it to
# shut up and not prompt us to accept the license.
os.environ['BK_LICENSE'] = 'ACCEPTED'

test.run(chdir = bkroot,
         program = bk,
         arguments = 'setup -f -c %s foo' % bk_conf)

test.write(['import', 'aaa.in'], "import/aaa.in\n")
test.write(['import', 'bbb.in'], "import/bbb.in\n")
test.write(['import', 'ccc.in'], "import/ccc.in\n")

test.run(chdir = 'import',
         program = bk,
         arguments = 'import -q -f -tplain . %s/foo' % bkroot)

# Test the most straightforward BitKeeper checkouts, using the module name.
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
env.SourceCode('.', env.BitKeeper(r'%s'))
""" % bkroot)

test.subdir(['work1', 'foo'])
test.write(['work1', 'foo', 'bbb.in'], "work1/foo/bbb.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout("""\
bk get -p %s/foo/aaa.in > foo/aaa.in
cat("aaa.out", "foo/aaa.in")
cat("bbb.out", "foo/bbb.in")
bk get -p %s/foo/ccc.in > foo/ccc.in
cat("ccc.out", "foo/ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
""" % (bkroot, bkroot)),
         stderr = """\
%s/foo/aaa.in 1.1: 1 lines
%s/foo/ccc.in 1.1: 1 lines
""" % (bkroot, bkroot))

test.fail_test(test.read(['work1', 'all']) != "import/aaa.in\nwork1/foo/bbb.in\nimport/ccc.in\n")

# Test BitKeeper checkouts when the module name is specified.
test.write(['work2', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  BITKEEPERFLAGS='-q')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.BitKeeper(r'%s', 'foo'))
""" % bkroot)

test.write(['work2', 'bbb.in'], "work2/bbb.in\n")

test.run(chdir = 'work2',
         arguments = '.',
         stdout = test.wrap_stdout("""\
bk get -q -p %s/foo/aaa.in > aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
bk get -q -p %s/foo/ccc.in > ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
""" % (bkroot, bkroot)))

test.fail_test(test.read(['work2', 'all']) != "import/aaa.in\nwork2/bbb.in\nimport/ccc.in\n")

test.pass_test()
