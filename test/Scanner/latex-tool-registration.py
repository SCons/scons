#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Scan implicit TeX dependencies only after a TeX tool is loaded."""

import TestSCons


test = TestSCons.TestSCons()

# Neither the default keys nor a user-provided suffix enable a tool implicitly.
case = 'no-tool'
test.subdir(case)
test.write([case, 'SConstruct'], """\
env = Environment(tools=[], LATEXSUFFIXES=['.special'])
AllowSubstExceptions()
for suffix in ('.tex', '.ltx', '.latex', '.special'):
    env.Command('copy' + suffix, 'main' + suffix, Copy('$TARGET', '$SOURCE'))
""")
for suffix in ('.tex', '.ltx', '.latex', '.special'):
    test.write([case, 'main' + suffix], '\\input{included}\n')
test.write([case, 'included.tex'], 'First contents\n')
test.run(chdir=case, arguments='.')
test.write([case, 'included.tex'], 'Changed contents\n')
test.up_to_date(chdir=case, arguments='.')

# Each scanner family registers fixed keys, independent of LATEXSUFFIXES.
for tool in ('tex', 'pdflatex'):
    test.subdir(tool)
    test.write([tool, 'SConstruct'], """\
first_tool = %r
env = Environment(tools=[], LATEXSUFFIXES=['.special'])
env.Tool(first_tool)
for suffix in ('.tex', '.ltx', '.latex', '.special'):
    env.Command('copy' + suffix, 'main' + suffix, Copy('$TARGET', '$SOURCE'))
""" % tool)
    for suffix in ('.tex', '.ltx', '.latex', '.special'):
        test.write([tool, 'main' + suffix], '\\input{included}\n')
    test.write([tool, 'included.tex'], 'First contents\n')
    test.run(chdir=tool, arguments='.')
    test.up_to_date(chdir=tool, arguments='.')
    test.write([tool, 'included.tex'], 'Changed contents\n')
    for suffix in ('.tex', '.ltx', '.latex'):
        test.run(chdir=tool, arguments='-q copy' + suffix, status=1)
    test.up_to_date(chdir=tool, arguments='copy.special')
    test.run(chdir=tool, arguments='.')
    test.up_to_date(chdir=tool, arguments='.')

# An earlier custom scanner still takes precedence over the tool's scanner.
test.subdir('custom')
test.write(['custom', 'SConstruct'], """\
env = Environment(tools=[])
custom = Scanner(function=lambda node, env, path: [], skeys=['.tex'])
env.Prepend(SCANNERS=[custom])
env.Tool('tex')
env.Tool('pdflatex')
env.Command('copy.tex', 'main.tex', Copy('$TARGET', '$SOURCE'))
""")
test.write(['custom', 'main.tex'], '\\input{included}\n')
test.write(['custom', 'included.tex'], 'First contents\n')
test.run(chdir='custom', arguments='copy.tex')
test.write(['custom', 'included.tex'], 'Changed contents\n')
test.up_to_date(chdir='custom', arguments='copy.tex')

test.pass_test()
