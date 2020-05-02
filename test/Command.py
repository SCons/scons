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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

python = TestSCons.python
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('expand_chdir_sub')
test.subdir('sub')

build_py = r"""
import sys
with open(sys.argv[1], 'w') as f, open(sys.argv[2], 'r') as infp:
    f.write(infp.read())
"""
test.write('build.py', build_py)
test.write(['expand_chdir_sub', 'subbuild.py'], build_py)

test.write('SConstruct', """
import os
import sys

def buildIt(env, target, source):
    with open(str(target[0]), 'w') as f, open(str(source[0]), 'r') as infp:
        xyzzy = env.get('XYZZY', '')
        if xyzzy:
            f.write(xyzzy + '\\n')
        f.write(infp.read())
    return 0

def sub(env, target, source):
    target = str(target[0])
    source = str(source[0])
    with open(target, 'w') as t:
        for f in sorted(os.listdir(source)):
            with open(os.path.join(source, f), 'r') as s:
                t.write(s.read())
    return 0

def source_scanner(node, env, path, builder):
    print("Source scanner node=", node, "builder =", builder,file=sys.stderr)
    return []

def target_scanner(node, env, path, builder):
    print("Target scanner node=", node, "builder =", builder,file=sys.stderr)
    return []

def factory(node,*lst,**kw):
    print("factory called on:",node,file=sys.stderr)
    return env.File(node)

env = Environment(COPY_THROUGH_TEMP = r'%(_python_)s build.py .tmp $SOURCE' + '\\n' + r'%(_python_)s build.py $TARGET .tmp',
                  EXPAND = '$COPY_THROUGH_TEMP')
env.Command(target = 'f1.out', source = 'f1.in',
            action = buildIt)
env.Command(target = 'f2.out', source = 'f2.in',
            action = r'%(_python_)s build.py temp2 $SOURCES' + '\\n' + r'%(_python_)s build.py $TARGET temp2')
env.Command(target = 'f3.out', source = 'f3.in',
            action = [ [ r'%(_python_)s', 'build.py', 'temp3', '$SOURCES' ],
                       [ r'%(_python_)s', 'build.py', '$TARGET', 'temp3'] ])
Command(target = 'f4.out', source = 'sub', action = sub)
env.Command(target = 'f5.out', source = 'f5.in', action = buildIt,
            XYZZY='XYZZY is set')
env.Command(target = 'f5.out', source = 'f5.in', action = buildIt,
            XYZZY='XYZZY is set')
Command(target = 'f6.out', source = 'f6.in',
        action = r'%(_python_)s build.py f6.out f6.in')
env.Command(target = 'f7.out', source = 'f7.in',
            action = r'%(_python_)s build.py $TARGET $SOURCE')
Command(target = 'f8.out', source = 'f8.in',
        action = r'%(_python_)s build.py $TARGET $SOURCE')
env.Command(target = 'f7s.out', source = 'f7.in',
            action = r'%(_python_)s build.py $TARGET $SOURCE',
            target_scanner=Scanner(lambda node, env, path: target_scanner(node, env, path, "w-env")),
            source_scanner=Scanner(lambda node, env, path: source_scanner(node, env, path, "w-env")))
Command(target = 'f8s.out', source = 'f8.in',
        action = r'%(_python_)s build.py $TARGET $SOURCE',
        target_scanner=Scanner(lambda node, env, path: target_scanner(node, env, path, "wo-env")),
        source_scanner=Scanner(lambda node, env, path: source_scanner(node, env, path, "wo-env")))
Command(target = 'f8f.out', source = 'f8.in',
        action = r'%(_python_)s build.py $TARGET $SOURCE',
        target_factory=factory,
        source_factory=factory
        )
env.Command(target = 'f9.out', source = 'f9.in',
            action = r'$EXPAND')
env.Command(target = '${F10}.out', source = '${F10}.in',
            action = r'%(_python_)s build.py $TARGET $SOURCE',
            F10 = 'f10')
env['SUB'] = 'expand_chdir_sub'
env.Command(target = '$SUB/${F11}.out', source = '$SUB/${F11}.in',
            action = r'%(_python_)s subbuild.py ${F11}.out ${F11}.in',
            chdir = '$SUB',
            F11 = 'f11')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write(['sub', 'f4a'], "sub/f4a\n")
test.write(['sub', 'f4b'], "sub/f4b\n")
test.write(['sub', 'f4c'], "sub/f4c\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")
test.write('f7.in', "f7.in\n")
test.write('f8.in', "f8.in\n")
test.write('f9.in', "f9.in\n")
test.write('f10.in', "f10.in\n")
test.write(['expand_chdir_sub', 'f11.in'], "expand_chdir_sub/f11.in\n")

test_str = r'''factory called on: f8.in
factory called on: f8f.out
Source scanner node= f7.in builder = w-env
Target scanner node= f7s.out builder = w-env
Source scanner node= f8.in builder = wo-env
Target scanner node= f8s.out builder = wo-env
'''

out = test.run(arguments='.',
               stderr=test_str,
               match=TestSCons.match_re_dotall)


test.must_match('f1.out', "f1.in\n", mode='r')
test.must_match('f2.out', "f2.in\n", mode='r')
test.must_match('f3.out', "f3.in\n", mode='r')
test.must_match('f4.out', "sub/f4a\nsub/f4b\nsub/f4c\n", mode='r')
test.must_match('f5.out', "XYZZY is set\nf5.in\n", mode='r')
test.must_match('f6.out', "f6.in\n", mode='r')
test.must_match('f7.out', "f7.in\n", mode='r')
test.must_match('f8.out', "f8.in\n", mode='r')
test.must_match('f7s.out', "f7.in\n", mode='r')
test.must_match('f8s.out', "f8.in\n", mode='r')
test.must_match('f9.out', "f9.in\n", mode='r')
test.must_match('f10.out', "f10.in\n", mode='r')
test.must_match(['expand_chdir_sub', 'f11.out'],
                "expand_chdir_sub/f11.in\n", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
