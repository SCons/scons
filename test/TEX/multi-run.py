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
Validate that both .tex and .ltx files can handle a LaTeX-style
bibliography (by calling $BIBTEX to generate a .bbl file) and
correctly re-run to resolve undefined references.

Also verifies that package warnings are caught and re-run as needed.
"""

import TestSCons

test = TestSCons.TestSCons()

tex = test.where_is('tex')
latex = test.where_is('latex')
if not all((tex, latex)):
    test.skip_test("Could not find 'tex' and/or 'latex'; skipping test(s).\n")

test.subdir('work1', 'work2', 'work3', 'work4')


input_file = r"""
\documentclass{article}

\begin{document}
As stated in \cite{X}, this is a bug-a-boo.
\bibliography{fooref}
\bibliographystyle{plain}
\end{document}
"""

input_file2 = r"""
\documentclass{article}
\begin{document}
Hello world.
% \bibliography{fooref}
% \bibliographystyle{plain}
\end{document}
"""

input_file3 = r"""
\documentclass{article}
\usepackage{longtable}

\begin{document}
As stated in the last paper, this is a bug-a-boo.
here is some more junk and another table
here is some more junk and another table

\begin{longtable}[l]{rlll}
         Isotope  &\multicolumn{1}{c}{Abar}  &Name\\
\\
         1001    &1.0078    &Proton        &$p$\\
         1002    &2.0141    &Deuterium     &$d$\\
         1003    &3.0170    &Tritium       &$t$\\
         2003    &3.0160    &Helium 3      &He$^3$\\
         2004    &4.0026    &Helium 4      &He$^{4}$\\
\end{longtable}

and a closing comment

 These parameters and arrays are filled in when the parameter \textbf{iftnrates}
   is set to 1:

\begin{longtable}[l]{ll}
\\
\textbf{nxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{pxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{nxxxxx}    &Total number of particles made by xxxxx reaction\\
\textbf{nxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{pxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{nxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{pxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{nxxxxx}    &Total number of particles made by xxxxx reaction\\
\textbf{nxxxx}     &Total number of particles made by xxxx reaction\\
\textbf{pxxxx}     &Total number of particles made by xxxx reaction\\
\\
\textbf{rnxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rpxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rnxxxxx}   &Regional total of particles made by xxxxx reaction\\
\textbf{rnxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rpxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rnxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rpxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rnxxxxx}   &Regional total of particles made by xxxxx reaction\\
\textbf{rnxxxx}    &Regional total of particles made by xxxx reaction\\
\textbf{rpxxxx}    &Regional total of particles made by xxxx reaction\\
\\
\textbf{reactot}(r)     &Total number of reactions for reaction r\\
\textbf{reacreg}(r,ir)  &Total number of reactions for reaction r in region ir\\
\end{longtable}


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
import os
env = Environment(tools = ['pdftex', 'dvipdf', 'tex', 'latex'])
env.DVI( "foo.tex" )
env.PDF( "foo.tex" )
""")

    test.write(['work1', 'foo.tex'], input_file)
    test.write(['work1', 'fooref.bib'], bibfile)

    test.run(chdir = 'work1', arguments = '.')

    test.must_exist(['work1', 'foo.bbl'])

    foo_log = test.read(['work1', 'foo.log'], mode='r')
    test.must_not_contain_any_line(foo_log, ['undefined references'], 'foo.log')

    test.write(['work3', 'SConstruct'], """\
import os
env = Environment(tools = ['tex', 'latex'],
                  ENV = {'PATH' : os.environ['PATH']})
env.DVI( "foo3.tex" )
""")

    test.write(['work3', 'foo3.tex'], input_file3)

    test.run(chdir = 'work3', arguments = '.')

    foo_log = test.read(['work3', 'foo3.log'], mode='r')
    test.must_not_contain_any_line(foo_log, ['Rerun LaTeX'], 'foo3.log')



if latex:

    test.write(['work2', 'SConstruct'], """\
import os
env = Environment(tools = ['dvi', 'pdf', 'pdftex', 'dvipdf', 'pdflatex', 'tex', 'latex'],
                  ENV = {'PATH' : os.environ['PATH']})
env.DVI( "foo.ltx" )
env.PDF( "foo.ltx" )
""")

    test.write(['work2', 'foo.ltx'], input_file)
    test.write(['work2', 'fooref.bib'], bibfile)

    test.run(chdir = 'work2', arguments = '.')

    test.must_exist(['work2', 'foo.bbl'])

    foo_log = test.read(['work2', 'foo.log'], mode='r')
    test.must_not_contain_any_line(foo_log, ['undefined references'], 'foo.log')

    test.write(['work3', 'SConstruct'], """\
import os
env = Environment(tools = ['pdftex', 'dvipdf', 'tex', 'latex'],
                  ENV = {'PATH' : os.environ['PATH']})
env.DVI( "foo3.tex" )
env.PDF( "foo3.tex" )
""")

    test.write(['work3', 'foo3.tex'], input_file3)

    test.run(chdir = 'work3', arguments = '.')

    foo_log = test.read(['work3', 'foo3.log'], mode='r')
    test.must_not_contain_any_line(foo_log, ['Rerun LaTeX'], 'foo3.log')


    test.write(['work4', 'SConstruct'], """\
import os
env = Environment(tools = ['tex', 'latex'],
                  ENV = {'PATH' : os.environ['PATH']})
env.DVI( "foo.ltx" )
""")
    test.write(['work4', 'foo.ltx'], input_file2)

    test.run(chdir = 'work4', arguments = '.')

    test.up_to_date(chdir = 'work4', arguments = '.')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
