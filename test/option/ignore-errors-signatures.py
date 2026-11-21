#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Ignored failures must not become successful signatures or shared cache entries."""

import TestSCons

test = TestSCons.TestSCons()

for index, options in enumerate(
    ('-i', '--ignore-errors --cache-force', '-i -j 2 --cache-force')
):
    work = f'case{index}'
    test.subdir(work)
    test.write(
        [work, 'SConstruct'],
        """\
import os

DefaultEnvironment(tools=[])
env = Environment(tools=[])
env.CacheDir('cache')

def generate(target, source, env):
    with open('attempts', 'a') as log:
        log.write('attempt\\n')
    for node in target:
        with open(str(node), 'w') as output:
            output.write('generated\\n')
    return 1 if os.path.exists('fail') else 0

def copy(target, source, env):
    with open(str(source[0])) as input:
        contents = input.read()
    with open(str(target[0]), 'w') as output:
        output.write(contents)

outputs = env.Command(['first', 'second'], 'input', generate)
env.Command('dependent', outputs[1], copy)
env.Command('independent', 'input', copy)
""",
    )
    test.write([work, 'input'], 'source\n')
    test.write([work, 'fail'], '')

    # Ignore the failure but still run independent and dependent builders.
    test.run(chdir=work, arguments=options, stderr=None)
    test.fail_test('Error 1' not in test.stderr())
    test.must_match([work, 'dependent'], 'generated\n', mode='r')
    test.must_match([work, 'independent'], 'source\n', mode='r')
    test.must_match([work, 'attempts'], 'attempt\n', mode='r')

    # A subsequent build must retry the failed action and report its failure.
    test.run(chdir=work, arguments='first second', status=2, stderr=None)
    test.fail_test('Error 1' not in test.stderr())
    test.must_match([work, 'attempts'], 'attempt\nattempt\n', mode='r')

    # Removing both outputs must not let a later build retrieve failed results.
    test.unlink([work, 'first'])
    test.unlink([work, 'second'])
    test.run(chdir=work, arguments='first second', status=2, stderr=None)
    test.fail_test('Retrieved' in test.stdout())
    test.must_match([work, 'attempts'], 'attempt\nattempt\nattempt\n', mode='r')

    # Once the builder succeeds, signatures and cache population work as usual.
    test.unlink([work, 'fail'])
    test.run(chdir=work, arguments='first second')
    test.must_match(
        [work, 'attempts'], 'attempt\nattempt\nattempt\nattempt\n', mode='r'
    )
    test.up_to_date(chdir=work, arguments='first')
    test.up_to_date(chdir=work, arguments='second')
    test.unlink([work, 'first'])
    test.unlink([work, 'second'])
    test.run(chdir=work, arguments='first second')
    test.fail_test('Retrieved' not in test.stdout())
    test.must_match(
        [work, 'attempts'], 'attempt\nattempt\nattempt\nattempt\n', mode='r'
    )
    test.must_match([work, 'first'], 'generated\n', mode='r')
    test.must_match([work, 'second'], 'generated\n', mode='r')

    # A failed rebuild must not overwrite a previous successful build record.
    test.write([work, 'input'], 'changed source\n')
    test.write([work, 'fail'], '')
    test.run(chdir=work, arguments=options, stderr=None)
    test.must_match([work, 'attempts'], 'attempt\n' * 5, mode='r')
    test.run(chdir=work, arguments='first second', status=2, stderr=None)
    test.must_match([work, 'attempts'], 'attempt\n' * 6, mode='r')
    test.unlink([work, 'first'])
    test.unlink([work, 'second'])
    test.run(chdir=work, arguments='first second', status=2, stderr=None)
    test.fail_test('Retrieved' in test.stdout())
    test.must_match([work, 'attempts'], 'attempt\n' * 7, mode='r')

test.pass_test()
