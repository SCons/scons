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
import string
import sys
import TestSCons

python = TestSCons.python

if sys.platform == 'win32':
    _obj = '.obj'
else:
    _obj = '.os'

test = TestSCons.TestSCons()



test.write('myg77.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'cf:o:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:4] != '#g77':
	outfile.write(l)
sys.exit(0)
""")



test.write('SConstruct', """
env = Environment(SHF77 = r'%s myg77.py')
env.SharedObject(target = 'test1', source = 'test1.f')
env.SharedObject(target = 'test2', source = 'test2.for')
env.SharedObject(target = 'test3', source = 'test3.FOR')
env.SharedObject(target = 'test4', source = 'test4.F')
env.SharedObject(target = 'test5', source = 'test5.fpp')
env.SharedObject(target = 'test6', source = 'test6.FPP')
""" % python)

test.write('test1.f', r"""This is a .f file.
#g77
""")

test.write('test2.for', r"""This is a .for file.
#g77
""")

test.write('test3.FOR', r"""This is a .FOR file.
#g77
""")

test.write('test4.F', r"""This is a .F file.
#g77
""")

test.write('test5.fpp', r"""This is a .fpp file.
#g77
""")

test.write('test6.FPP', r"""This is a .FPP file.
#g77
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1' + _obj) != "This is a .f file.\n")

test.fail_test(test.read('test2' + _obj) != "This is a .for file.\n")

test.fail_test(test.read('test3' + _obj) != "This is a .FOR file.\n")

test.fail_test(test.read('test4' + _obj) != "This is a .F file.\n")

test.fail_test(test.read('test5' + _obj) != "This is a .fpp file.\n")

test.fail_test(test.read('test6' + _obj) != "This is a .FPP file.\n")



g77 = test.where_is('g77')

if g77:

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment(LIBS = 'g2c')
shf77 = foo.Dictionary('SHF77')
bar = foo.Copy(SHF77 = r'%s wrapper.py ' + shf77)
foo.SharedObject(target = 'foo/foo', source = 'foo.f')
bar.SharedObject(target = 'bar/bar', source = 'bar.f')
""" % python)

    test.write('foo.f', r"""
      PROGRAM FOO
      PRINT *,'foo.f'
      STOP
      END
""")

    test.write('bar.f', r"""
      PROGRAM BAR
      PRINT *,'bar.f'
      STOP
      END
""")


    test.run(arguments = 'foo', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(arguments = 'bar')

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

test.pass_test()
