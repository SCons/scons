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
Test creation of a fully-featured TeX document (with bibunit
driven bibliographies) in a variant_dir.

Also test that the target can be named differently than what
Latex produces by default.

Test courtesy Rob Managan.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('pdflatex')
bibtex = test.where_is('bibtex')
if not all((latex, bibtex)):
    test.skip_test("Could not find 'latex' and/or 'bibtex'; skipping test.\n")

cp = subprocess.run('kpsewhich bibunits.sty', shell=True)
if cp.returncode:
    test.skip_test("bibunits.sty not installed; skipping test(s).\n")

test.subdir(['src'])


test.write(['SConstruct'], """\
import os

env = Environment()
Export(['env'])

env.SConscript(os.path.join('src', 'SConscript'),
               variant_dir='build',
               duplicate=0)
""")


test.write(['src', 'SConscript'], """\
Import('env')

env.PDF('units.tex')
""")


test.write(['src', 'units.tex'],
r"""
\documentclass{article}
\usepackage{bibunits}
\begin{document}
\begin{bibunit}[plain]
some text \cite{lamport:1994} more text more citations
2
\putbib[units]
\end{bibunit}
some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:1998} more text more citations  2
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:1999} more text more citations 3
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:1998} more text more citations 4
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:2000} more text more citations 5
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:1998} more text more citations 6
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:2001} more text more citations 7
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text more \cite{gnu:2002} text more citations 8
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text more text more citations 9
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:1998} more text more citations 10
\putbib[units]
\end{bibunit}

some text between the units
\begin{bibunit}[abbrv]
some text \cite{gnu:2003} more text more citations 11
\putbib[units]
\end{bibunit}


after the last unit another ref \cite{gnu:1998} and then a second \cite{gnu:2003}
\bibliographystyle{unsrt}
\bibliography{units}
\end{document}
""")


test.write(['src', 'units.bib'], """\
%% This BibTeX bibliography file was created using BibDesk.
%% http://bibdesk.sourceforge.net/

@techreport{gnu:1998,
    Author = {A. N. Author},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper},
    Year = {1998}}
@techreport{gnu:1999,
    Author = {A. N. Author},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper 1},
    Year = {1999}}
@techreport{gnu:2000,
    Author = {A. N. Author},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper 2},
    Year = {2000}}
@techreport{gnu:2001,
    Author = {A. N. Author},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper 3},
    Year = {2001}}
@techreport{gnu:2002,
    Author = {A. N. Author},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper 4},
    Year = {2002}}
@techreport{gnu:2003,
    Author = {A. N. Author},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper 5},
    Year = {2003}}
@techreport{lamport:1994,
    Author = {A. N. Lamport},
    Date-Added = {2006-11-15 12:51:30 -0800},
    Date-Modified = {2006-11-15 12:52:35 -0800},
    Institution = {none},
    Month = {November},
    Title = {A Test Paper},
    Year = {1994}}
""")



#test.run(arguments = '.', stderr=None)
test.run(arguments = '.')


# All (?) the files we expect will get created in the variant_dir
# (build/docs) and not in the srcdir (src).
files = [
'bu.aux',
'bu1.aux',
'bu1.bbl',
'bu1.blg',
'bu10.aux',
'bu10.bbl',
'bu10.blg',
'bu11.aux',
'bu11.bbl',
'bu11.blg',
'bu2.aux',
'bu2.bbl',
'bu2.blg',
'bu3.aux',
'bu3.bbl',
'bu3.blg',
'bu4.aux',
'bu4.bbl',
'bu4.blg',
'bu5.aux',
'bu5.bbl',
'bu5.blg',
'bu6.aux',
'bu6.bbl',
'bu6.blg',
'bu7.aux',
'bu7.bbl',
'bu7.blg',
'bu8.aux',
'bu8.bbl',
'bu8.blg',
'bu9.aux',
'bu9.bbl',
'bu9.blg',
'units.aux',
'units.bbl',
'units.blg',
'units.fls',
'units.log',
'units.pdf',
]

for f in files:
    test.must_exist(['build', f])
    test.must_not_exist(['src', f])

test.run(arguments = '-c')

for f in files:
    test.must_not_exist(['build', f])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
