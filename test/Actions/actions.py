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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[3], 'rb') as infp:
    f.write((sys.argv[2] + "\n").encode())
    f.write(infp.read())
sys.exit(0)
""")

test.write('SConstruct', """
B = Builder(action = r'%(_python_)s build.py $TARGET 1 $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % locals())

test.write('foo.in', "foo.in\n")

test.run(arguments = '.')

test.must_match('foo.out', '1\nfoo.in\n')

test.up_to_date(arguments = '.')

test.write('SConstruct', """
B = Builder(action = r'%(_python_)s build.py $TARGET 2 $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % locals())

test.run(arguments = '.')

test.must_match('foo.out', '2\nfoo.in\n')

test.up_to_date(arguments = '.')

test.write('SConstruct', """
import subprocess
def func(env, target, source):
    cmd = r'%(_python_)s build.py %%s 3 %%s' %% (' '.join(map(str, target)),
                                       ' '.join(map(str, source)))
    print(cmd)
    cp = subprocess.run(cmd, shell=True)
    return cp.returncode
B = Builder(action = func)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % locals())

test.run(arguments = '.', stderr = None)

test.must_match('foo.out', '3\nfoo.in\n')

test.up_to_date(arguments = '.')

test.write('SConstruct', """
import subprocess
assert 'string' not in globals()
class bld:
    def __init__(self):
        self.cmd = r'%(_python_)s build.py %%s 4 %%s'
    def __call__(self, env, target, source):
        cmd = self.get_contents(env, target, source)
        print(cmd)
        cp = subprocess.run(cmd, shell=True)
        return cp.returncode
    def get_contents(self, env, target, source):
        return self.cmd %% (' '.join(map(str, target)),
                            ' '.join(map(str, source)))
B = Builder(action = bld())
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % locals())

test.run(arguments = '.')

test.must_match('foo.out', '4\nfoo.in\n')

test.up_to_date(arguments = '.')

# Make sure we can expand actions in substitutions.
test.write('SConstruct', """\
def func(env, target, source):
    pass
env = Environment(S = Action('foo'),
                  F = Action(func),
                  L = Action(['arg1', 'arg2']))
print(env.subst('$S'))
print(env.subst('$F'))
print(env.subst('$L'))
""")

test.run(arguments = '-Q .', stdout = """\
foo
func(target, source, env)
arg1
arg2
scons: `.' is up to date.
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
