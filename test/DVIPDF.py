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

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

test = TestSCons.TestSCons()



test.write('mytex.py', r"""
import os
import sys
base_name = os.path.splitext(sys.argv[1])[0]
infile = open(sys.argv[1], 'rb')
out_file = open(base_name+'.dvi', 'wb')
for l in infile.readlines():
    if l[:4] != '#tex':
        out_file.write(l)
sys.exit(0)
""")

test.write('mylatex.py', r"""
import os
import sys
base_name = os.path.splitext(sys.argv[1])[0]
infile = open(sys.argv[1], 'rb')
out_file = open(base_name+'.dvi', 'wb')
for l in infile.readlines():
    if l[:6] != '#latex':
        out_file.write(l)
sys.exit(0)
""")

test.write('mydvipdf.py', r"""
import os
import sys
infile = open(sys.argv[1], 'rb')
out_file = open(sys.argv[2], 'wb')
for l in infile.readlines():
    if l[:7] != '#dvipdf':
        out_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TEX = r'%s mytex.py',
                  LATEX = r'%s mylatex.py',
                  DVIPDF = r'%s mydvipdf.py')
dvi = env.DVI(target = 'test1.dvi', source = 'test1.tex')
env.PDF(target = 'test1.pdf', source = dvi)
env.PDF(target = 'test2.pdf', source = 'test2.tex')
env.PDF(target = 'test3.pdf', source = 'test3.ltx')
env.PDF(target = 'test4.pdf', source = 'test4.latex')
""" % (python, python, python))

test.write('test1.tex', r"""This is a .dvi test.
#tex
#dvipdf
""")

test.write('test2.tex', r"""This is a .tex test.
#tex
#dvipdf
""")

test.write('test3.ltx', r"""This is a .ltx test.
#latex
#dvipdf
""")

test.write('test4.latex', r"""This is a .latex test.
#latex
#dvipdf
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1.pdf') != "This is a .dvi test.\n")

test.fail_test(test.read('test2.pdf') != "This is a .tex test.\n")

test.fail_test(test.read('test3.pdf') != "This is a .ltx test.\n")

test.fail_test(test.read('test4.pdf') != "This is a .latex test.\n")



dvipdf = None
for dir in string.split(os.environ['PATH'], os.pathsep):
    l = os.path.join(dir, 'dvipdf' + _exe)
    if os.path.exists(l):
        dvipdf = l
        break

if dvipdf:

    test.write("wrapper.py", """import os
import string
import sys
cmd = string.join(sys.argv[1:], " ")
open('%s', 'ab').write("%%s\\n" %% cmd)
os.system(cmd)
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment()
dvipdf = foo.Dictionary('DVIPDF')
bar = Environment(DVIPDF = r'%s wrapper.py ' + dvipdf)
foo.PDF(target = 'foo.pdf', source = 'foo.tex')
bar.PDF(target = 'bar1', source = 'bar1.tex')
bar.PDF(target = 'bar2', source = 'bar2.ltx')
bar.PDF(target = 'bar3', source = 'bar3.latex')
""" % python)

    tex = r"""
This is the %s TeX file.
\end
"""

    latex = r"""
\documentclass{letter}
\begin{document}
This is the %s LaTeX file.
\end{document}
"""

    test.write('foo.tex', tex % 'foo.tex')
    test.write('bar1.tex', tex % 'bar1.tex')
    test.write('bar2.ltx', latex % 'bar2.ltx')
    test.write('bar3.latex', latex % 'bar3.latex')

    test.run(arguments = 'foo.dvi', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.dvi')))

    test.run(arguments = 'bar1.pdf bar2.pdf bar3.pdf', stderr = None)

    expect = """dvipdf bar1.dvi bar1.pdf
dvipdf bar2.dvi bar2.pdf
dvipdf bar3.dvi bar3.pdf
"""

    test.fail_test(test.read('wrapper.out') != expect)

    test.fail_test(not os.path.exists(test.workpath('bar1.pdf')))
    test.fail_test(not os.path.exists(test.workpath('bar2.pdf')))
    test.fail_test(not os.path.exists(test.workpath('bar3.pdf')))

test.pass_test()
