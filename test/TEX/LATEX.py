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

"""
Validate that we can set the LATEX string to our own utility, that
the produced .dvi, .aux and .log files get removed by the -c option,
and that we can use this to wrap calls to the real latex utility.
"""

import string

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mylatex.py', r"""
import sys
import os
import getopt
cmd_opts, arg = getopt.getopt(sys.argv[1:], 'i:', [])
base_name = os.path.splitext(arg[0])[0]
infile = open(arg[0], 'rb')
dvi_file = open(base_name+'.dvi', 'wb')
aux_file = open(base_name+'.aux', 'wb')
log_file = open(base_name+'.log', 'wb')
for l in infile.readlines():
    if l[0] != '\\':
        dvi_file.write(l)
        aux_file.write(l)
        log_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LATEX = r'%(_python_)s mylatex.py', tools=['latex'])
env.DVI(target = 'test1.dvi', source = 'test1.ltx')
env.DVI(target = 'test2.dvi', source = 'test2.latex')
""" % locals())

test.write('test1.ltx', r"""This is a .ltx test.
\end
""")

test.write('test2.latex', r"""This is a .latex test.
\end
""")

test.run(arguments = '.')

test.must_match('test1.dvi', "This is a .ltx test.\n")
test.must_match('test1.aux', "This is a .ltx test.\n")
test.must_match('test1.log', "This is a .ltx test.\n")

test.must_match('test2.dvi', "This is a .latex test.\n")
test.must_match('test2.aux', "This is a .latex test.\n")
test.must_match('test2.log', "This is a .latex test.\n")

test.run(arguments = '-c .')

test.must_not_exist('test1.dvi')
test.must_not_exist('test1.aux')
test.must_not_exist('test1.log')

test.must_not_exist('test2.dvi')
test.must_not_exist('test2.aux')
test.must_not_exist('test2.log')



latex = test.where_is('latex')

if latex:

    test.write("wrapper.py", """import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
import os
ENV = { 'PATH' : os.environ['PATH'],
        'TEXINPUTS' : [ 'subdir', os.environ.get('TEXINPUTS', '') ] }
foo = Environment(ENV = ENV)
latex = foo.Dictionary('LATEX')
makeindex = foo.Dictionary('MAKEINDEX')
python_path = r'%(_python_)s'
bar = Environment(ENV = ENV,
                  LATEX = python_path + ' wrapper.py ' + latex,
                  MAKEINDEX =  python_path + ' wrapper.py ' + makeindex)
foo.DVI(target = 'foo.dvi', source = 'foo.ltx')
bar.DVI(target = 'bar', source = 'bar.latex')

bar.DVI(target = 'makeindex', source = 'makeindex.tex')
foo.DVI(target = 'latexi', source = 'latexi.tex')
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
    test.write('latexi.tex',  latex1 % 'latexi.tex');
    test.write([ 'subdir', 'latexinputfile'], latex2)
    test.write([ 'subdir', 'latexincludefile.tex'], latex3 % '1')

    test.run(arguments = 'foo.dvi', stderr = None)
    test.must_not_exist('wrapper.out')
    test.must_exist('foo.dvi')

    test.run(arguments = 'bar.dvi', stderr = None)
    test.must_match('wrapper.out', "wrapper.py\n")
    test.must_exist('bar.dvi')

    test.run(arguments = 'makeindex.dvi', stderr = None)
    test.must_match('wrapper.out', "wrapper.py\n")

    test.run(arguments = 'latexi.dvi', stderr = None)
    test.must_exist('latexi.dvi')
    test.must_exist('latexi.ind')

    test.write([ 'subdir', 'latexincludefile.tex'], latex3 % '2')
    test.not_up_to_date(arguments = 'latexi.dvi', stderr = None)

    test.run(arguments = '-c', stderr = None)
    test.must_not_exist('latexi.ind')
    test.must_not_exist('latexi.ilg')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
