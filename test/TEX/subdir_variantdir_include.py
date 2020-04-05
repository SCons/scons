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
Verify that we execute TeX in a subdirectory (if that's where the document
resides) by checking that all the auxiliary files get created there and
not in the top-level directory. Test this when variantDir is used

Also check that we find files

Test case courtesy Joel B. Mohler.
"""

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')
if not latex:
    test.skip_test("Could not find 'latex'; skipping test.\n")

pdflatex = test.where_is('pdflatex')
if not pdflatex:
    test.skip_test("Could not find 'pdflatex'; skipping test.\n")

test.subdir('docs')
test.subdir(['docs','sub'])
test.subdir(['docs','sub','sub2'])

test.write('SConstruct', """\
import os
env = Environment(TOOLS = ['tex', 'pdftex'])

env.VariantDir('build', 'docs',duplicate=0)
env.SConscript('build/SConscript', exports = ['env'])
""")

test.write(['docs','SConscript'], """\
Import('env')

env.PDF( 'sub/x.tex' )
env.DVI( 'sub/x.tex' )
""")

test.write(['docs','sub', 'x.tex'],
r"""\documentclass{article}
\usepackage{makeidx}
\makeindex
\begin{document}
Hi there.
\index{info}
\include{sub2/y}
\printindex{}
\end{document}
""")

test.write(['docs','sub','sub2','y.tex'], """\
Sub-document 1
""")

#test.run(arguments = '.')
test.run(arguments = '.', stderr=None, stdout=None)

test.must_exist(['build', 'sub', 'x.aux'])
test.must_exist(['build', 'sub', 'x.dvi'])
test.must_exist(['build', 'sub', 'x.fls'])
test.must_exist(['build', 'sub', 'x.idx'])
test.must_exist(['build', 'sub', 'x.ilg'])
test.must_exist(['build', 'sub', 'x.ind'])
test.must_exist(['build', 'sub', 'x.log'])
test.must_exist(['build', 'sub', 'x.pdf'])

test.must_exist(['build', 'sub', 'sub2', 'y.aux'])

test.must_not_exist('x.aux')
test.must_not_exist('x.dvi')
test.must_not_exist('x.idx')
test.must_not_exist('x.ilg')
test.must_not_exist('x.ind')
test.must_not_exist('x.log')
test.must_not_exist('x.pdf')

test.must_not_exist(['docs', 'x.aux'])
test.must_not_exist(['docs', 'x.dvi'])
test.must_not_exist(['docs', 'x.idx'])
test.must_not_exist(['docs', 'x.ilg'])
test.must_not_exist(['docs', 'x.ind'])
test.must_not_exist(['docs', 'x.log'])
test.must_not_exist(['docs', 'x.pdf'])

test.must_not_exist(['docs', 'sub', 'x.aux'])
test.must_not_exist(['docs', 'sub', 'x.dvi'])
test.must_not_exist(['docs', 'sub', 'x.idx'])
test.must_not_exist(['docs', 'sub', 'x.ilg'])
test.must_not_exist(['docs', 'sub', 'x.ind'])
test.must_not_exist(['docs', 'sub', 'x.log'])
test.must_not_exist(['docs', 'sub', 'x.pdf'])

test.must_not_exist(['docs', 'sub', 'sub2', 'y.aux'])

test.up_to_date(arguments = '.', stderr=None, stdout=None)

test.write(['docs','sub', 'sub2', 'y.tex'], """\
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
