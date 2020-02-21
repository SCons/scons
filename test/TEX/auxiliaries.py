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
Verify that sections of LaTeX output that use auxiliary files (a
bibliography in our configuration below) are consistent when re-run
after modifying the input file.

This checks for a bug that was triggered by the presence of auxiliary
files which were detected by SCons but then removed prior to invoking
TeX, causing the auxiliary sections to be excluded from the output.
That was fixed (courtesy Joel B. Mohler) by making all the relevant
auxiliary files Precious().

Test configuration courtesy Dmitry Mikhin.
"""

import TestSCons

test = TestSCons.TestSCons()

dvips = test.where_is('dvips')
latex = test.where_is('latex')

if not all((dvips, latex)):
    test.skip_test("Could not find 'dvips' and/or 'latex'; skipping test(s).\n")


test.subdir(['docs'])

test.write(['SConstruct'], """\
import os
env = Environment(tools = ['pdftex', 'dvipdf', 'dvips', 'tex', 'latex'],
                  BUILD_DIR = '#build/docs')

# Use 'duplicate=1' because LaTeX toolchain does not work properly for
# input/output files outside of the current directory

env.VariantDir('$BUILD_DIR', 'docs', duplicate=1)
env.SConscript('$BUILD_DIR/SConscript', exports = ['env'])
""")

test.write(['docs', 'SConscript'], """\
Import('env')
envc = env.Clone()

test_dvi = envc.DVI(source='test.tex')
test_ps = envc.PostScript(source='test.tex')
test_pdf = envc.PDF(source='test.tex')

envc.Default(test_dvi)
envc.Default(test_ps)
envc.Default(test_pdf)
""")

test.write(['docs', 'my.bib'], r"""\
@ARTICLE{Mikhin,
   author = "Dmitry {\uppercase{Y}u}. Mikhin",
   title = "Blah!",
   journal = "Some yellow paper",
   year = "2007",
   volume = "7",
   number = "3",
   pages = "1--2"
}
""", mode='w')

tex_input = r"""\documentclass{article}

\title{BUG IN SCONS}

\author{Dmitry Yu. Mikhin}

\begin{document}

\maketitle


\begin{abstract}
\noindent A bug in BibTeX processing?
\end{abstract}


\section{The problem}

Provide a citation here: \cite{Mikhin}.


\bibliography{my}
\bibliographystyle{unsrtnat}

\end{document}
"""

test.write(['docs', 'test.tex'], tex_input)

test.run(stderr=None)

pdf_output_1 = test.read(['build', 'docs', 'test.pdf'])
ps_output_1 = test.read(['build', 'docs', 'test.ps'], mode='r')

# Adding blank lines will cause SCons to re-run the builds, but the
# actual contents of the output files should be the same modulo
# the CreationDate header and some other PDF garp.
test.write(['docs', 'test.tex'], tex_input + "\n\n\n")

test.run(stderr=None)

pdf_output_2 = test.read(['build', 'docs', 'test.pdf'])
ps_output_2 = test.read(['build', 'docs', 'test.ps'], mode='r')



pdf_output_1 = test.normalize_pdf(pdf_output_1)
pdf_output_2 = test.normalize_pdf(pdf_output_2)

if pdf_output_1 != pdf_output_2:
    import sys
    test.write(['build', 'docs', 'test.normalized.1.pdf'], pdf_output_1)
    test.write(['build', 'docs', 'test.normalized.2.pdf'], pdf_output_2)
    sys.stdout.write("***** 1.pdf and 2.pdf are different!\n")
    sys.stdout.write(test.diff_substr(pdf_output_1, pdf_output_2, 80, 80) + '\n')
    sys.stdout.write("Output from run 1:\n")
    sys.stdout.write(test.stdout(-1) + '\n')
    sys.stdout.write("Output from run 2:\n")
    sys.stdout.write(test.stdout() + '\n')
    sys.stdout.flush()
    test.fail_test()

ps_output_1 = test.normalize_ps(ps_output_1)
ps_output_2 = test.normalize_ps(ps_output_2)

if ps_output_1 != ps_output_2:
    import sys
    sys.stdout.write("***** 1.ps and 2.ps are different!\n")
    sys.stdout.write(test.diff_substr(ps_output_1, ps_output_2, 80, 80) + '\n')
    sys.stdout.write("Output from run 1:\n")
    sys.stdout.write(test.stdout(-1) + '\n')
    sys.stdout.write("Output from run 2:\n")
    sys.stdout.write(test.stdout() + '\n')
    sys.stdout.flush()
    test.fail_test()



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
