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

"""
Verify that we execute TeX in a subdirectory (if that's where the document
resides) by checking that all the auxiliary files get created there and
not in the top-level directory. Test this when variantDir is used
Add use of \include and \includegraphics from within the included file

Also check that we find files

Test case courtesy Joel B. Mohler.
"""

import TestSCons

test = TestSCons.TestSCons()

#test.verbose_set(2)

latex = test.where_is('latex')
if not latex:
    test.skip_test("Could not find 'latex'; skipping test.\n")

pdflatex = test.where_is('pdflatex')
if not pdflatex:
    test.skip_test("Could not find 'pdflatex'; skipping test.\n")

test.subdir('docs')
test.subdir(['docs','content'])
test.subdir(['docs','fig'])

test.write('SConstruct', """\
import os
env = Environment(TOOLS = ['tex', 'pdftex'],ENV = {'PATH' : os.environ['PATH']})

env.VariantDir('build', 'docs', duplicate=0)
graph = env.PDF('build/fig/graph.eps')
pdf = env.PDF('build/main.tex')
Depends(pdf, graph)
""")

test.write(['docs','main.tex'],
r"""\documentclass{article}
\usepackage{makeidx}
\usepackage{graphicx}
\makeindex
\begin{document}
Hi there.
\index{info}
\include{content/chapter}
\printindex{}
\end{document}
""")

test.write(['docs','content','chapter.tex'], """\
Sub-document 1
\input{content/subchap}

""")

test.write(['docs','content','subchap.tex'], """\
Sub-chapter 2

""")

test.write(['docs','fig','graph.eps'], """\
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

/gr {grestore} bind def
/gs {gsave} bind def
/rs {restore} bind def
/n {newpath} bind def
/s {stroke} bind def
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

#test.run(arguments = '.')
test.run(arguments = '.', stderr=None, stdout=None)

test.must_exist(['build', 'main.aux'])
test.must_exist(['build', 'main.fls'])
test.must_exist(['build', 'main.idx'])
test.must_exist(['build', 'main.ilg'])
test.must_exist(['build', 'main.ind'])
test.must_exist(['build', 'main.log'])
test.must_exist(['build', 'main.pdf'])

test.must_exist(['build', 'content', 'chapter.aux'])

test.must_not_exist('main.aux')
test.must_not_exist('main.dvi')
test.must_not_exist('main.idx')
test.must_not_exist('main.ilg')
test.must_not_exist('main.ind')
test.must_not_exist('main.log')
test.must_not_exist('main.pdf')

test.must_not_exist(['docs', 'main.aux'])
test.must_not_exist(['docs', 'main.dvi'])
test.must_not_exist(['docs', 'main.idx'])
test.must_not_exist(['docs', 'main.ilg'])
test.must_not_exist(['docs', 'main.ind'])
test.must_not_exist(['docs', 'main.log'])
test.must_not_exist(['docs', 'main.pdf'])

test.must_not_exist(['docs', 'content', 'main.aux'])
test.must_not_exist(['docs', 'content', 'main.dvi'])
test.must_not_exist(['docs', 'content', 'main.idx'])
test.must_not_exist(['docs', 'content', 'main.ilg'])
test.must_not_exist(['docs', 'content', 'main.ind'])
test.must_not_exist(['docs', 'content', 'main.log'])
test.must_not_exist(['docs', 'content', 'main.pdf'])

test.must_not_exist(['docs', 'content', 'chapter.aux'])

test.up_to_date(arguments = '.', stderr=None, stdout=None)

test.write(['docs','content', 'subchap.tex'], """\
Sub-document 2
""")

test.not_up_to_date(arguments = '.')
#test.up_to_date(arguments = '.', stderr=None, stdout=None)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
