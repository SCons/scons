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

Test courtesy Rob Managan.
"""

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')
dvipdf = test.where_is('dvipdf')
if not all((latex, dvipdf)):
    test.skip_test("Could not find 'latex' and/or 'dvipdf'; skipping test(s).\n")

test.subdir(['docs'])


test.write(['SConstruct'], """\
import os

env = Environment(TOOLS = ['tex', 'latex', 'dvipdf'])
Export(['env'])

SConscript(os.path.join('docs', 'SConscript'),
           variant_dir=os.path.join('mybuild','docs'),
           duplicate=1)
""")


test.write(['docs', 'SConscript'], """\
Import('env')

test_dvi = env.DVI(source='test.tex')
testpdf = env.PDF(source=test_dvi)
""")


test.write(['docs', 'Fig1.ps'], """\
%!PS-Adobe-2.0 EPSF-2.0
%%Title: Fig1.fig
%%Creator: fig2dev Version 3.2 Patchlevel 4
%%CreationDate: Tue Apr 25 09:56:11 2006
%%For: managan@mangrove.llnl.gov (Rob Managan)
%%BoundingBox: 0 0 98 98
%%Magnification: 1.0000
%%EndComments
/$F2psDict 200 dict def
$F2psDict begin
$F2psDict /mtrx matrix put
/col-1 {0 setgray} bind def
/col0 {0.000 0.000 0.000 srgb} bind def

end
save
newpath 0 98 moveto 0 0 lineto 98 0 lineto 98 98 lineto closepath clip newpath
-24.9 108.2 translate
1 -1 scale

/cp {closepath} bind def
/ef {eofill} bind def
/gr {grestore} bind def
/gs {gsave} bind def
/rs {restore} bind def
/l {lineto} bind def
/m {moveto} bind def
/rm {rmoveto} bind def
/n {newpath} bind def
/s {stroke} bind def
/slc {setlinecap} bind def
/slj {setlinejoin} bind def
/slw {setlinewidth} bind def
/srgb {setrgbcolor} bind def
/sc {scale} bind def
/sf {setfont} bind def
/scf {scalefont} bind def
/tr {translate} bind def
 /DrawEllipse {
	/endangle exch def
	/startangle exch def
	/yrad exch def
	/xrad exch def
	/y exch def
	/x exch def
	/savematrix mtrx currentmatrix def
	x y tr xrad yrad sc 0 0 1 startangle endangle arc
	closepath
	savematrix setmatrix
	} def

/$F2psBegin {$F2psDict begin /$F2psEnteredState save def} def
/$F2psEnd {$F2psEnteredState restore end} def

$F2psBegin
10 setmiterlimit
 0.06299 0.06299 sc
%
% Fig objects follow
%
7.500 slw
% Ellipse
n 1170 945 766 766 0 360 DrawEllipse gs col0 s gr

$F2psEnd
rs
""")


test.write(['docs', 'Fig1.tex'],
r"""\begin{picture}(0,0)%
\includegraphics{Fig1.ps}%
\end{picture}%
\setlength{\unitlength}{4144sp}%
%
\begingroup\makeatletter\ifx\SetFigFont\undefined%
\gdef\SetFigFont#1#2#3#4#5{%
  \reset@font\fontsize{#1}{#2pt}%
  \fontfamily{#3}\fontseries{#4}\fontshape{#5}%
  \selectfont}%
\fi\endgroup%
\begin{picture}(1548,1546)(397,-879)
\put(856,-196){\makebox(0,0)[lb]{\smash{\SetFigFont{12}{14.4}{\rmdefault}{\mddefault}{\updefault}{\color[rgb]{0,0,0}center $r_0$}%
}}}
\end{picture}
""")


test.write(['docs', 'test.bib'], """\
%% This BibTeX bibliography file was created using BibDesk.
%% http://bibdesk.sourceforge.net/


%% Created for Rob Managan at 2006-11-15 12:53:16 -0800


%% Saved with string encoding Western (ASCII)



@techreport{Managan:2006fk,
	Author = {Robert Managan},
	Date-Added = {2006-11-15 12:51:30 -0800},
	Date-Modified = {2006-11-15 12:52:35 -0800},
	Institution = {none},
	Month = {November},
	Title = {A Test Paper},
	Year = {2006}}
""")


test.write(['docs', 'test.tex'],
r"""\documentclass{report}

\usepackage{graphicx}
\usepackage{epsfig,color} % for .tex version of figures if we go that way

\usepackage{makeidx}
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

The Acknowledgements are show as well \cite{Managan:2006fk}.

\index{Getting the Report}

To get a hard copy of this report call me.

\begin{figure}[htbp]
\begin{center}
\input{Fig1.tex} % testing figure variant that uses TeX labeling
\caption{Zone and Node indexing}
\label{fig1}
\end{center}
\end{figure}

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
    'test.aux',
    'test.bbl',
    'test.blg',
    'test.dvi',
    'test.idx',
    'test.ilg',
    'test.ind',
    'test.lof',
    'test.log',
    'test.pdf',
    'test.toc',
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
