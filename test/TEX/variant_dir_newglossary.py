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
Validate the use of \newglossary in TeX source files in conjunction
with variant_dir.

Test configuration contributed by Kendrick Boyd.
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


test.subdir(['src'])

test.write(['SConstruct'], r"""
import os

env = Environment(TOOLS = ['tex', 'latex'])
Export(['env'])

SConscript(os.path.join('src','SConscript'), variant_dir='build/', duplicate=1)
""")

test.write(['src', 'SConscript'], r"""
Import('env')

test_pdf = env.PDF(source='test.tex')

""")

test.write(['src', 'test.tex'], r"""
\documentclass{report}

\usepackage{glossaries}

\newglossary[ntg]{notation}{nts}{nto}{List of Notation}

\makeglossary

\newglossaryentry{pi}{type=notation, name={$\pi$}, description={ratio
    of circumference to diameter of a circle}}

\begin{document}

\glsaddall

\printglossary[type=notation, style=list]

\end{document}
""")

test.run(arguments = '.', stderr = None)

files = [
    'test.aux',
    'test.fls',
    'test.glg',
    'test.glo',
    'test.gls',
    'test.ist',
    'test.log',
    'test.ntg',
    'test.nto',
    'test.nts',
    'test.pdf',
]

for f in files:
    test.must_exist(['build',f])
    test.must_not_exist(['src',f])


test.pass_test()
