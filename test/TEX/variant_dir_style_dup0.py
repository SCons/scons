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
Test creation of a fully-featured TeX document (with bibliography
and index) in a variant_dir.

Also test that the target can be named differently than what
Latex produces by default.

Also test that style files can be found when the tex file is generated
and duplicate=0 is used with variant dir

Test courtesy Rob Managan.
"""

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')
dvipdf = test.where_is('dvipdf')
makeindex = test.where_is('makeindex')
bibtex = test.where_is('bibtex')
if not all((latex, makeindex, bibtex, dvipdf)):
    test.skip_test("Could not find one or more of 'latex', 'makeindex', 'bibtex', or 'dvipdf'; skipping test.\n")

test.subdir(['docs'])


test.write(['SConstruct'], """\
import os

env = Environment(tools = ['tex', 'latex', 'dvipdf'])
copy_latex = Builder(action=Copy('$TARGET', '$SOURCE'),
                     suffix='.tex',
                     src_suffix='.src')
env.Append( BUILDERS={'CopyLatex' : copy_latex} )
#
#  tell latex where to find the style file.
#  these files are normally system files but since the .tex file is generated
#  the latex builder really does not know where the source file that the
#  latex file was built from is located.
#
env['TEXINPUTS'] = 'docs'

Export(['env'])

SConscript(os.path.join('docs', 'SConscript'),
           variant_dir=os.path.join('mybuild','docs'),
           duplicate=0)
""")


test.write(['docs', 'SConscript'], """\
import os
Import('env')

latex_file = env.CopyLatex('test2.src')
test2_dvi  = env.DVI(target='result',source='test2.tex')
test2pdf   = env.PDF(target='pdfoutput.xyz',source=test2_dvi)
""")


test.write(['docs', 'test.bib'], r"""
% This BibTeX bibliography file was created using BibDesk.
% http://bibdesk.sourceforge.net/

@techreport{AnAuthor:2006fk,
	Author = {A. N. Author},
	Date-Added = {2006-11-15 12:51:30 -0800},
	Date-Modified = {2006-11-15 12:52:35 -0800},
	Institution = {none},
	Month = {November},
	Title = {A Test Paper},
	Year = {2006}}
""")

test.write(['docs', 'noweb.sty'], """\
% empty style file

""")


test.write(['docs', 'test2.src'],
r"""
\documentclass{report}

\usepackage{graphicx}
\usepackage{epsfig,color} % for .tex version of figures if we go that way

\usepackage{makeidx}
\usepackage{noweb}
\makeindex

\begin{document}

\title{Report Title}

\author{A. N. Author}

\maketitle

\begin{abstract}
there is no abstract
\end{abstract}

\tableofcontents
\listoffigures

\chapter{Introduction}

The introduction is short.

\index{Acknowledgements}

\section{Acknowledgements}

The Acknowledgements are show as well \cite{AnAuthor:2006fk}.

\index{Getting the Report}

To get a hard copy of this report call me.

All done now.

\bibliographystyle{unsrt}
\bibliography{test}
\newpage

\printindex

\end{document}
""")


# makeindex will write status messages to stderr (grrr...), so ignore it.
test.run(arguments = '.', stderr=None)


# All (?) the files we expect will get created in the variant_dir
# (mybuild/docs) and not in the srcdir (docs).
files = [
    'test2.aux',
    'test2.bbl',
    'test2.blg',
    'test2.idx',
    'test2.ilg',
    'test2.ind',
    'test2.log',
    'test2.toc',
    'result.dvi',
    'pdfoutput.xyz'
]

for f in files:
    test.must_exist(['mybuild', 'docs', f])
    test.must_not_exist(['docs', f])


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
