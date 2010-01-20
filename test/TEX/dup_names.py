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
Test whether duplicate base names are handled correctly. Basically there 
is a directory and a file in the same location with the same basename 
(foo/ and foo.tex). This test verifies \include{foo} includes foo.tex 
and not the directory.

Test configuration courtesy Lennart Sauerbeck.
"""

import TestSCons

test = TestSCons.TestSCons()

pdflatex = test.where_is('pdflatex')

if not pdflatex:
    test.skip_test("Could not find pdflatex; skipping test(s).\n")

test.subdir(['foo'])

test.write('SConstruct', """\
import os
env = Environment(tools = ['pdflatex'],
                  ENV = {'PATH' : os.environ['PATH']})
pdf = env.PDF( "base.ltx" )
""")

test.write('base.ltx', r"""
\documentclass{article}

\begin{document}
\input{foo}
\end{document}
""")

test.write('foo.tex', r"""
Yes, this is a valid document.
""")

test.run(arguments = '.', stderr=None)

test.must_exist(test.workpath('base.aux'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
