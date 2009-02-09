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
import sys
import TestSCons

_exe = TestSCons._exe
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('work1', 'work2', 'work3', 'work4')



test.write(['work1', 'SConstruct'], """
import os.path
import stat

env = Environment(XXX='bar%(_exe)s')

def before(env, target, source):
    a=str(target[0])
    f=open(a, "wb")
    f.write("Foo\\n")
    f.close()
    os.chmod(a, os.stat(a)[stat.ST_MODE] | stat.S_IXUSR)
    f=open("before.txt", "ab")
    f.write(os.path.splitext(str(target[0]))[0] + "\\n")
    f.close()

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

test.write(['work1', 'foo.c'], r"""
#include <stdio.h>

int main(void)
{
    printf("foo.c\n");
    return 0;
}
""")

test.write(['work1', 'bar.c'], r"""
#include <stdio.h>

int main(void)
{
    printf("bar.c\n");
    return 0;
}
""")

test.run(chdir='work1', arguments='.')

test.run(program=test.workpath('work1', 'foo'+ _exe), stdout="foo.c\n")
test.run(program=test.workpath('work1', 'bar'+ _exe), stdout="bar.c\n")

test.must_match(['work1', 'before.txt'], "bar\nfoo\n")

after_foo_exe = test.workpath('work1', 'after_foo' + _exe)
test.run(program=after_foo_exe, stdout="foo.c\n")

after_bar_exe = test.workpath('work1', 'after_bar' + _exe)
test.run(program=after_bar_exe, stdout="bar.c\n")




test.write(['work2', 'SConstruct'], """\
def b(target, source, env):
    open(str(target[0]), 'wb').write(env['X'] + '\\n')
env1 = Environment(X='111')
env2 = Environment(X='222')
B = Builder(action = b, env = env1, multi=1)
print "B =", B
print "B.env =", B.env
env1.Append(BUILDERS = {'B' : B})
env2.Append(BUILDERS = {'B' : B})
env3 = env1.Clone(X='333')
print "env1 =", env1
print "env2 =", env2
print "env3 =", env3
f1 = env1.B(File('file1.out'), [])
f2 = env2.B('file2.out', [])
f3 = env3.B('file3.out', [])
def do_nothing(env, target, source):
    pass
AddPreAction(f2[0], do_nothing)
AddPostAction(f3[0], do_nothing)
print "f1[0].builder =", f1[0].builder
print "f2[0].builder =", f2[0].builder
print "f3[0].builder =", f3[0].builder
print "f1[0].env =", f1[0].env
print "f2[0].env =", f2[0].env
print "f3[0].env =", f3[0].env
""")

test.run(chdir='work2', arguments = '.')

test.must_match(['work2', 'file1.out'], "111\n")
test.must_match(['work2', 'file2.out'], "222\n")
test.must_match(['work2', 'file3.out'], "333\n")



test.write(['work3', 'SConstruct'], """\
def pre(target, source, env):
    pass
def post(target, source, env):
    pass
def build(target, source, env):
    open(str(target[0]), 'wb').write('build()\\n')
env = Environment()
AddPreAction('dir', pre)
AddPostAction('dir', post)
env.Command('dir/file', [], build)
""")

test.run(chdir = 'work3', arguments = 'dir/file', stdout=test.wrap_stdout("""\
pre(["dir"], [])
post(["dir"], [])
build(["%s"], [])
""" % os.path.join('dir', 'file')))

test.must_match(['work3', 'dir', 'file'], "build()\n")



test.write(['work4', 'build.py'], """\
import sys
outfp = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    outfp.write(open(f, 'rb').read())
outfp.close()
""")

test.write(['work4', 'SConstruct'], """\
def pre_action(target, source, env):
    open(str(target[0]), 'ab').write('pre %%s\\n' %% source[0])
def post_action(target, source, env):
    open(str(target[0]), 'ab').write('post %%s\\n' %% source[0])
env = Environment()
o = env.Command(['pre-post', 'file.out'],
                'file.in',
                '%(_python_)s build.py ${TARGETS[1]} $SOURCE')
env.AddPreAction(o, pre_action)
env.AddPostAction(o, post_action)
""" % locals())

test.write(['work4', 'file.in'], "file.in\n")

test.run(chdir='work4', arguments='.')

test.must_match(['work4', 'file.out'], "file.in\n")
test.must_match(['work4', 'pre-post'], "pre file.in\npost file.in\n")

test.pass_test()



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
