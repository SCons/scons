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
Test that the $ARCOMSTR construction variable allows you to customize
the displayed archiver string.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()



test.write('myar.py', """
import sys
outfile = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    infile = open(f, 'rb')
    for l in filter(lambda l: l != '/*ar*/\\n', infile.readlines()):
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools=['default', 'ar'],
                  ARCOM = r'%s myar.py $TARGET $SOURCES',
                  ARCOMSTR = 'Archiving $TARGET from $SOURCES',
                  LIBPREFIX = '',
                  LIBSUFFIX = '.lib')
env.Library(target = 'output', source = ['file.1', 'file.2'])
""" % python)

test.write('file.1', "file.1\n/*ar*/\n")
test.write('file.2', "file.2\n/*ar*/\n")

test.run(stdout = test.wrap_stdout("""\
Archiving output.lib from file.1 file.2
"""))

test.must_match('output.lib', "file.1\nfile.2\n")



test.pass_test()
