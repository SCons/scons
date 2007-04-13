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
Verify that we re-run LaTeX after running BibTeX in response to
changes in a .bib file.

Thanks to Rob Managan for the patch that fixed this, and to Joel B. Mohler
for code clean up and packaging the test case.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write(['SConstruct'], """\
PDF( 'bibtest.tex' )
""")

test.write(['bibtest.tex'], r"""
\documentclass{article}
\begin{document}
Learn about cool math in \cite{koblitz:elliptic_curves}.
\bibliographystyle{alpha}
\bibliography{sources}
\end{document}
""")

sources_bib_content = r"""
@book{koblitz:elliptic_curves,
	author    = "Neal Koblitz",
	title     = "Elliptic Curves and Modular Forms",
	year      = "%s",
	publisher = "Springer-Verlag New York Inc."
}
"""



test.write('sources.bib', sources_bib_content % '1981')

test.run()

pdf_output_1 = test.read('bibtest.pdf')



test.write('sources.bib', sources_bib_content % '1982')

test.run()

pdf_output_2 = test.read('bibtest.pdf')

# If the PDF file is the same as it was previously, then it didn't
# pick up the change from 1981 to 1982, so fail.
test.fail_test(pdf_output_1 == pdf_output_2)



# Double-check:  clean everything and rebuild from scratch, which
# should force the PDF file to be the 1982 version.

test.run(arguments = '-c')

test.run()

pdf_output_3 = test.read('bibtest.pdf')

# If the PDF file is now different than the second run, then something
# else odd has happened, so fail.  (Note that this test will be incorrect
# if the tool does something like insert a timestamp in the PDF file.)
test.fail_test(pdf_output_2 != pdf_output_3)



test.pass_test()
