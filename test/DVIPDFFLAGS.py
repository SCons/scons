#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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

python = TestSCons.python

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
import getopt
import os
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'x', [])
opt_string = ''
for opt, arg in cmd_opts:
    opt_string = opt_string + ' ' + opt
infile = open(args[0], 'rb')
out_file = open(args[1], 'wb')
out_file.write(opt_string + "\n")
for l in infile.readlines():
    if l[:7] != '#dvipdf':
        out_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TEX = r'%s mytex.py',
                  LATEX = r'%s mylatex.py',
                  DVIPDF = r'%s mydvipdf.py', DVIPDFFLAGS = '-x',
                  tools = ['tex', 'latex', 'dvipdf'])
dvi = env.DVI(target = 'test1.dvi', source = 'test1.tex')
env.DVI(target = 'test2.dvi', source = 'test2.tex')
env.PDF(target = 'test1.pdf', source = dvi)
env.PDF(target = 'test2.pdf', source = 'test2.dvi')
""" % (python, python, python))

test.write('test1.tex', r"""This is a .dvi test.
#tex
#dvipdf
""")

test.write('test2.tex', r"""This is a .tex test.
#tex
#dvipdf
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1.pdf') != " -x\nThis is a .dvi test.\n")

test.fail_test(test.read('test2.pdf') != " -x\nThis is a .tex test.\n")



dvipdf = test.where_is('dvipdf')
tex = test.where_is('tex')

if dvipdf and tex:

    test.write("wrapper.py", """import os
import string
import sys
cmd = string.join(sys.argv[1:], " ")
open('%s', 'ab').write("%%s\\n" %% cmd)
os.system(cmd)
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment(DVIPDFFLAGS = '-N')
dvipdf = foo.Dictionary('DVIPDF')
bar = Environment(DVIPDF = r'%s wrapper.py ' + dvipdf)
foo.PDF(target = 'foo.pdf',
        source = foo.DVI(target = 'foo.dvi', source = 'foo.tex'))
bar.PDF(target = 'bar.pdf',
        source = bar.DVI(target = 'bar.dvi', source = 'bar.tex'))
foo.PDF(target = 'xxx.pdf', source = 'xxx.tex')
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

    test.write('xxx.tex', tex % 'xxx.tex')

    test.write('bar.tex', tex % 'bar.tex')

    test.run(arguments = 'foo.pdf', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.pdf')))

    test.run(arguments = 'xxx.pdf', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(os.path.exists(test.workpath('xxx.dvi')))

    test.run(arguments = 'bar.pdf', stderr = None)

    test.fail_test(test.read('wrapper.out') != "dvipdf bar.dvi bar.pdf\n")

    test.fail_test(not os.path.exists(test.workpath('bar.pdf')))

test.pass_test()
