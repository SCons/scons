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
Test that --implicit-cache works correctly in conjonction with a
builder that produces multiple targets.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
import os.path

def emitter(target, source, env):
    tgt0 = target[0].get_abspath()
    base,ext = os.path.splitext(tgt0)
    target.append(base + '.b')
    return(target, source)


def source_scan(node, env, path):
    path = node.get_abspath()
    base,ext = os.path.splitext(path)
    return [base + '.lib']


env = Environment(tools=[])
env['BUILDERS']['DualTarget'] = Builder(
    action = Action(
        [ 
            Copy( '$TARGET', '$SOURCE' ), 
            Copy( '${TARGET.base}.b', '$SOURCE' ), 
            ],
        ),
    suffix = '.a',
    src_suffix = '.cpp',
    single_source = True,
    emitter=emitter,
    source_scanner=Scanner(source_scan),
    )

env.Command( 'x.cpp', '', Touch('$TARGET') )
env.Command( 'x.lib', '', Touch('$TARGET') )

env.DualTarget('x.cpp')
""" % locals())

test.must_not_exist('x.cpp')
test.must_not_exist('x.lib')
test.must_not_exist('x.a')
test.must_not_exist('x.b')

# Build everything first.
test.run(arguments = '.')
test.must_exist('x.cpp')
test.must_exist('x.lib')
test.must_exist('x.a')
test.must_exist('x.b')

test.must_contain_all_lines(test.stdout(), ['Copy'])

# Double check that targets are not rebuilt.
test.run(arguments = '.')
test.must_exist('x.cpp')
test.must_exist('x.lib')
test.must_exist('x.a')
test.must_exist('x.b')

test.must_not_contain_any_line(test.stdout(), ['Copy'])

# Double check that targets are not rebuilt even with --implicit-cache
test.run(arguments = '--implicit-cache x.a')
test.must_exist('x.cpp')
test.must_exist('x.lib')
test.must_exist('x.a')
test.must_exist('x.b')

test.must_not_contain_any_line(test.stdout(), ['Copy'])

# Double check that targets are not rebuilt even with --implicit-cache
# a second time.
test.run(arguments = '--implicit-cache x.a')
test.must_exist('x.cpp')
test.must_exist('x.lib')
test.must_exist('x.a')
test.must_exist('x.b')

test.must_not_contain_any_line(test.stdout(), ['Copy'])

# Double check that targets are not rebuilt if we reran without
# --implicit-cache
test.run(arguments = '.')
test.must_exist('x.cpp')
test.must_exist('x.lib')
test.must_exist('x.a')
test.must_exist('x.b')

test.must_not_contain_any_line(test.stdout(), ['Copy'])

# Double check again
test.run(arguments = '.')
test.must_exist('x.cpp')
test.must_exist('x.lib')
test.must_exist('x.a')
test.must_exist('x.b')

test.must_not_contain_any_line(test.stdout(), ['Copy'])

# Then only of the targets using --implicit-cache
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
