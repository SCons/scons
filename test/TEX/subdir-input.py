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
not in the top-level directory.

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

test.subdir('sub')

test.write('SConstruct', """\
import os
env = Environment(TOOLS = ['tex', 'pdftex'])
env.PDF( 'sub/x.tex' )
env.DVI( 'sub/x.tex' )
""")

test.write(['sub', 'x.tex'],
r"""\documentclass{article}
\begin{document}
Hi there.
\input{y}
\end{document}
""")

test.write(['sub', 'y.tex'], """\
Sub-document 1
""")

test.run(arguments = '.')

test.must_exist(['sub', 'x.aux'])
test.must_exist(['sub', 'x.dvi'])
test.must_exist(['sub', 'x.log'])
test.must_exist(['sub', 'x.pdf'])

test.must_not_exist('x.aux')
test.must_not_exist('x.dvi')
test.must_not_exist('x.log')
test.must_not_exist('x.pdf')

test.up_to_date(arguments = '.')

test.write(['sub', 'y.tex'], """\
Sub-document 2
""")

test.not_up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
