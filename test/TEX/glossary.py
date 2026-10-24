#!/usr/bin/env python
#
# MIT License
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

r"""
Validate that use of ``\makeglossaries`` in TeX source files causes SCons to
be aware of the necessary created glossary files.

Uses the modern 'glossaries' package (replacement for the obsolete glossary package).

Original test configuration contributed by Robert Managan.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')
if not latex:
    test.skip_test("Could not find 'latex'; skipping test.\n")

makeindex = test.where_is('makeindex')
if not makeindex:
    test.skip_test("Could not find 'makeindex'; skipping test.\n")

cp = subprocess.run('kpsewhich glossaries.sty', shell=True)
if cp.returncode:
    test.skip_test("glossaries.sty not installed; skipping test.\n")

test.write('SConstruct', """\
import os
env = Environment()
env.PDF('glossary', 'glossary.tex')
""")

test.write('glossary.tex', r"""
\documentclass{article}

\usepackage{glossaries}

\newglossaryentry{nix}{
  name={Nix},
  description={Version 5}
}

\makeglossaries


\begin{document}

A glossary entry \gls{nix}.

\printglossary[type=main]

\end{document}
""")

test.run(arguments='.', stderr=None)

test.must_exist(test.workpath('glossary.aux'))
test.must_exist(test.workpath('glossary.fls'))
test.must_exist(test.workpath('glossary.glg'))
test.must_exist(test.workpath('glossary.glo'))
test.must_exist(test.workpath('glossary.ist'))
test.must_exist(test.workpath('glossary.log'))
test.must_exist(test.workpath('glossary.pdf'))

test.run(arguments='-c .')

x = "Could not remove 'glossary.aux': No such file or directory"
test.must_not_contain_any_line(test.stdout(), [x])

test.must_not_exist(test.workpath('glossary.aux'))
test.must_not_exist(test.workpath('glossary.fls'))
test.must_not_exist(test.workpath('glossary.glg'))
test.must_not_exist(test.workpath('glossary.glo'))
test.must_not_exist(test.workpath('glossary.ist'))
test.must_not_exist(test.workpath('glossary.log'))
test.must_not_exist(test.workpath('glossary.pdf'))

test.pass_test()
