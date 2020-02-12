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
Validate that use of \makeindex in TeX source files causes SCons to be
aware of the necessary created index files.

Test configuration courtesy Joel B. Mohler.
"""

import TestSCons

test = TestSCons.TestSCons()

pdflatex = test.where_is('pdflatex')
makeindex = test.where_is('makeindex')

if not all((pdflatex, makeindex)):
    test.skip_test("Could not find 'pdflatex' and/or 'makeindex'; skipping test(s).\n")

test.write('SConstruct', """\
import os
env = Environment(tools = ['pdftex', 'dvipdf', 'tex', 'latex'])
env.PDF( "no_index.tex" )
env.PDF( "simple.tex" )
""")

test.write('no_index.tex', r"""
\documentclass{article}

\begin{document}
Nothing to see here, move along!
\end{document}
""")

test.write('simple.tex', r"""
\documentclass{article}
\usepackage{makeidx}
\makeindex

\begin{document}
\section{Test 1}
I would like to \index{index} this.

\section{test 2}
I'll index \index{this} as well.

\printindex
\end{document}
""")

# Bleah, makeindex seems to print a bunch of diagnostic stuff on stderr,
# so we have to ignore it.
test.run(arguments = '.', stderr=None)

test.must_exist(test.workpath('simple.aux'))
test.must_exist(test.workpath('simple.idx'))
test.must_exist(test.workpath('simple.ilg'))
test.must_exist(test.workpath('simple.ind'))

test.must_exist(test.workpath('no_index.aux'))

test.must_not_exist(test.workpath('no_index.idx'))
test.must_not_exist(test.workpath('no_index.ilg'))
test.must_not_exist(test.workpath('no_index.ind'))

test.run(arguments = '-c .')

x = "Could not remove 'no_index.aux': No such file or directory"
test.must_not_contain_any_line(test.stdout(), [x])
x = "Could not remove 'simple.aux': No such file or directory"
test.must_not_contain_any_line(test.stdout(), [x])

test.must_not_exist(test.workpath('simple.aux'))
test.must_not_exist(test.workpath('simple.idx'))
test.must_not_exist(test.workpath('simple.ilg'))
test.must_not_exist(test.workpath('simple.ind'))

test.must_not_exist(test.workpath('no_index.aux'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
