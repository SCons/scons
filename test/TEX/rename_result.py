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
Validate that we can rename the output from latex to the
target name provided by the user.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

latex = test.where_is('latex')

if not latex:
    test.skip_test("could not find 'latex'; skipping test\n")

test.write('SConstruct', """
import os
foo = Environment()
foo['TEXINPUTS'] = [ 'subdir', os.environ.get('TEXINPUTS', '') ]
foo.DVI(target = 'foobar.dvi', source = 'foo.ltx')
foo.PDF(target = 'bar.xyz', source = 'bar.ltx')
""" % locals())

test.write('foo.ltx', r"""
\documentclass{letter}
\begin{document}
This is the foo.ltx file.
\end{document}
""")

test.write('bar.ltx', r"""
\documentclass{letter}
\begin{document}
This is the bar.ltx file.
\end{document}
""")

test.run(arguments = '.', stderr = None)

test.must_exist('foobar.dvi')
test.must_not_exist('foo.dvi')

test.must_exist('bar.xyz')
test.must_not_exist('bar.pdf')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
