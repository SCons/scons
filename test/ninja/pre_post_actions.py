#!/usr/bin/env python
#
# Copyright The SCons Foundation
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

"""Test that AddPreAction() and AddPostAction() actions run in a ninja build."""

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = TestSCons.NINJA_BINARY

test.dir_fixture('ninja-fixture')

# write.py FILE TEXT [TARGET]: append TEXT to FILE, and whether TARGET exists.
test.write('write.py', """\
import os, sys
with open(sys.argv[1], 'a', newline='\\n') as f:
    f.write(sys.argv[2])
    if len(sys.argv) > 3:
        f.write(' built' if os.path.exists(sys.argv[3]) else ' missing')
    f.write('\\n')
""")

test.write('SConstruct', """\
SetOption('experimental', 'ninja')
DefaultEnvironment(tools=[])
env = Environment()
env.Tool('ninja')

write = r'%(_python_)s write.py'

# Command pre/post actions are folded into the ninja command.
t = env.Command('cmd.out', [], write + ' $TARGET cmd')
env.AddPreAction(t, write + ' cmd_pre.out pre')
env.AddPostAction(t, write + ' cmd_post.out post')

# A linked program keeps its LINK rule, with the commands around it.
# Several actions run in the order they were added, as in SCons.
t = env.Program('foo', 'foo.c')
env.AddPreAction(t, write + ' prog.log pre1 $TARGET')
env.AddPreAction(t, write + ' prog.log pre2 $TARGET')
env.AddPostAction(t, write + ' prog.log post1 $TARGET')
env.AddPostAction(t, [write + ' prog.log post2 $TARGET', write + ' prog.log post3 $TARGET'])

# An archive keeps its AR rule.
t = env.StaticLibrary('bar', 'bar.c')
env.AddPostAction(t, write + ' lib.log post $TARGET')

# A Python function post action needs SCons to build the target.
def post_func(target, source, env):
    with open('func_post.out', 'w') as f:
        f.write('post')

t = env.Command('func.out', [], write + ' $TARGET func')
env.AddPostAction(t, post_func)
""" % locals())


def ninja_file():
    """Return build.ninja with ninja_syntax's line wrapping undone."""
    return ' '.join(test.read('build.ninja', mode='r').replace('$\n', ' ').split())


test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_contain_all_lines(ninja_file(), [
    'build cmd.out: GENERATED_CMD',
    'build foo%(_exe)s: LINK' % locals(),
    'build func.out: TEMPLATE',
])

program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.must_match('cmd_pre.out', 'pre\n')
test.must_match('cmd.out', 'cmd\n')
test.must_match('cmd_post.out', 'post\n')
test.must_match('prog.log', """\
pre1 missing
pre2 missing
post1 built
post2 built
post3 built
""")
test.must_match('lib.log', 'post built\n')
test.must_match('func.out', 'func\n')
test.must_match('func_post.out', 'post')

# Regenerating after a build: SCons now sees the targets as up to date and
# releases their target info, which must not drop the pre/post actions.
for _ in range(2):
    test.run(arguments='--disable-execute-ninja', stdout=None)
    test.must_contain_all_lines(ninja_file(), [
        'cmd_pre.out pre',
        'cmd_post.out post',
        'prog.log pre1',
        'prog.log post3',
        'lib.log post',
        'build func.out: TEMPLATE',
    ])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
