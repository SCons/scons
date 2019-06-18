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
Test creation of a Tex document with generated tex files
This checks whether the .bbl file is kept as a side effect
Test creation with pdflatex

Test courtesy Rob Managan.
"""

import TestSCons
import os

test = TestSCons.TestSCons()

pdflatex = test.where_is('latex')
if not pdflatex:
    test.skip_test("Could not find 'pdflatex'; skipping test.\n")

test.subdir(['src'])


test.write(['SConstruct'], """\
import os

env = Environment()

copy_latex = Builder(action=Copy('$TARGET', '$SOURCE'),
                     suffix='.tex',
                     src_suffix='.src')
env.Append( BUILDERS={'CopyLatex' : copy_latex} )

Export(['env'])

VariantDir('pdf', 'src')
SConscript('pdf/SConscript')
""")

test.write(['src','SConscript'],"""
import os
Import('env')

latex_file = env.CopyLatex('main.src')

# latexing
pdf = env.PDF(latex_file)

""")


test.write(['src','literatura.bib'],r"""
@INPROCEEDINGS{Groce03whatwent,
    author = {Alex Groce and Willem Visser},
    title = {What Went Wrong: Explaining Counterexamples},
    booktitle = {In SPIN Workshop on Model Checking of Software},
    year = {2003},
    pages = {121--135}
}

@book{Herlihy08TAOMP,
    author = {Herlihy, Maurice and Shavit, Nir},
    howpublished = {Paperback},
    isbn = {0123705916},
    month = {March},
    publisher = {Morgan Kaufmann},
    title = {The Art of Multiprocessor Programming},
    url = {http://www.worldcat.org/isbn/0123705916},
    year = {2008}
}

@book{Grumberg99MC,
    author = "Edmund M. Clarke and Orna Grumberg and Doron A. Peled",
    title = "Model Checking",
    publisher = "The MIT Press",
    year = "1999",
    address = "Cambridge, Massachusetts"
}

@book{Katoen08PrincMC,
    author = {Baier, Christel and Katoen, Joost-Pieter},
    howpublished = {Hardcover},
    isbn = {026202649X},
    keywords = {books, model\_checking},
    publisher = {The MIT Press},
    title = {Principles of Model Checking},
    url = {http://www.worldcat.org/isbn/026202649X},
    year = {2008}
}


""")

test.write(['src','main.src'],r"""
% vim:ft=context
\documentclass[draft]{report}
\usepackage[utf8]{inputenc}

%\usepackage{algorithm2e}
%\usepackage{amsthm}


\begin{document}


A safety property $\phi$ holds in a Kripke structure $M$ if and only if
$\phi$ holds in every state reachable from $S_0$ \cite{Katoen08PrincMC}.
$\phi$ holds in a state $s\in S$, written as $s \models \phi$, when
$\phi$ holds under valuation corresponding to $L(s)$.

Given the structure and a formula, the model checker can verify it by
visiting all states from the initial state using DFS or BFS and checking
the validity of the formula at every state. When a state is found in
which the formula does not hold, the search is terminated and the path
from initial state to the failing state is presented to the user as a
counterexample. This algorithm may also be called \emph{reachability},
because it enumerates the reachable states and additionally performs the
formula validity.




\section{Comparing correct and incorrect traces in explicit MC}
\label{hd003001}
Alex Groce and Willem Visser implemented an algorithm in the Java
PathFinder model checker which explains violations of safety properties
\cite{Groce03whatwent}. The algorithm finds a set of failing runs

\bibliographystyle{plain}
\bibliography{literatura}


\end{document}

""")


test.run(arguments = '', stderr=None)


# All (?) the files we expect will get created in the docs directory
files = [
    'pdf/main.aux',
    'pdf/main.bbl',
    'pdf/main.blg',
    'pdf/main.fls',
    'pdf/main.log',
    'pdf/main.pdf',
]

for f in files:
    test.must_exist([ f])

#test.must_not_exist(['docs/Fig1.pdf',])

test.pass_test()
