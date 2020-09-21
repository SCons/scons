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
Test creation of a Tex document that uses the biblatex package

Test courtesy Rob Managan.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('pdflatex')
if not latex:
    test.skip_test("Could not find 'pdflatex'; skipping test.\n")

cp = subprocess.run('kpsewhich biblatex.sty', shell=True)
if cp.returncode:
    test.skip_test("biblatex.sty not installed; skipping test(s).\n")


test.write(['SConstruct'], """\
import os
env = Environment(ENV=os.environ)
main_output = env.PDF(target='biblatextest.pdf', source='biblatextest.tex')
""")

test.write(['biblatextest.tex'],r"""
\documentclass{article}

\usepackage{biblatex}

\begin{document}

Hello. This is boring.
And even more boring.

\end{document}
""")


test.run()


# All (?) the files we expect will get created in the docs directory
files = [
    'biblatextest.aux',
    'biblatextest.blg',
    'biblatextest.fls',
    'biblatextest.log',
    'biblatextest.pdf',
    'biblatextest.run.xml',
]

for f in files:
    test.must_exist([ f])

test.run(arguments = '-c .')

for f in files:
    test.must_not_exist([ f])

test.pass_test()

