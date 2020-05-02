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
Verify that we re-run LaTeX after changing a nested \import. This
checks that recursive implicit dependencies are found correctly.

This is a separate test from the
recursive_scanner_dependencies_input.py test because \input and
\include are handled specially by the PDF builder, whereas \import
dependencies are found only by the scanner.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

pdflatex = test.where_is('pdflatex')

if not pdflatex:
    test.skip_test("Could not find 'pdflatex'; skipping test(s).\n")

cp = subprocess.run('kpsewhich import.sty', shell=True)
if cp.returncode:
    test.skip_test("import.sty not installed; skipping test(s).\n")

test.subdir('subdir')
test.subdir('subdir/subdir2')

test.write(['SConstruct'], """\
env = Environment(tools=['pdftex', 'tex'])
env.PDF('master.tex')
""")

test.write(['master.tex'], r"""
\documentclass{article}
\usepackage{import}
\begin{document}
\subinputfrom{subdir/}{sub1}
\end{document}
""")

test.write(['subdir', 'sub1.tex'], r"""
\subinputfrom{subdir2/}{sub2}
""")

test.write(['subdir', 'subdir2', 'sub2.tex'], r"""
Sub-document 2 content
""")

test.run()

pdf_output_1 = test.read('master.pdf')

# Change sub2.tex, see if master.pdf is changed
test.write(['subdir', 'subdir2', 'sub2.tex'], r"""
Sub-document 2 content -- updated
""")

test.run()

pdf_output_2 = test.read('master.pdf')

# If the PDF file is the same as it was previously, then it didn't
# pick up the change in sub2.tex, so fail.
test.fail_test(pdf_output_1 == pdf_output_2)

# Double-check:  clean everything and rebuild from scratch, which
# should force the PDF file to be the 1982 version.

test.run(arguments='-c')
test.run()

pdf_output_3 = test.read('master.pdf')

# If the PDF file is now different than the second run, modulo the
# creation timestamp and the ID and some other PDF garp, then something
# else odd has happened, so fail.

pdf_output_2 = test.normalize_pdf(pdf_output_2)
pdf_output_3 = test.normalize_pdf(pdf_output_3)

if pdf_output_2 != pdf_output_3:
    import sys
    test.write('master.normalized.2.pdf', pdf_output_2)
    test.write('master.normalized.3.pdf', pdf_output_3)
    sys.stdout.write("***** 2 and 3 are different!\n")
    sys.stdout.write(test.diff_substr(pdf_output_2, pdf_output_3, 80, 80)
                     + '\n')
    sys.stdout.write("Output from run 2:\n")
    sys.stdout.write(test.stdout(-2) + '\n')
    sys.stdout.write("Output from run 3:\n")
    sys.stdout.write(test.stdout() + '\n')
    sys.stdout.flush()
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
