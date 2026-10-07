#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Scan implicit TeX dependencies only after a TeX tool is loaded."""

import TestSCons


test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment(tools=[], LATEXSUFFIXES=['.tex'])
env.Command('copy.tex', 'main.tex', Copy('$TARGET', '$SOURCE'))
""")
test.write('main.tex', '\\input{included}\n')
test.write('included.tex', 'First contents\n')
test.run(arguments='copy.tex')
test.up_to_date(arguments='copy.tex')
test.write('included.tex', 'Changed contents\n')
test.up_to_date(arguments='copy.tex')

# Neither the default keys nor a user-provided suffix enable a tool implicitly.
for suffixes in (['.tex', '.ltx', '.latex'], ['.special']):
    case = 'no-tool-' + str(len(suffixes))
    test.subdir(case)
    test.write([case, 'SConstruct'], """\
env = Environment(tools=[], LATEXSUFFIXES=%r)
AllowSubstExceptions()
for suffix in ('.tex', '.ltx', '.latex', '.special'):
    env.Command('copy' + suffix, 'main' + suffix, Copy('$TARGET', '$SOURCE'))
""" % suffixes)
    for suffix in ('.tex', '.ltx', '.latex', '.special'):
        test.write([case, 'main' + suffix], '\\input{included}\n')
    test.write([case, 'included.tex'], 'First contents\n')
    test.run(chdir=case, arguments='.')
    test.write([case, 'included.tex'], 'Changed contents\n')
    test.up_to_date(chdir=case, arguments='.')

# All four tools retain nested Command dependencies and fixed registration keys.
for tool in ('tex', 'latex', 'pdftex', 'pdflatex'):
    test.subdir(tool)
    test.write([tool, 'SConstruct'], """\
env = Environment(tools=[%r], LATEXSUFFIXES=['.special'])
scanner_count = len(env['SCANNERS'])
for tool in ('tex', 'latex', 'pdftex', 'pdflatex', 'tex'):
    env.Tool(tool)
assert len(env['SCANNERS']) == scanner_count
for suffix in ('.tex', '.ltx', '.latex', '.special'):
    env.Command('copy' + suffix, 'main' + suffix, Copy('$TARGET', '$SOURCE'))
""" % tool)
    for suffix in ('.tex', '.ltx', '.latex', '.special'):
        test.write([tool, 'main' + suffix], '\\input{included}\n')
    test.write([tool, 'included.tex'], '\\input{nested}\n')
    test.write([tool, 'nested.tex'], 'First contents\n')
    test.run(chdir=tool, arguments='.')
    test.up_to_date(chdir=tool, arguments='.')
    test.write([tool, 'nested.tex'], 'Changed contents\n')
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
env.Command('copy.tex', 'main.tex', Copy('$TARGET', '$SOURCE'))
""")
test.write(['custom', 'main.tex'], '\\input{included}\n')
test.write(['custom', 'included.tex'], 'First contents\n')
test.run(chdir='custom', arguments='copy.tex')
test.write(['custom', 'included.tex'], 'Changed contents\n')
test.up_to_date(chdir='custom', arguments='copy.tex')

# Populating a scanner cache, loading another environment, and cloning do not
# enable scanning in the original environment.
test.subdir('isolated')
test.write(['isolated', 'SConstruct'], """\
plain = Environment(tools=[], LATEXSUFFIXES=['.tex'])
plain.get_scanner('.tex')
loaded = Environment(tools=['tex'])
clone = plain.Clone(tools=['tex'])
loaded_clone = loaded.Clone()
for name, env in (('plain', plain), ('loaded', loaded),
                  ('clone', clone), ('loaded-clone', loaded_clone)):
    env.Command(name + '.tex', 'main.tex', Copy('$TARGET', '$SOURCE'))
""")
test.write(['isolated', 'main.tex'], '\\input{included}\n')
test.write(['isolated', 'included.tex'], 'First contents\n')
test.run(chdir='isolated', arguments='.')
test.write(['isolated', 'included.tex'], 'Changed contents\n')
test.up_to_date(chdir='isolated', arguments='plain.tex')
for target in ('loaded.tex', 'clone.tex', 'loaded-clone.tex'):
    test.run(chdir='isolated', arguments='-q ' + target, status=1)
test.run(chdir='isolated', arguments='.')
test.up_to_date(chdir='isolated', arguments='.')

# DVI/PDF builders keep their explicit scanners, including graphics selection.
# Copy actions exercise dependency tracking without requiring TeX executables.
for builder, tool, output, graphic, other in (
        ('DVI', 'tex', 'output.dvi', 'figure.eps', 'figure.png'),
        ('PDF', 'pdftex', 'output.pdf', 'figure.png', 'figure.eps')):
    test.subdir(builder)
    test.write([builder, 'SConstruct'], """\
DefaultEnvironment(tools=[])
env = Environment(tools=[%r])
env['BUILDERS'][%r].add_action('.tex', Copy('$TARGET', '$SOURCE'))
env.%s(%r, 'main.tex')
""" % (tool, builder, builder, output))
    test.write([builder, 'main.tex'],
               '\\input{included}\n\\includegraphics{figure}\n')
    test.write([builder, 'included.tex'], '\\input{nested}\n')
    test.write([builder, 'nested.tex'], 'First contents\n')
    test.write([builder, 'figure.eps'], 'First EPS contents\n')
    test.write([builder, 'figure.png'], 'First PNG contents\n')
    test.run(chdir=builder, arguments=output)
    test.up_to_date(chdir=builder, arguments=output)
    test.write([builder, 'nested.tex'], 'Changed contents\n')
    test.run(chdir=builder, arguments='-q ' + output, status=1)
    test.run(chdir=builder, arguments=output)
    test.write([builder, other], 'Changed unrelated graphic\n')
    test.up_to_date(chdir=builder, arguments=output)
    test.write([builder, graphic], 'Changed selected graphic\n')
    test.run(chdir=builder, arguments='-q ' + output, status=1)
    test.run(chdir=builder, arguments=output)

test.pass_test()
