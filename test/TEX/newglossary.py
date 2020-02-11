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
Validate that use of \newglossary in TeX source files causes SCons to
be aware of the necessary created glossary files.

Test configuration contributed by Robert Managan.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')

if not latex:
    test.skip_test("Could not find 'latex'; skipping test(s).\n")

cp = subprocess.run('kpsewhich glossaries.sty', shell=True)
if cp.returncode:
    test.skip_test("glossaries.sty not installed; skipping test(s).\n")

test.write('SConstruct', """\
import os
env = Environment()
env.PDF('newglossary', 'newglossary.tex')
""")

test.write('newglossary.tex', r"""
\documentclass{report}

% for glossary
\newlength{\symcol}
\newlength{\symw}
\newcommand{\symtab}[1]{\setlength{\symcol}{1.3cm}\settowidth{\symw}{\ensuremath{#1}}\advance\symcol by -\symw\hspace{\symcol}}
\newcommand{\newsym}[5]{\newglossaryentry{#1}{name=\ensuremath{#2},description={\symtab{#2}{#4}},parent={#5},sort={#3}}}
\newcommand{\newacronymf}[3]{\newglossaryentry{#1}{name={#2},description={#3},first={#2}}}

\usepackage[acronym]{glossaries}
\newglossary[symlog]{symbol}{symi}{symo}{Symbols}
\newglossaryentry{nix}{
  name={Nix},
  description={Version 5}
}
\newglossary[deflog]{definition}{defi}{defo}{Definitions}
\newglossaryentry{defPower}{name=Ddyn,type={definition},description={def of 1 dynamic power consumption},sort={DP}}

\newacronym{gnu}{GNU}{GNU's Not UNIX}
\makeglossaries
\glstoctrue
%\loadglsentries[\acronymtype]{chapters/acronyms}
\loadglsentries[symbol]{symbols}
%\loadglsentries[definition]{defns}


\begin{document}

Here is a symbol: \gls{dynPower} and a glossary entry \gls{mel}

Acronyms \gls{gnu} and glossary entries \gls{nix}.

a definition \gls{defPower}

\glossarystyle{index}
\printglossary[type=symbol]
\printglossary[type=acronym]
\printglossary[type=main]
\printglossary[type=definition]
\glossarystyle{super}

\end{document}""")


test.write('symbols.tex', r"""
\newglossaryentry{mel}{name={Microelectronic Fundamentals},description={\nopostdesc},sort=d}
\newsym{dynPower}{P_{dyn}}{P}{Dynamic power consumption}{mel}

%\newcommand{\newsym}[5]{\newglossaryentry{#1}{name=\ensuremath{#2},description={\symtab{#2}{#4}},parent={#5},sort={#3}}}
""")

test.run(arguments = '.', stderr=None)

test.must_exist(test.workpath('newglossary.acn'))
test.must_exist(test.workpath('newglossary.acr'))
test.must_exist(test.workpath('newglossary.alg'))
test.must_exist(test.workpath('newglossary.aux'))
test.must_exist(test.workpath('newglossary.defi'))
test.must_exist(test.workpath('newglossary.deflog'))
test.must_exist(test.workpath('newglossary.defo'))
test.must_exist(test.workpath('newglossary.fls'))
test.must_exist(test.workpath('newglossary.glg'))
test.must_exist(test.workpath('newglossary.glo'))
test.must_exist(test.workpath('newglossary.gls'))
test.must_exist(test.workpath('newglossary.ist'))
test.must_exist(test.workpath('newglossary.log'))
test.must_exist(test.workpath('newglossary.pdf'))
test.must_exist(test.workpath('newglossary.symi'))
test.must_exist(test.workpath('newglossary.symlog'))
test.must_exist(test.workpath('newglossary.symo'))

test.run(arguments = '-c .')

x = "Could not remove 'newglossary.aux': No such file or directory"
test.must_not_contain_any_line(test.stdout(), [x])

test.must_not_exist(test.workpath('newglossary.acn'))
test.must_not_exist(test.workpath('newglossary.acr'))
test.must_not_exist(test.workpath('newglossary.alg'))
test.must_not_exist(test.workpath('newglossary.defi'))
test.must_not_exist(test.workpath('newglossary.deflog'))
test.must_not_exist(test.workpath('newglossary.defo'))
test.must_not_exist(test.workpath('newglossary.aux'))
test.must_not_exist(test.workpath('newglossary.fls'))
test.must_not_exist(test.workpath('newglossary.glg'))
test.must_not_exist(test.workpath('newglossary.glo'))
test.must_not_exist(test.workpath('newglossary.gls'))
test.must_not_exist(test.workpath('newglossary.ist'))
test.must_not_exist(test.workpath('newglossary.log'))
test.must_not_exist(test.workpath('newglossary.pdf'))
test.must_not_exist(test.workpath('newglossary.symi'))
test.must_not_exist(test.workpath('newglossary.symlog'))
test.must_not_exist(test.workpath('newglossary.symo'))

test.pass_test()




# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
