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
This is an obscure test case. When
  1) a file without a suffix is included in a TeX build and
  2) there is a directory with the same name as that file,
verify that a TypeError is not thrown upon trying to recursively scan
the contents of includes. The TypeError indicates that the directory
with the same name was trying to be scanned as the include file, which
it clearly is not.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

latex = test.where_is('latex')
if not latex:
    test.skip_test("Could not find 'latex'; skipping test.\n")

test.subdir('inc')

test.write('SConstruct', """\
import os

env = Environment()
env.DVI('root.tex')
""")

test.write('root.tex',
r"""\documentclass{article}
\begin{document}
\input{inc}
\end{document}
""")

test.write('inc.tex',
r"""Hello World.
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
