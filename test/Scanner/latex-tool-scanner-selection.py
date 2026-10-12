#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Generic Commands use the loaded TeX tool's graphics scanner."""

import TestSCons

test = TestSCons.TestSCons()

# Each tool selects its own graphics; mixed tools keep the first registration.
# Repeated loads must not change the scanner chosen for generic Commands.
for case, tools, selected, other in (
    ('tex', ['tex'], 'figure.eps', 'figure.png'),
    ('latex', ['latex'], 'figure.eps', 'figure.png'),
    ('pdftex', ['pdftex'], 'figure.png', 'figure.eps'),
    ('pdflatex', ['pdflatex'], 'figure.png', 'figure.eps'),
    ('tex-first', ['tex', 'pdflatex'], 'figure.eps', 'figure.png'),
    ('pdflatex-first', ['pdflatex', 'tex'], 'figure.png', 'figure.eps'),
):
    test.subdir(case)
    test.write([case, 'SConstruct'], """\
DefaultEnvironment(tools=[])
env = Environment(tools=%r)
for tool in %r:
    env.Tool(tool)
for suffix in ('.tex', '.ltx', '.latex'):
    env.Command('copy' + suffix, 'main' + suffix, Copy('$TARGET', '$SOURCE'))
""" % (tools, tools + tools))
    for suffix in ('.tex', '.ltx', '.latex'):
        test.write([case, 'main' + suffix], '\\includegraphics{figure}\n')
    test.write([case, 'figure.eps'], 'First EPS contents\n')
    test.write([case, 'figure.png'], 'First PNG contents\n')
    test.run(chdir=case, arguments='.')
    test.up_to_date(chdir=case, arguments='.')

    # Tracking both formats would cause an unnecessary rebuild here.
    test.write([case, other], 'Changed unrelated graphic\n')
    test.up_to_date(chdir=case, arguments='.')

    # Tracking neither format, or the wrong one, would miss these rebuilds.
    test.write([case, selected], 'Changed selected graphic\n')
    for suffix in ('.tex', '.ltx', '.latex'):
        test.run(chdir=case, arguments='-q copy' + suffix, status=1)
    test.run(chdir=case, arguments='.')
    test.up_to_date(chdir=case, arguments='.')

# Loading both kinds in separate environments must keep their choices separate.
test.subdir('isolated')
test.write(['isolated', 'SConstruct'], """\
DefaultEnvironment(tools=[])
tex = Environment(tools=['tex'])
pdf = Environment(tools=['pdflatex'])
tex.Command('tex-copy', 'main.tex', Copy('$TARGET', '$SOURCE'))
pdf.Command('pdf-copy', 'main.tex', Copy('$TARGET', '$SOURCE'))
""")
test.write(['isolated', 'main.tex'], '\\includegraphics{figure}\n')
test.write(['isolated', 'figure.eps'], 'First EPS contents\n')
test.write(['isolated', 'figure.png'], 'First PNG contents\n')
test.run(chdir='isolated', arguments='.')
test.up_to_date(chdir='isolated', arguments='.')
test.write(['isolated', 'figure.eps'], 'Changed EPS contents\n')
test.up_to_date(chdir='isolated', arguments='pdf-copy')
test.run(chdir='isolated', arguments='-q tex-copy', status=1)
test.run(chdir='isolated', arguments='tex-copy')
test.write(['isolated', 'figure.png'], 'Changed PNG contents\n')
test.up_to_date(chdir='isolated', arguments='tex-copy')
test.run(chdir='isolated', arguments='-q pdf-copy', status=1)
test.run(chdir='isolated', arguments='pdf-copy')
test.up_to_date(chdir='isolated', arguments='.')

test.pass_test()
