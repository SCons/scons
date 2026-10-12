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
env.Command('copy.tex', 'main.tex', Copy('$TARGET', '$SOURCE'))
""" % (tools, tools))
    test.write([case, 'main.tex'], '\\includegraphics{figure}\n')
    test.write([case, 'figure.eps'], 'First EPS contents\n')
    test.write([case, 'figure.png'], 'First PNG contents\n')
    test.run(chdir=case, arguments='.')
    test.up_to_date(chdir=case, arguments='.')

    # Tracking both formats would cause an unnecessary rebuild here.
    test.write([case, other], 'Changed unrelated graphic\n')
    test.up_to_date(chdir=case, arguments='.')

    # Tracking neither format, or the wrong one, would miss these rebuilds.
    test.write([case, selected], 'Changed selected graphic\n')
    test.run(chdir=case, arguments='-q copy.tex', status=1)
    test.run(chdir=case, arguments='.')
    test.up_to_date(chdir=case, arguments='.')

# Cached scanners and clones stay isolated across both tool families.
test.subdir('isolated')
test.write(['isolated', 'SConstruct'], """\
DefaultEnvironment(tools=[])
plain = Environment(tools=[], LATEXSUFFIXES=['.tex'])
plain.get_scanner('.tex')
tex = Environment(tools=['tex'])
pdf_clone = plain.Clone(tools=['pdflatex'])
tex_clone = tex.Clone()
plain.Command('plain-copy', 'main.tex', Copy('$TARGET', '$SOURCE'))
tex.Command('tex-copy', 'main.tex', Copy('$TARGET', '$SOURCE'))
pdf_clone.Command('pdf-copy', 'main.tex', Copy('$TARGET', '$SOURCE'))
tex_clone.Command('tex-clone-copy', 'main.tex', Copy('$TARGET', '$SOURCE'))
""")
test.write(['isolated', 'main.tex'],
           '\\input{included}\n\\includegraphics{figure}\n')
test.write(['isolated', 'included.tex'], '\\input{nested}\n')
test.write(['isolated', 'nested.tex'], 'First contents\n')
test.write(['isolated', 'figure.eps'], 'First EPS contents\n')
test.write(['isolated', 'figure.png'], 'First PNG contents\n')
test.run(chdir='isolated', arguments='.')
test.up_to_date(chdir='isolated', arguments='.')

# One nested input exercises the complete generic Command scanner path.
test.write(['isolated', 'nested.tex'], 'Changed nested contents\n')
test.up_to_date(chdir='isolated', arguments='plain-copy')
for target in ('tex-copy', 'pdf-copy', 'tex-clone-copy'):
    test.run(chdir='isolated', arguments='-q ' + target, status=1)
test.run(chdir='isolated', arguments='.')

test.write(['isolated', 'figure.eps'], 'Changed EPS contents\n')
for target in ('plain-copy', 'pdf-copy'):
    test.up_to_date(chdir='isolated', arguments=target)
for target in ('tex-copy', 'tex-clone-copy'):
    test.run(chdir='isolated', arguments='-q ' + target, status=1)
test.run(chdir='isolated', arguments='tex-copy tex-clone-copy')
test.write(['isolated', 'figure.png'], 'Changed PNG contents\n')
for target in ('plain-copy', 'tex-copy', 'tex-clone-copy'):
    test.up_to_date(chdir='isolated', arguments=target)
test.run(chdir='isolated', arguments='-q pdf-copy', status=1)
test.run(chdir='isolated', arguments='pdf-copy')
test.up_to_date(chdir='isolated', arguments='.')

test.pass_test()
