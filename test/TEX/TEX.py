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

r"""
Validate that we can set the TEX string to our own utility, that
the produced .dvi, .aux and .log files get removed by the -c option,
and that we can use this to wrap calls to the real latex utility.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

have_latex = test.where_is('latex')
if not have_latex:
    test.skip_test("Could not find 'latex'; skipping test(s).\n")


test.write('mytex.py', r"""
import sys
import os
import getopt
cmd_opts, arg = getopt.getopt(sys.argv[1:], 'i:r:', [])
base_name = os.path.splitext(arg[0])[0]
with open(arg[0], 'r') as ifp:
    with open(base_name+'.dvi', 'w') as dvi_file, \
         open(base_name+'.aux', 'w') as aux_file, \
         open(base_name+'.log', 'w') as log_file:

        for l in ifp.readlines():
            if l[0] != '\\':
                dvi_file.write(l)
                aux_file.write(l)
                log_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TEX = r'%(_python_)s mytex.py', tools=['tex'])
env.DVI(target = 'test.dvi', source = 'test.tex')
""" % locals())

test.write('test.tex', r"""This is a test.
\end
""")

test.run(arguments = 'test.dvi')

test.must_match('test.dvi', "This is a test.\n")
test.must_match('test.aux', "This is a test.\n")
test.must_match('test.log', "This is a test.\n")

test.run(arguments = '-c test.dvi')

test.must_not_exist('test.dvi')
test.must_not_exist('test.aux')
test.must_not_exist('test.log')



tex = test.where_is('tex')

if tex:

    test.file_fixture('wrapper.py')

    test.write('SConstruct', """
import os
ENV = { 'PATH' : os.environ['PATH'] }
foo = Environment(ENV = ENV)
tex = foo.Dictionary('TEX')
bar = Environment(ENV = ENV, TEX = r'%(_python_)s wrapper.py ' + tex)
foo.DVI(target = 'foo.dvi', source = 'foo.tex')
foo.DVI(target = 'foo-latex.dvi', source = 'foo-latex.tex')
bar.DVI(target = 'bar', source = 'bar.tex')
bar.DVI(target = 'bar-latex', source = 'bar-latex.tex')
foo.DVI('rerun.tex')
foo.DVI('bibtex-test.tex')
""" % locals())

    tex = r"""
This is the %s TeX file.
\end
"""

    latex = r"""
\document%s{letter}
\begin{document}
This is the %s LaTeX file.
\end{document}
"""

    rerun = r"""
\documentclass{article}

\begin{document}

\LaTeX\ will need to run twice on this document to get a reference to section
\ref{sec}.

\section{Next section}
\label{sec}

\end{document}
"""

    bibtex = r"""
\documentclass{article}

\begin{document}

Run \texttt{latex}, then \texttt{bibtex}, then \texttt{latex} twice again \cite{lamport}.

\bibliographystyle{plain}
\bibliography{test}

\end{document}
"""

    bib = r"""
@Book{lamport,
  author =      {L. Lamport},
  title =       {{\LaTeX: A} Document Preparation System},
  publisher =   {Addison-Wesley},
  year =        1994
}
"""

    test.write('foo.tex', tex % 'foo.tex')
    test.write('bar.tex', tex % 'bar.tex')
    test.write('foo-latex.tex', latex % ('style', 'foo-latex.tex'))
    test.write('bar-latex.tex', latex % ('class', 'bar-latex.tex'))
    test.write('rerun.tex', rerun)
    test.write('bibtex-test.tex', bibtex)
    test.write('test.bib', bib)

    test.run(arguments = 'foo.dvi foo-latex.dvi', stderr = None)
    test.must_not_exist('wrapper.out')
    test.must_exist('foo.dvi')
    test.must_exist('foo-latex.dvi')

    test.run(arguments = 'bar.dvi bar-latex.dvi', stderr = None)
    test.must_exist('wrapper.out')
    test.must_exist('bar.dvi')
    test.must_exist('bar-latex.dvi')

    test.run(stderr = None)
    output_lines = test.stdout().split('\n')

    reruns = [x for x in output_lines if x.find('latex -interaction=nonstopmode -recorder rerun.tex') != -1]
    if len(reruns) != 2:
        print("Expected 2 latex calls, got %s:" % len(reruns))
        print('\n'.join(reruns))
        test.fail_test()

    bibtex = [x for x in output_lines if x.find('bibtex bibtex-test') != -1]
    if len(bibtex) != 1:
        print("Expected 1 bibtex call, got %s:" % len(bibtex))
        print('\n'.join(bibtex))
        test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
