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

"""
Verify running LaTeX with a bibliography and a subdirectory named after
the main document does not fail to locate the bibliography file
"""

import TestSCons

test = TestSCons.TestSCons()

pdflatex = test.where_is('pdflatex')

if not pdflatex:
    test.skip_test("Could not find 'pdflatex'; skipping test(s).\n")

test.write(["SConstruct"], """\
env = Environment(tools=['pdftex', 'tex'])
env.PDF('paper.tex')
""")

test.write(["paper.tex"], r"""\documentclass{article}
\usepackage{biblatex}
\addbibresource{paper.bib}
\begin{document}
\input{paper/body.tex}
\printbibliography
\end{document}
""")

test.write("paper.bib", r"""
@misc{scons,
    title = {SCons},
    url = {https://scons.org},
    language = {en-US},
    urldate = {2025-08-15},
    author = {{SCons} {Foundation}},
    year = {2025},
}
""")

test.subdir("paper")

test.write(["paper", "body.tex"], r"SCons \cite{scons}!")

test.run()
test.pass_test()
