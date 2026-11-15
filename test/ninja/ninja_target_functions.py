#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Test target-affecting functions with Ninja tool:
AlwaysBuild, Ignore, AddPreAction, AddPostAction, SideEffect, NoClean, Precious
"""

import os
import TestSCons

test = TestSCons.TestSCons(fail_fast=False)

try:
    import ninja
except ImportError:
    test.skip_test("Could not import ninja Python module.")

_python_ = TestSCons._python_
_exe = TestSCons._exe
ninja_bin = TestSCons.NINJA_BINARY

test.write('SConstruct', """\
SetOption('experimental', 'ninja')
env = Environment(tools=['default', 'ninja'])

# Test AlwaysBuild
t_always = env.Command('always.out', [], [Touch('$TARGET')])
env.AlwaysBuild(t_always)

# Test Ignore
t_ignore = env.Command('ignore.out', 'ignore.in', [Copy('$TARGET', '$SOURCE')])
dep = env.File('ignore.dep')
env.Depends(t_ignore, dep)
env.Ignore(t_ignore, dep)

# Test AddPreAction / AddPostAction
t_actions = env.Command('actions.out', 'actions.in', [Copy('$TARGET', '$SOURCE')])
env.AddPreAction(t_actions, Action('echo PRE_ACTION'))
env.AddPostAction(t_actions, Action('echo POST_ACTION'))
# Force it to not be a simple Copy if it's causing issues with detection
t_actions_2 = env.Command('actions2.out', 'actions.in', [Action('cp $SOURCE $TARGET')])
env.AddPreAction(t_actions_2, Action('echo PRE_ACTION'))
env.AddPostAction(t_actions_2, Action('echo POST_ACTION'))

# Test SideEffect
t_side = env.Command('main.out', 'main.in', 'cp $SOURCE $TARGET && touch side.effect')
env.SideEffect('side.effect', t_side)

# Test NoClean (Currently a gap, but let's see how it behaves)
t_noclean = env.Command('noclean.out', 'noclean.in', [Copy('$TARGET', '$SOURCE')])
env.NoClean(t_noclean)

# Test Precious (Currently a gap)
t_precious = env.Command('precious.out', 'precious.in', [Copy('$TARGET', '$SOURCE')])
env.Precious(t_precious)
""")

test.write('ignore.in', 'ignore.in\n')
test.write('ignore.dep', 'ignore.dep\n')
test.write('actions.in', 'actions.in\n')
test.write('main.in', 'main.in\n')
test.write('noclean.in', 'noclean.in\n')
test.write('precious.in', 'precious.in\n')

# 1. Generate build.ninja
test.run(arguments='build.ninja', status=None)
test.must_exist('build.ninja')

# 2. Verify AlwaysBuild in build.ninja
# It should have ALWAYS_BUILD as an implicit dependency
test.must_contain_all_lines(test.read('build.ninja').decode(), ['build always.out:'])
# We check if ALWAYS_BUILD is in the build line for always.out
with open(test.workpath('build.ninja'), 'r') as f:
    content = f.read()
    if (
        'build always.out: TEMPLATE | ALWAYS_BUILD' not in content
        and 'build always.out: GENERATED_CMD | ALWAYS_BUILD' not in content
    ):
        # It might use a different rule, let's just check for the dependency
        if (
            'always.out' in content
            and 'ALWAYS_BUILD'
            not in content.split('build always.out')[1].split('\n')[0]
        ):
            test.fail_test(
                    message="AlwaysBuild target missing ALWAYS_BUILD dependency in build.ninja"
                )

# 3. Verify Ignore in build.ninja
# ignore.dep should NOT be a dependency of ignore.out
with open(test.workpath('build.ninja'), 'r') as f:
    content = f.read()
    # Find the build line for ignore.out
    lines = content.splitlines()
    for line in lines:
        if line.startswith('build ignore.out:'):
            if 'ignore.dep' in line:
                test.fail_test(message="Ignore dependency still present in build.ninja")

# 4. Verify AddPreAction / AddPostAction in build.ninja
# Should have combined commands with &&
with open(test.workpath('build.ninja'), 'r') as f:
    content = f.read()
    if 'echo PRE_ACTION' not in content or 'echo POST_ACTION' not in content:
        # In some cases, SCons might not use the combined command if it's not
        # a generic shell command.  But we expect it to be here if our
        # implementation is working.
        test.fail_test(message="Pre/Post actions missing from build.ninja")

# 5. Verify SideEffect in build.ninja
# side.effect should be an implicit output
with open(test.workpath('build.ninja'), 'r') as f:
    content = f.read()
    if 'side.effect' not in content:
        test.fail_test(message="SideEffect missing from build.ninja")
    # Ninja syntax for implicit outputs is:
    # build out1 out2 | imp_out1
    # imp_out2 : rule in1 in2 | imp_in1 imp_in2
    # In our implementation it should be in implicit_outputs (after the | on LHS
    found_side_effect = False
    for line in content.splitlines():
        if line.startswith('build main.out') and '| side.effect' in line:
            found_side_effect = True
            break
    if not found_side_effect:
         test.fail_test(message="SideEffect not found as implicit output in build.ninja")

# 6. Run ninja to build everything
test.run(program=ninja_bin, arguments=['-f', 'build.ninja', 'actions.out', 'actions2.out', 'always.out', 'ignore.out', 'main.out', 'noclean.out', 'precious.out'])
test.must_exist('always.out')
test.must_exist('ignore.out')
test.must_exist('actions.out')
test.must_exist('actions2.out')
test.must_exist('main.out')
test.must_exist('side.effect')
test.must_exist('noclean.out')
test.must_exist('precious.out')

# 7. Verify AlwaysBuild actually rebuilds
import time
time.sleep(1.1)
mtime1 = os.path.getmtime(test.workpath('always.out'))
test.run(program=ninja_bin, arguments=['-f', 'build.ninja'])
mtime2 = os.path.getmtime(test.workpath('always.out'))
if mtime1 == mtime2:
    test.fail_test(message="AlwaysBuild target did not rebuild")

# 8. Test NoClean behavior with Ninja
# By default, ninja doesn't know about SCons' NoClean.
# But let's check what happens if we use ninja -t clean.
test.run(program=ninja_bin, arguments=['-f', 'build.ninja', '-t', 'clean'])
# Currently, Ninja will clean it because it's a target in build.ninja.
# If we wanted to support NoClean, we might need to exclude it from the clean rule or something.
# For now, it's a known gap.

test.pass_test()
