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
Verify basic operation of the SideEffect() method, using a "log
file" as the side effect "target."
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
def copy(source, target):
    with open(target, "wb") as f, open(source, "rb") as f2:
        f.write(f2.read())

def build(env, source, target):
    copy(str(source[0]), str(target[0]))
    if target[0].side_effects:
        with open(str(target[0].side_effects[0]), "ab") as side_effect:
            side_effect.write(('%%s -> %%s\\n'%%(str(source[0]), str(target[0]))).encode())

Build = Builder(action=build)
env = Environment(BUILDERS={'Build':Build}, SUBDIR='subdir')
env.Build('foo.out', 'foo.in')
env.Build('bar.out', 'bar.in')
env.Build('blat.out', 'blat.in')
SideEffect('log.txt', ['foo.out', 'bar.out', 'blat.out'])
env.Build('log.out', 'log.txt')
env.Build('subdir/baz.out', 'baz.in')
env.SideEffect(r'%s', ['blat.out', r'%s'])
env.Build('subdir/out.out', 'subdir/out.txt')
""" % (os.path.join('$SUBDIR', 'out.txt'),
       os.path.join('$SUBDIR', 'baz.out')))

test.write('foo.in', 'foo.in\n')
test.write('bar.in', 'bar.in\n')
test.write('blat.in', 'blat.in\n')
test.write('baz.in', 'baz.in\n')

test.run(arguments = 'foo.out bar.out', stdout=test.wrap_stdout("""\
build(["foo.out"], ["foo.in"])
build(["bar.out"], ["bar.in"])
"""))

expect = """\
foo.in -> foo.out
bar.in -> bar.out
"""
test.must_match('log.txt', expect)

test.write('bar.in', 'bar.in 2 \n')

test.run(arguments = 'log.txt', stdout=test.wrap_stdout("""\
build(["bar.out"], ["bar.in"])
build(["blat.out"], ["blat.in"])
"""))

expect = expect + """\
bar.in -> bar.out
blat.in -> blat.out
"""
test.must_match('log.txt', expect)

test.write('foo.in', 'foo.in 2 \n')

test.run(arguments = ".", stdout=test.wrap_stdout("""\
build(["foo.out"], ["foo.in"])
build(["log.out"], ["log.txt"])
build(["%s"], ["baz.in"])
build(["%s"], ["%s"])
""" % (os.path.join('subdir', 'baz.out'),
       os.path.join('subdir', 'out.out'),
       os.path.join('subdir', 'out.txt'))))

expect = expect + """\
foo.in -> foo.out
"""

test.must_match('log.txt', expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
