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
Check that all auxilary files created by LaTeX are properly cleaned by scons -c.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')

if not latex:
    test.skip_test("Could not find 'latex'; skipping test(s).\n")

cp = subprocess.run('kpsewhich comment.sty', shell=True)
if cp.returncode:
    test.skip_test("comment.sty not installed; skipping test(s).\n")

# package hyperref generates foo.out
# package comment generates comment.cut
# todo: add makeindex etc.
input_file = r"""
\documentclass{article}
\usepackage{hyperref}
\usepackage{comment}
\specialcomment{foocom}{}{}
\begin{document}
\begin{foocom}
Hi
\end{foocom}
As stated in \cite{X}, this is a bug-a-boo.
\bibliography{fooref}
\bibliographystyle{plain}
\end{document}
"""

bibfile = r"""
@Article{X,
  author = 	 "Mr. X",
  title = 	 "A determination of bug-a-boo-ness",
  journal =	 "Journal of B.a.B.",
  year = 	 1920,
  volume =	 62,
  pages =	 291
}
"""

test.write('SConstruct', """\
import os
env = Environment(tools = ['tex', 'latex'])
env.DVI( "foo.ltx" )
""")

test.write('foo.ltx', input_file)
test.write('fooref.bib', bibfile)

test.run()

test.must_exist('foo.log')
test.must_exist('foo.aux')
test.must_exist('foo.bbl')
test.must_exist('foo.blg')
test.must_exist('comment.cut')
test.must_exist('foo.out')

test.run(arguments = '-c')

test.must_not_exist('foo.log')
test.must_not_exist('foo.aux')
test.must_not_exist('foo.bbl')
test.must_not_exist('foo.blg')
test.must_not_exist('comment.cut')
test.must_not_exist('foo.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
