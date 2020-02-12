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
# This test exercises the AddPreAction() and AddPostAction() API
# functions, which add pre-build and post-build actions to nodes.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import stat

import TestSCons

_exe = TestSCons._exe
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.dir_fixture('pre-post-fixture')

test.write(['work1', 'SConstruct'], """
import os.path
import stat

# DefaultEnvironment(tools=[])
env = Environment(XXX='bar%(_exe)s')

def before(env, target, source):
    a=str(target[0])
    with open(a, "wb") as f:
        f.write(b"Foo\\n")
    os.chmod(a, os.stat(a)[stat.ST_MODE] | stat.S_IXUSR)
    with open("before.txt", "ab") as f:
        f.write((os.path.splitext(str(target[0]))[0] + "\\n").encode())

def after(env, target, source):
    t = str(target[0])
    a = "after_" + t
    fin = open(t, "rb")
    fout = open(a, "wb")
    fout.write(fin.read())
    fout.close()
    fin.close()
    os.chmod(a, os.stat(a)[stat.ST_MODE] | stat.S_IXUSR)

foo = env.Program(source='foo.c', target='foo')
AddPreAction(foo, before)
AddPostAction('foo%(_exe)s', after)

bar = env.Program(source='bar.c', target='bar')
env.AddPreAction('$XXX', before)
env.AddPostAction('$XXX', after)
""" % locals())

test.run(chdir='work1', arguments='.')

test.run(program=test.workpath('work1', 'foo'+ _exe), stdout="foo.c\n")
test.run(program=test.workpath('work1', 'bar'+ _exe), stdout="bar.c\n")

test.must_match(['work1', 'before.txt'], "bar\nfoo\n")

after_foo_exe = test.workpath('work1', 'after_foo' + _exe)
test.run(program=after_foo_exe, stdout="foo.c\n")

after_bar_exe = test.workpath('work1', 'after_bar' + _exe)
test.run(program=after_bar_exe, stdout="bar.c\n")

# work2 start
test.run(chdir='work2', arguments = '.')

test.must_match(['work2', 'file1.out'], "111\n")
test.must_match(['work2', 'file2.out'], "222\n")
test.must_match(['work2', 'file3.out'], "333\n")

# work3 start
test.run(chdir = 'work3', arguments = 'dir/file', stdout=test.wrap_stdout("""\
pre(["dir"], [])
post(["dir"], [])
build(["%s"], [])
""" % os.path.join('dir', 'file')))

test.must_match(['work3', 'dir', 'file'], "build()\n")

# work4 start
test.write(['work4', 'SConstruct'], """\

DefaultEnvironment(tools=[])

def pre_action(target, source, env):
    with open(str(target[0]), 'ab') as f:
        f.write(('pre %%s\\n' %% source[0]).encode())
def post_action(target, source, env):
    with open(str(target[0]), 'ab') as f:
        f.write(('post %%s\\n' %% source[0]).encode())
env = Environment(tools=[])
o = env.Command(['pre-post', 'file.out'],
                'file.in',
                r'%(_python_)s build.py ${TARGETS[1]} $SOURCE')
env.AddPreAction(o, pre_action)
env.AddPostAction(o, post_action)
""" % locals())

test.run(chdir='work4', arguments='.')

test.must_match(['work4', 'file.out'], "file.in\n")
test.must_match(['work4', 'pre-post'], "pre file.in\npost file.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
