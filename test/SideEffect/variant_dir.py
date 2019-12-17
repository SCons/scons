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
Verify correct operation of SideEffect() when an SConscript()
variant_dir is used.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', 
"""
def copy(source, target):
    with open(target, "wb") as f, open(source, "rb") as f2:
        f.write(f2.read())

def build(env, source, target):
    copy(str(source[0]), str(target[0]))
    if target[0].side_effects:
        with open(str(target[0].side_effects[0]), "ab") as side_effect:
            side_effect.write(('%s -> %s\\n'%(str(source[0]), str(target[0]))).encode())

Build = Builder(action=build)
env = Environment(BUILDERS={'Build':Build})
Export('env')
SConscript('SConscript', variant_dir='build', duplicate=0)""")

test.write('SConscript', """
Import('env')
env.Build('foo.out', 'foo.in')
env.Build('bar.out', 'bar.in')
env.Build('blat.out', 'blat.in')
env.SideEffect('log.txt', ['foo.out', 'bar.out', 'blat.out'])
""")

test.write('foo.in', 'foo.in\n')
test.write('bar.in', 'bar.in\n')

build_foo_out = os.path.join('build', 'foo.out')
build_bar_out = os.path.join('build', 'bar.out')

test.run(arguments = '%s %s' % (build_foo_out, build_bar_out))

expect = """\
foo.in -> %s
bar.in -> %s
""" % (build_foo_out, build_bar_out)

test.must_match('build/log.txt', expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
