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
Validate that both .tex and .ltx files can handle a LaTeX-style
bibliography (by calling $BIBTEX to generate a .bbl file) and
correctly re-run to resolve undefined references.
"""

import string

import TestSCons

test = TestSCons.TestSCons()

tex = test.where_is('tex')
latex = test.where_is('latex')

if not tex and not latex:
    test.skip_test("Could not find tex or latex; skipping test(s).\n")

test.subdir('work1', 'work2')


input_file = r"""
\documentclass{article}

\begin{document}
As stated in \cite{X}, this is a bug-a-boo.
\bibliography{fooref}
\bibliographystyle{plain}
\end{document}
"""

bibfile = r"""
@Article{X,
  author = 	 "Mr. X",
  title = 	 "A determination of bug-a-boo-ness",
  journal =	 "Journal of B.a.B.",
  year = 	 1920,
  volume =	 62,
  pages =	 291
}
"""

if tex:

    test.write(['work1', 'SConstruct'], """\
DVI( "foo.tex" )
PDF( "foo.tex" )
""")

    test.write(['work1', 'foo.tex'], input_file)
    test.write(['work1', 'fooref.bib'], bibfile)

    test.run(chdir = 'work1', arguments = '.')

    test.must_exist(['work1', 'foo.bbl'])

    foo_log = test.read(['work1', 'foo.log'])
    if string.find(foo_log, 'undefined references') != -1:
        print 'foo.log contains "undefined references":'
        print foo_log
        test.fail_test(1)

if latex:

    test.write(['work2', 'SConstruct'], """\
DVI( "foo.ltx" )
PDF( "foo.ltx" )
""")

    test.write(['work2', 'foo.ltx'], input_file)
    test.write(['work2', 'fooref.bib'], bibfile)

    test.run(chdir = 'work2', arguments = '.')

    test.must_exist(['work2', 'foo.bbl'])

    foo_log = test.read(['work2', 'foo.log'])
    if string.find(foo_log, 'undefined references') != -1:
        print 'foo.log contains "undefined references":'
        print foo_log
        test.fail_test(1)

test.pass_test()
