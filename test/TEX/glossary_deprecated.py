#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

r"""
Validate that use of the legacy \makeglossary command (from the obsolete
glossary.sty package) produces a deprecation warning advising use of
\makeglossaries with the glossaries package instead.

The warning fires during dependency analysis (the emitter), so it appears
even if the obsolete glossary.sty package is not installed and the
LaTeX build itself fails.
"""

import subprocess

import TestSCons

test = TestSCons.TestSCons()

latex = test.where_is('latex')
if not latex:
    test.skip_test("Could not find 'latex'; skipping test.\n")

test.write(
    'SConstruct',
    """\
import os
env = Environment(tools = ['latex'], ENV = {'PATH' : os.environ['PATH']})
env.DVI('glossary', 'glossary.ltx')
""",
)

test.write(
    'glossary.ltx',
    r"""
\documentclass{article}

\usepackage{glossary}

\makeglossary


\begin{document}

A glossary entry \glossary{name={gnu}, description={an animal or software group}}.

\printglossary

\end{document}
""",
)

cp = subprocess.run('kpsewhich glossary.sty', shell=True)
# If glossary.sty is installed the build succeeds (status 0), otherwise it fails (status 2)
expected_status = 0 if cp.returncode == 0 else 2

test.run(arguments='.', stderr=None, status=expected_status)

deprecation_msg = "Found \\makeglossary in"
test.must_contain_any_line(test.stderr(), [deprecation_msg])

test.pass_test()
