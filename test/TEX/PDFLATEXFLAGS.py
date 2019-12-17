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

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mypdflatex.py', r"""
import getopt
import os
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'tx', [])
opt_string = ''
for opt, arg in cmd_opts:
    opt_string = opt_string + ' ' + opt
base_name = os.path.splitext(args[0])[0]
with open(base_name+'.pdf', 'w') as ofp, open(args[0], 'r') as ifp:
    ofp.write(opt_string + "\n")
    for l in ifp.readlines():
        if l[0] != '\\':
            ofp.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(PDFLATEX = r'%(_python_)s mypdflatex.py',
                  PDFLATEXFLAGS = '-x',
                  tools=['pdflatex'])
env.PDF(target = 'test1.pdf', source = 'test1.ltx')
env.Clone(PDFLATEXFLAGS = '-t').PDF(target = 'test2.pdf', source = 'test2.latex')
""" % locals())

test.write('test1.ltx', r"""This is a .ltx test.
\end
""")

test.write('test2.latex', r"""This is a .latex test.
\end
""")

test.run(arguments = '.', stderr = None)

test.fail_test(not os.path.exists(test.workpath('test1.pdf')))

test.fail_test(not os.path.exists(test.workpath('test2.pdf')))



pdflatex = test.where_is('pdflatex')

if pdflatex:

    test.file_fixture('wrapper.py')

    test.write('SConstruct', """
import os
ENV = { 'PATH' : os.environ['PATH'] }
foo = Environment(ENV = ENV, PDFLATEXFLAGS = '--output-comment Commentary')
pdflatex = foo.Dictionary('PDFLATEX')
bar = Environment(ENV = ENV, PDFLATEX = r'%(_python_)s wrapper.py ' + pdflatex)
foo.PDF(target = 'foo.pdf', source = 'foo.ltx')
bar.PDF(target = 'bar', source = 'bar.latex')
""" % locals())

    latex = r"""
\documentclass{letter}
\begin{document}
This is the %s LaTeX file.
\end{document}
"""

    test.write('foo.ltx', latex % 'foo.ltx')

    test.write('bar.latex', latex % 'bar.latex')

    test.run(arguments = 'foo.pdf', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.pdf')))

    test.run(arguments = 'bar.pdf', stderr = None)

    test.must_match('wrapper.out',"wrapper.py\n", mode='r')

    test.fail_test(not os.path.exists(test.workpath('bar.pdf')))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
