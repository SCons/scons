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
import os.path
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()



test.write('mypdftex.py', r"""
import getopt
import os
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'tx', [])
opt_string = ''
for opt, arg in cmd_opts:
    opt_string = opt_string + ' ' + opt
base_name = os.path.splitext(args[0])[0]
infile = open(args[0], 'rb')
out_file = open(base_name+'.pdf', 'wb')
out_file.write(opt_string + "\n")
for l in infile.readlines():
    if l[0] != '\\':
	out_file.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(PDFTEX = r'%s mypdftex.py', PDFTEXFLAGS = '-x', tools=['pdftex'])
env.PDF(target = 'test.pdf', source = 'test.tex')
""" % python)

test.write('test.tex', r"""This is a test.
\end
""")

test.run(arguments = 'test.pdf', stderr = None)

test.fail_test(not os.path.exists(test.workpath('test.pdf')))



pdftex = test.where_is('pdftex')

if pdftex:

    test.write("wrapper.py", """import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment(PDFTEXFLAGS = '--output-comment Commentary')
pdftex = foo.Dictionary('PDFTEX')
bar = Environment(PDFTEX = r'%s wrapper.py ' + pdftex)
foo.PDF(target = 'foo.pdf', source = 'foo.tex')
bar.PDF(target = 'bar', source = 'bar.tex')
""" % python)

    tex = r"""
This is the %s TeX file.
\end
"""

    test.write('foo.tex', tex % 'foo.tex')

    test.write('bar.tex', tex % 'bar.tex')

    test.run(arguments = 'foo.pdf', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.pdf')))

    test.run(arguments = 'bar.pdf', stderr = None)

    test.fail_test(not os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('bar.pdf')))

test.pass_test()
