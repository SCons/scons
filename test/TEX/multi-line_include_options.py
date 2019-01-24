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
When an inclusion's optional argument (enclosed in square brackets:
[]) spans multiple lines (via comment wrapping), ensure that the LaTeX
Scanner doesn't throw an IndexError.

An example of this in the wild is in Thomas Heim's epsdice LaTeX package:
  \includegraphics[height=1.75ex,viewport= 3 4 38 39,%
  clip=true]{\dicefile}%
In epsdice 2007/02/15, v. 2.1.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

latex = test.where_is('latex')

if not latex:
    test.skip_test("Could not find 'latex'; skipping test(s).\n")

test.write('SConstruct', """\
import os
env = Environment()
env.DVI('root.tex')
""")

test.write('root.tex',
r"""\documentclass{article}
\usepackage{graphicx}
\begin{document}
  \includegraphics[height=1.75ex,%
  clip=true]{square}
\end{document}
""")

# Dummy EPS file drawing a square
test.write('square.eps',
r"""%!PS-Adobe-2.0 EPSF-1.2
%%BoundingBox: 0 0 20 20
 newpath
  5 5 moveto
 15 5 lineto
 15 15 lineto
 5 15 lineto
 5  5 lineto
 stroke
%%EOF
""")

test.run(arguments = '.')

test.must_exist(test.workpath('root.dvi'))
test.must_exist(test.workpath('root.log'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:

