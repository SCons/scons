#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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
import os.path
import string
import sys
import TestSCons

python = sys.executable

test = TestSCons.TestSCons()



test.write('mylatex.py', r"""
import sys
import os
base_name = os.path.splitext(sys.argv[1])[0]
infile = open(sys.argv[1], 'rb')
out_file = open(base_name+'.dvi', 'wb')
for l in infile.readlines():
    if l[0] != '\\':
	out_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LATEX = r'%s mylatex.py', tools=['latex'])
env.DVI(target = 'test1.dvi', source = 'test1.ltx')
env.DVI(target = 'test2.dvi', source = 'test2.latex')
""" % python)

test.write('test1.ltx', r"""This is a .ltx test.
\end
""")

test.write('test2.latex', r"""This is a .latex test.
\end
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1.dvi') != "This is a .ltx test.\n")

test.fail_test(test.read('test2.dvi') != "This is a .latex test.\n")



latex = test.where_is('latex')

if latex:

    test.write("wrapper.py", """import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment()
latex = foo.Dictionary('LATEX')
bar = Environment(LATEX = r'%s wrapper.py ' + latex)
foo.DVI(target = 'foo.dvi', source = 'foo.ltx')
bar.DVI(target = 'bar', source = 'bar.latex')
""" % python)

    latex = r"""
\documentclass{letter}
\begin{document}
This is the %s LaTeX file.
\end{document}
"""

    test.write('foo.ltx', latex % 'foo.ltx')

    test.write('bar.latex', latex % 'bar.latex')

    test.run(arguments = 'foo.dvi', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.dvi')))

    test.run(arguments = 'bar.dvi', stderr = None)

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

    test.fail_test(not os.path.exists(test.workpath('bar.dvi')))

test.pass_test()
