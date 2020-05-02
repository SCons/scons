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
Add use of \include and \includegraphics from within the included file

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
test.subdir(['docs','content'])
test.subdir(['docs','fig'])

test.write('SConstruct', """\
import os
env = Environment(TOOLS = ['tex', 'pdftex'])

env.VariantDir('build', 'docs', duplicate=0)
pdf = env.PDF('build/main.tex')
""")

test.write(['docs','main.tex'],
r"""\documentclass{article}
\usepackage{makeidx}
\makeindex
\begin{document}
Hi there.
\index{info}
\include{content/chapter}
\printindex{}
\end{document}
""")

test.write(['docs','content','chapter.tex'],
r"""Sub-document 1
\input{content/subchap}

""")

test.write(['docs','content','subchap.tex'], """\
Sub-chapter 2

""")

#test.run(arguments = '.')
#test.run(arguments = '.', stderr=None, stdout=None)

# next line tests that side effect nodes get disambiguated
# and their directories created in a variantDir before
# the builder tries to populate them and fails
test.run(arguments = 'build/main.pdf', stderr=None, stdout=None)

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
Sub-document 2a
""")

test.not_up_to_date(arguments = '.')
#test.up_to_date(arguments = '.', stderr=None, stdout=None)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
