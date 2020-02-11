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
import sys

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mygs.py', r"""
import os
import sys
outfile = open(sys.argv[1], 'w')
infile = open(sys.argv[2], 'r')
for l in infile.readlines():
    if l[:3] != '#ps':
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(GS = r'%(_python_)s mygs.py',
                  GSCOM = r'$GS $TARGET $SOURCE',
                  tools=['gs'])
env.PDF(target = 'test1.pdf', source = 'test1.ps')
env.Gs(target = 'test2.pdf', source = 'test1.ps')
""" % locals())

test.write('test1.ps', r"""This is a .ps test.
#ps
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.pdf', "This is a .ps test.\n", mode='r')
test.must_match('test2.pdf', "This is a .ps test.\n", mode='r')



if sys.platform == 'win32':
    gs_executable = 'gswin32c'
elif sys.platform == 'os2':
    gs_executable = 'gsos2'
else:
    gs_executable = 'gs'
gs = test.where_is(gs_executable)

if gs:
    test.write("wrapper.py", """\
import subprocess
import sys
cmd = " ".join(sys.argv[1:])
open('%s', 'a').write("%%s\\n" %% cmd)
subprocess.run(cmd, shell=True)
""" % test.workpath('wrapper.out').replace('\\', '\\\\'))

    test.write('SConstruct', """\
import os
foo = Environment(ENV = { 'PATH' : os.environ['PATH'] })
gs = foo.Dictionary('GS')
bar = Environment(ENV = { 'PATH' : os.environ['PATH'] },
                  GS = r'%(_python_)s wrapper.py ' + gs)
foo.PDF(target = 'foo.pdf', source = 'foo.ps')
bar.PDF(target = 'bar.pdf', source = 'bar.ps')
""" % locals())

    input = """\
%!PS-Adobe
100 100 moveto /Times-Roman findfont 24 scalefont (Hello, world!) show showpage
"""

    test.write('foo.ps', input)

    test.write('bar.ps', input)

    test.run(arguments = 'foo.pdf', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.pdf')))

    test.run(arguments = 'bar.pdf', stderr = None)

    test.must_match('wrapper.out', "%s -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=bar.pdf bar.ps\n" % gs_executable, mode='r')

    test.fail_test(not os.path.exists(test.workpath('bar.pdf')))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
