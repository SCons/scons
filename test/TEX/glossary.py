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
Validate that use of \glossary in TeX source files causes SCons to
be aware of the necessary created glossary files.

Test configuration contributed by Robert Managan.
"""

import os
import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')

if not latex:
    test.skip_test("Could not find latex; skipping test(s).\n")

gloss = os.system('kpsewhich glossary.sty')
if not gloss==0:
    test.skip_test("glossary.sty not installed; skipping test(s).\n")

test.write('SConstruct', """\
import os
env = Environment(tools = ['latex'], ENV = {'PATH' : os.environ['PATH']})
env.DVI('gloassary', 'glossary.ltx')
""")

test.write('glossary.ltx', r"""
\documentclass{article}

\usepackage{glossary}

\makeglossary


\begin{document}

A glossary entry \glossary{name={gnu}, description={an animal or software group}}
and another\glossary{name={nix}, description={not sure}}.

\printglossary

\end{document}
""")

test.run(arguments = '.', stderr=None)

test.must_exist(test.workpath('glossary.aux'))
test.must_exist(test.workpath('glossary.fls'))
test.must_exist(test.workpath('glossary.glg'))
test.must_exist(test.workpath('glossary.glo'))
test.must_exist(test.workpath('glossary.gls'))
test.must_exist(test.workpath('glossary.ist'))
test.must_exist(test.workpath('glossary.log'))
test.must_exist(test.workpath('gloassary.dvi'))

test.run(arguments = '-c .')

x = "Could not remove 'glossary.aux': No such file or directory"
test.must_not_contain_any_line(test.stdout(), [x])

test.must_not_exist(test.workpath('glossary.aux'))
test.must_not_exist(test.workpath('glossary.fls'))
test.must_not_exist(test.workpath('glossary.glg'))
test.must_not_exist(test.workpath('glossary.glo'))
test.must_not_exist(test.workpath('glossary.gls'))
test.must_not_exist(test.workpath('glossary.ist'))
test.must_not_exist(test.workpath('glossary.log'))
test.must_not_exist(test.workpath('gloassary.dvi'))

test.pass_test()




# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
