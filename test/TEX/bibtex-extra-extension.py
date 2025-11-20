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
Verify that running LaTeX with a file named main.extra.tex pulls the
right bibliography file.
"""

import TestSCons

test = TestSCons.TestSCons()

pdflatex = test.where_is('pdflatex')

if not pdflatex:
    test.skip_test("Could not find 'pdflatex'; skipping test(s).\n")

mains = ["main.tex", "main.extra.tex"]

test.write(["SConstruct"], f"""\
import os
env = Environment(tools=['pdftex', 'tex'])
env.PDF({mains})
""")

body_content = r"""\documentclass{article}
\begin{document}
SCons \cite{scons}!
\bibliography{references}
\bibliographystyle{plain}
\end{document}
"""

for _ in mains:
    test.write(_, body_content)

test.write("references.bib", r"""
@misc{scons,
    title = {SCons},
    url = {https://scons.org},
    language = {en-US},
    urldate = {2025-08-15},
    author = {{SCons} {Foundation}},
    year = {2025},
}
""")

test.run()

pdfs = [test.normalize_pdf(test.read(_[:-3] + "pdf")) for _ in mains]
test.fail_test(pdfs[0] != pdfs[1])
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
