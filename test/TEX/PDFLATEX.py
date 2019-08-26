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
Validate that we can set the PDFLATEX string to our own utility, that
the produced .dvi, .aux and .log files get removed by the -c option,
and that we can use this to wrap calls to the real latex utility.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mypdflatex.py', r"""
import sys
import os
import getopt
cmd_opts, arg = getopt.getopt(sys.argv[1:], 'i:r:', [])
base_name = os.path.splitext(arg[0])[0]
with open(arg[0], 'r') as ifp:
    with open(base_name+'.pdf', 'w') as pdf_file, \
         open(base_name+'.aux', 'w') as aux_file, \
         open(base_name+'.log', 'w') as log_file:

        for l in ifp.readlines():
            if l[0] != '\\':
                pdf_file.write(l)
                aux_file.write(l)
                log_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(PDFLATEX = r'%(_python_)s mypdflatex.py', tools=['pdflatex'])
env.PDF(target = 'test1.pdf', source = 'test1.ltx')
env.PDF(target = 'test2.pdf', source = 'test2.latex')
""" % locals())

test.write('test1.ltx', r"""This is a .ltx test.
\end
""")

test.write('test2.latex', r"""This is a .latex test.
\end
""")

test.run(arguments = '.')

test.must_exist('test1.pdf')
test.must_exist('test1.aux')
test.must_exist('test1.log')

test.must_exist('test2.pdf')
test.must_exist('test2.aux')
test.must_exist('test2.log')

test.run(arguments = '-c .')

test.must_not_exist('test1.pdf')
test.must_not_exist('test1.aux')
test.must_not_exist('test1.log')

test.must_not_exist('test2.pdf')
test.must_not_exist('test2.aux')
test.must_not_exist('test2.log')



pdflatex = test.where_is('pdflatex')

if pdflatex:

    test.file_fixture('wrapper.py')

    test.write('SConstruct', """
import os
ENV = { 'PATH' : os.environ['PATH'] }
foo = Environment(ENV = ENV)
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

    test.must_not_exist('wrapper.out')

    test.must_exist('foo.pdf')

    test.run(arguments = 'bar.pdf', stderr = None)

    test.must_match('wrapper.out', "wrapper.py\n")

    test.must_exist('bar.pdf')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
