#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Copy LaTeX sources without a tool when substitution errors are enabled."""

import TestSCons

test = TestSCons.TestSCons()

# Reproduce #4511 with strict substitution and no TeX tool or LATEXSUFFIXES.
test.write('SConstruct', """\
env = Environment(tools=[])
AllowSubstExceptions()
for suffix in ('.tex', '.ltx', '.latex'):
    env.Command('target' + suffix, 'source' + suffix, Copy('$TARGET', '$SOURCE'))
""")

# Cover each suffix that previously enabled the global LaTeX scanner.
for suffix in ('.tex', '.ltx', '.latex'):
    test.write('source' + suffix, 'Source content for ' + suffix + '\n')

# Building must copy all sources without looking up LATEXSUFFIXES.
test.run(arguments='.')
for suffix in ('.tex', '.ltx', '.latex'):
    test.must_match('target' + suffix, 'Source content for ' + suffix + '\n')

test.pass_test()
