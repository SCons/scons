#!/usr/bin/env python
#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

r"""
Test creation of a Tex document that uses the multibib oackage

Test courtesy Rob Managan.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')
if not latex:
    test.skip_test("Could not find 'latex'; skipping test.\n")

cp = subprocess.run('kpsewhich multibib.sty', shell=True)
if cp.returncode:
    test.skip_test("multibib.sty not installed; skipping test(s).\n")

test.subdir(['src'])


test.write(['SConstruct'], """\
import os

env = Environment()

DVI('multibib.tex')
""")


test.write(['lit.bib'],r"""
@book{Knuth:1991, author = {Knuth, Donald E.}, title = {The TEX book}, publisher = {Addison-Wesley, Reading, Massachusetts}, year = {1991}}
@book{Lamport:1994, author = {Lamport, Leslie}, title = {LATEX: A Document Preparation System}, publisher = {Addison-Wesley, Reading, Massachusetts, 2 edition}, year = {1994} }
@book{Adobe:1985, author = {Adobe System Incorporated},   title = {Postscript Language Tutorial and Cookbook},   publisher = {Addison-Wesley, Reading, Massachusetts},   year = {1985}}

""")

test.write(['multibib.tex'],r"""
\documentclass{article}
\usepackage{multibib}
\newcites{ltex}{\TeX\ and \LaTeX\ References}
\begin{document}
References to the \TeX book \citeltex{Knuth:1991} and to Lamport's \LaTeX\ book, which appears only in the references\nociteltex{Lamport:1994}. Finally a cite to a Postscript tutorial \cite{Adobe:1985}.
\bibliographystyleltex{alpha}
\bibliographyltex{lit}
\renewcommand{\refname}{Postscript References}
\bibliographystyle{plain}
\bibliography{lit}
\end{document}
""")


test.run(arguments = '', stderr=None)


# All (?) the files we expect will get created in the docs directory
files = [
    'ltex.aux',
    'ltex.bbl',
    'ltex.blg',
    'multibib.aux',
    'multibib.bbl',
    'multibib.blg',
    'multibib.fls',
    'multibib.log',
    'multibib.dvi',
]

for f in files:
    test.must_exist([ f])

#test.must_not_exist(['docs/Fig1.pdf',])

test.pass_test()
