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

test.write('mydvipdf.py', r"""
import os
import sys
import getopt
cmd_opts, arg = getopt.getopt(sys.argv[1:], 'i:r:', [])
infile = open(arg[0], 'r')
out_file = open(arg[1], 'w')
for l in infile.readlines():
    if l[:7] != '#dvipdf':
        out_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TEX = r'%(_python_)s mytex.py',
                  LATEX = r'%(_python_)s mylatex.py',
                  DVIPDF = r'%(_python_)s mydvipdf.py',
                  tools=['latex', 'tex', 'dvipdf'])
dvi = env.DVI(target = 'test1.dvi', source = 'test1.tex')
env.DVI(target = 'test2.dvi', source = 'test2.tex')
env.PDF(target = 'test1.pdf', source = dvi)
env.PDF(target = 'test2.pdf', source = 'test2.dvi')
""" % locals())

test.write('test1.tex', r"""This is a .dvi test.
#tex
#dvipdf
""")

test.write('test2.tex', r"""This is a .tex test.
#tex
#dvipdf
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.pdf', "This is a .dvi test.\n", mode='r')

test.must_match('test2.pdf', "This is a .tex test.\n", mode='r')



dvipdf = test.where_is('dvipdf')
tex = test.where_is('tex')

if dvipdf and tex:

    test.write("wrapper.py", """\
import subprocess
import sys
cmd = " ".join(sys.argv[1:])
open('%s', 'a').write("%%s\\n" %% cmd)
subprocess.run(cmd, shell=True)
""" % test.workpath('wrapper.out').replace('\\', '\\\\'))

    test.write('SConstruct', """
import os
foo = Environment(ENV = { 'PATH' : os.environ['PATH'] })
dvipdf = foo.Dictionary('DVIPDF')
bar = Environment(ENV = { 'PATH' : os.environ['PATH'] },
                  DVIPDF = r'%(_python_)s wrapper.py ' + dvipdf)
foo.PDF(target = 'foo.pdf',
        source = foo.DVI(target = 'foo.dvi', source = 'foo.tex'))
bar.PDF(target = 'bar.pdf',
        source = bar.DVI(target = 'bar.dvi', source = 'bar.tex'))
foo.PDF(target = 'xxx.pdf', source = 'xxx.tex')
""" % locals())

    tex = r"""
This is the %s TeX file.
\end
"""

    test.write('foo.tex', tex % 'foo.tex')

    test.write('xxx.tex', tex % 'xxx.tex')

    test.write('bar.tex', tex % 'bar.tex')

    test.run(arguments = 'foo.pdf', stderr = None)

    test.must_not_exist(test.workpath('wrapper.out'))

    test.must_exist(test.workpath('foo.pdf'))

    test.run(arguments = 'xxx.pdf', stderr = None)

    test.must_not_exist(test.workpath('wrapper.out'))

    test.must_not_exist(test.workpath('xxx.dvi'))

    test.run(arguments = 'bar.pdf', stderr = None)

    test.must_match('wrapper.out', "dvipdf bar.dvi bar.pdf\n")

    test.must_exist(test.workpath('bar.pdf'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
