#!/usr/bin/env python
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
Test that dependencies in installed header files get re-scanned correctly.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(CPPPATH=['#include'])
Export('env')
SConscript('dist/SConscript')
libfoo = env.StaticLibrary('foo', ['foo.c'])
Default(libfoo)
""")

test.write('foo.c', """
#include <h1.h>
""")

test.subdir('dist')

test.write(['dist', 'SConscript'], """\
Import('env')
env.Install('#include', ['h1.h', 'h2.h', 'h3.h'])
""")

test.write(['dist', 'h1.h'], """\
#include "h2.h"
""")

test.write(['dist', 'h2.h'], """\
#include "h3.h"
""")

test.write(['dist', 'h3.h'], """\
int foo = 3;
""")

test.run(arguments = ".")

test.up_to_date(arguments = ".")

test.pass_test()
