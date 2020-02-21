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
Validate that use of \bibliography in TeX source files causes SCons to
be aware of the necessary created bibliography files.

Test configuration contributed by Christopher Drexler.
"""

import TestSCons

test = TestSCons.TestSCons()

dvips = test.where_is('dvips')

if not dvips:
    test.skip_test("Could not find 'dvips'; skipping test(s).\n")

bibtex = test.where_is('bibtex')
if not bibtex:
    test.skip_test("Could not find 'bibtex'; skipping test(s).\n")

have_latex = test.where_is('latex')
if not have_latex:
    test.skip_test("Could not find 'latex'; skipping test(s).\n")


test.write('SConstruct', """\
import os
env = Environment(tools = ['tex', 'latex', 'dvips'])
env.PostScript('simple', 'simple.tex')
""")

test.write('simple.tex', r"""
\documentclass[12pt]{book}

\begin{document}

\chapter{Chapter 1}\label{c:c1}

Test test.\cite{Aloimonos88:AV}

\section{Section 1}\label{s:c1s1}
Test test.

\section{Section 2}\label{s:c1s2}
Test test.

\chapter{Chapter 2}\label{c:c2}

Test test.\cite{Ayache86:HAN}

\section{Section 1}\label{s:c2s1}
Test test.

\section{Section 2}\label{s:c2s2}
Test test.

\bibliographystyle{plain}
\bibliography{simple}
\end{document}
""")

test.write('simple.bib', r"""
@Article{Aloimonos88:AV,
  Author         = {Aloimonos,~J and Weiss,~I. and Bandyopadyay,~A.},
  Title          = {Active Vision},
  Journal        = ijcv,
  Volume         = 2,
  Number         = 3,
  Pages          = {333--356},
  year           = 1988,
}

@Article{Ayache86:HAN,
  Author         = {Ayache, N. and Faugeras, O. D.},
  Title          = {HYPER: A new approach for the recognition and
                   positioning of 2D objects},
  Journal        = pami,
  Volume         = 8,
  Number         = 1,
  Pages          = {44-54},
  year           = 1986,
}
""")

test.run(arguments = '.', stderr=None)

test.must_exist(test.workpath('simple.aux'))
test.must_exist(test.workpath('simple.bbl'))
test.must_exist(test.workpath('simple.blg'))

test.run(arguments = '-c .')

x = "Could not remove 'simple.aux': No such file or directory"
test.must_not_contain_any_line(test.stdout(), [x])

test.must_not_exist(test.workpath('simple.aux'))
test.must_not_exist(test.workpath('simple.bbl'))
test.must_not_exist(test.workpath('simple.blg'))

test.pass_test()


test.write('SConstruct', """\
env = Environment(tools = ['tex', 'latex', 'dvips'])
env.PostScript('d00', 'd00.tex')
""")

test.write('d00.tex', r"""
\documentclass[12pt]{book}

\begin{document}
\include{d-toc}

\include{d01}
\include{d02}
\include{d03}

\include{d-lit}
\end{document}
""")

test.write('d01.tex', r"""
\chapter{Chapter 1}\label{c:c1}

Test test.\cite{Aloimonos88:AV}

\section{Section 1}\label{s:c1s1}
Test test.

\section{Section 2}\label{s:c1s2}
Test test.

\section{Section 3}\label{s:c1s3}
Test test.

\section{Section 4}\label{s:c1s4}
Test test.
""")

test.write('d02.tex', r"""
\chapter{Chapter 2}\label{c:c2}

Test test.\cite{Ayache86:HAN}

\section{Section 1}\label{s:c2s1}
Test test.

\section{Section 2}\label{s:c2s2}
Test test.

\section{Section 3}\label{s:c2s3}
Test test.

\section{Section 4}\label{s:c2s4}
Test test.
""")

test.write('d03.tex', r"""
\chapter{Chapter 3}\label{c:c3}

Test test.

\section{Section 1}\label{s:c3s1}
Test test.

\section{Section 2}\label{s:c3s2}
Test test.

\section{Section 3}\label{s:c3s3}
Test test.

\section{Section 4}\label{s:c3s4}
Test test.
""")

test.write('d-lit.tex', r"""
\bibliographystyle{plain}
\bibliography{d00}
""")

test.write('d-toc.tex', r"""
\tableofcontents
\clearpage
\listoffigures
\clearpage
\listoftables
\cleardoublepage
""")

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
