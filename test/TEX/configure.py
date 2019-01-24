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
Verify execution of custom test case.
The old code base would not be able to fail the test
"""

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

dvips = test.where_is('dvips')
latex = test.where_is('latex')

if not all((dvips, latex)):
    test.skip_test("Could not find 'dvips' and/or 'latex'; skipping test(s).\n")

NCR = test.NCR  # non-cached rebuild

#----------------
# 'lmodern' package for LaTeX available?
#  misspell package name to ensure failure

test.write('SConstruct', r"""
lmodern_test_text = r'''
\documentclass{article}
\usepackage{lmodernD}
\title{Mytitle}
\author{Jane Doe}
\begin{document}
   \maketitle
   Hello world!
\end{document}
'''

def CheckLModern(context):
    context.Message("Checking for lmodern...")
    b = context.env.DVI
    is_ok = context.TryBuild(b,lmodern_test_text,'.tex')
    context.Result(is_ok)
    return is_ok

import os
env = Environment()
env['TEXINPUTS'] = '.'
conf = Configure( env, custom_tests={'CheckLModern' : CheckLModern} )
conf.CheckLModern()
env = conf.Finish()
""" % locals())

test.run()

test.checkLogAndStdout(["Checking for lmodern..."],
                      ["no"],
                      [[(('', NCR), )]],
                       "config.log", ".sconf_temp", "SConstruct")


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
