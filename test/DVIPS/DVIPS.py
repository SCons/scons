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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mytex.py', r"""
import os
import sys
import getopt
cmd_opts, arg = getopt.getopt(sys.argv[1:], 'i:r:', [])
base_name = os.path.splitext(arg[0])[0]
infile = open(arg[0], 'r')
out_file = open(base_name+'.dvi', 'w')
for l in infile.readlines():
    if l[:4] != '#tex':
        out_file.write(l)
sys.exit(0)
""")

test.write('mylatex.py', r"""
import os
import sys
import getopt
cmd_opts, arg = getopt.getopt(sys.argv[1:], 'i:r:', [])
base_name = os.path.splitext(arg[0])[0]
infile = open(arg[0], 'r')
out_file = open(base_name+'.dvi', 'w')
for l in infile.readlines():
    if l[:6] != '#latex':
        out_file.write(l)
sys.exit(0)
""")

test.write('mydvips.py', r"""
import os
import sys
infile = open(sys.argv[3], 'r')
out_file = open(sys.argv[2], 'w')
for l in infile.readlines():
    if l[:6] != '#dvips':
        out_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TEX = r'%(_python_)s mytex.py',
                  LATEX = r'%(_python_)s mylatex.py',
                  DVIPS = r'%(_python_)s mydvips.py',
                  tools=['tex', 'latex', 'dvips'])
dvi = env.DVI(target = 'test1.dvi', source = 'test1.tex')
env.PostScript(target = 'test1.ps', source = dvi)
env.PostScript(target = 'test2.ps', source = 'test2.tex')
env.PostScript(target = 'test3.ps', source = 'test3.ltx')
env.PostScript(target = 'test4.ps', source = 'test4.latex')
""" % locals())

test.write('test1.tex', r"""This is a .dvi test.
#tex
#dvips
""")

test.write('test2.tex', r"""This is a .tex test.
#tex
#dvips
""")

test.write('test3.ltx', r"""This is a .ltx test.
#latex
#dvips
""")

test.write('test4.latex', r"""This is a .latex test.
#latex
#dvips
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.ps', "This is a .dvi test.\n", mode='r')

test.must_match('test2.ps', "This is a .tex test.\n", mode='r')

test.must_match('test3.ps', "This is a .ltx test.\n", mode='r')

test.must_match('test4.ps', "This is a .latex test.\n", mode='r')


have_latex = test.where_is('latex')
if not have_latex:
    test.skip_test("Could not find 'latex'; skipping test(s).\n")

dvips = test.where_is('dvips')
if not dvips:
    test.skip_test("Could not find 'dvips'; skipping test(s).\n")

test.write("wrapper.py", """
import subprocess
import sys
cmd = " ".join(sys.argv[1:])
open('%s', 'a').write("%%s\\n" %% cmd)
subprocess.run(cmd, shell=True)
""" % test.workpath('wrapper.out').replace('\\', '\\\\'))

test.write('SConstruct', """
import os
ENV = { 'PATH' : os.environ['PATH'] }
foo = Environment(ENV = ENV)
dvips = foo.Dictionary('DVIPS')
bar = Environment(ENV = ENV, DVIPS = r'%(_python_)s wrapper.py ' + dvips)
foo.PostScript(target = 'foo.ps', source = 'foo.tex')
bar.PostScript(target = 'bar1', source = 'bar1.tex')
bar.PostScript(target = 'bar2', source = 'bar2.ltx')
bar.PostScript(target = 'bar3', source = 'bar3.latex')
""" % locals())

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

test.must_not_exist(test.workpath('wrapper.out'))

test.must_exist(test.workpath('foo.dvi'))

test.run(arguments = 'bar1.ps bar2.ps bar3.ps', stderr = None)

expect = """dvips -o bar1.ps bar1.dvi
dvips -o bar2.ps bar2.dvi
dvips -o bar3.ps bar3.dvi
"""

test.must_match('wrapper.out', expect, mode='r')

test.must_exist(test.workpath('bar1.ps'))
test.must_exist(test.workpath('bar2.ps'))
test.must_exist(test.workpath('bar3.ps'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
