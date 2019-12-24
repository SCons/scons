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
Validate that we can produce several .pdf at once from several sources.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()


latex = test.where_is('latex')

if latex:

    test.write('SConstruct', """
import os
foo = Environment()
foo['TEXINPUTS'] = ['subdir',os.environ.get('TEXINPUTS', '')]
foo.PDF(source = ['foo.ltx','bar.latex','makeindex.tex','latexi.tex'])
""" % locals())

    latex = r"""
\documentclass{letter}
\begin{document}
This is the %s LaTeX file.
\end{document}
"""

    makeindex =  r"""
\documentclass{report}
\usepackage{makeidx}
\makeindex
\begin{document}
\index{info}
This is the %s LaTeX file.
\printindex{}
\end{document}
"""

    latex1 = r"""
\documentclass{report}
\usepackage{makeidx}
\input{latexinputfile}
\begin{document}
\index{info}
This is the %s LaTeX file.

It has an Index and includes another file.
\include{latexincludefile}
\end{document}
"""

    latex2 = r"""
\makeindex
"""

    latex3 = r"""
\index{include}
This is the include file. mod %s
\printindex{}
"""

    test.write('foo.ltx', latex % 'foo.ltx')

    test.write('bar.latex', latex % 'bar.latex')

    test.write('makeindex.tex',  makeindex % 'makeindex.tex')
    test.write('makeindex.idx',  '')

    test.subdir('subdir')
    test.write('latexi.tex',  latex1 % 'latexi.tex')
    test.write([ 'subdir', 'latexinputfile'], latex2)
    test.write([ 'subdir', 'latexincludefile.tex'], latex3 % '1')

    test.run(stderr = None)
    test.must_not_exist('wrapper.out')
    test.must_exist('foo.pdf')

    test.must_exist('bar.pdf')

    test.must_exist('latexi.pdf')
    test.must_exist('latexi.ind')

    test.write([ 'subdir', 'latexincludefile.tex'], latex3 % '2')
    test.not_up_to_date(arguments = 'latexi.pdf', stderr = None)

    test.run(arguments = '-c', stderr = None)
    test.must_not_exist('latexi.ind')
    test.must_not_exist('latexi.ilg')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
