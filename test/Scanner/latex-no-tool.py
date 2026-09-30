#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Copy LaTeX sources without a tool when substitution errors are enabled."""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment(tools=[])
AllowSubstExceptions()
for suffix in ('.tex', '.ltx', '.latex'):
    env.Command('target' + suffix, 'source' + suffix, Copy('$TARGET', '$SOURCE'))
""")

for suffix in ('.tex', '.ltx', '.latex'):
    test.write('source' + suffix, 'Source content for ' + suffix + '\n')

test.run(arguments='.')
for suffix in ('.tex', '.ltx', '.latex'):
    test.must_match('target' + suffix, 'Source content for ' + suffix + '\n')
test.up_to_date(arguments='.')

for suffix in ('.tex', '.ltx', '.latex'):
    test.write('source' + suffix, 'Updated source content for ' + suffix + '\n')

test.run(arguments='.')
for suffix in ('.tex', '.ltx', '.latex'):
    test.must_match('target' + suffix, 'Updated source content for ' + suffix + '\n')
test.up_to_date(arguments='.')

test.write('SConstruct', """\
env = Environment(tools=[])
AllowSubstExceptions()
env.Command('invalid.tex', 'source.tex', '$UNKNOWN_COPY_COMMAND $SOURCE $TARGET')
""")
test.run(status=2, stderr=None)
test.must_contain_all_lines(
    test.stderr(), ["name 'UNKNOWN_COPY_COMMAND' is not defined"]
)
test.must_not_exist('invalid.tex')

test.pass_test()
