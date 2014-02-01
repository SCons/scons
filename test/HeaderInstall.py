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

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('work1', ['work1', 'dist'])

test.write(['work1', 'SConstruct'], """
env = Environment(CPPPATH=['#include'])
Export('env')
SConscript('dist/SConscript')
libfoo = env.StaticLibrary('foo', ['foo.c'])
Default(libfoo)
""")

test.write(['work1', 'foo.c'], """
#include <h1.h>
""")

test.write(['work1', 'dist', 'SConscript'], """\
Import('env')
env.Install('#include', ['h1.h', 'h2.h', 'h3.h'])
""")

test.write(['work1', 'dist', 'h1.h'], """\
#include "h2.h"
""")

test.write(['work1', 'dist', 'h2.h'], """\
#include "h3.h"
""")

test.write(['work1', 'dist', 'h3.h'], """\
int foo = 3;
""")

test.run(chdir='work1', arguments=".",
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.up_to_date(chdir = 'work1', arguments = ".")

#
test.subdir('ref', 'work2', ['work2', 'src'])

test.write(['work2', 'SConstruct'], """
env = Environment(CPPPATH=['build', r'%s'])
env.Install('build', 'src/in1.h')
env.Install('build', 'src/in2.h')
env.Install('build', 'src/in3.h')
""" % test.workpath('ref'))

test.write(['ref', 'in1.h'], '#define FILE "ref/in1.h"\n#include <in2.h>\n')
test.write(['ref', 'in2.h'], '#define FILE "ref/in2.h"\n#include <in3.h>\n')
test.write(['ref', 'in3.h'], '#define FILE "ref/in3.h"\n#define FOO 0\n')

src_in1_h = '#define FILE "src/in1.h"\n#include <in2.h>\n'
src_in2_h = '#define FILE "src/in2.h"\n#include <in3.h>\n'
src_in3_h = '#define FILE "src/in3.h"\n#define FOO 0\n'
test.write(['work2', 'src', 'in1.h'], src_in1_h)
test.write(['work2', 'src', 'in2.h'], src_in2_h)
test.write(['work2', 'src', 'in3.h'], src_in3_h)

test.run(chdir = 'work2', arguments = 'build')

test.must_match(['work2', 'build', 'in1.h'], src_in1_h)
test.must_match(['work2', 'build', 'in2.h'], src_in2_h)
test.must_match(['work2', 'build', 'in3.h'], src_in3_h)

test.up_to_date(chdir = 'work2', arguments = 'build')

src_in3_h = '#define FILE "src/in3.h"\n#define FOO 1\n'
test.write(['work2', 'src', 'in3.h'], src_in3_h)

test.run(chdir = 'work2', arguments = 'build', stdout=test.wrap_stdout("""\
Install file: "%s" as "%s"
""" % (os.path.join('src', 'in3.h'),
       os.path.join('build', 'in3.h'))))

test.must_match(['work2', 'build', 'in1.h'], src_in1_h)
test.must_match(['work2', 'build', 'in2.h'], src_in2_h)
test.must_match(['work2', 'build', 'in3.h'], src_in3_h)

test.up_to_date(chdir = 'work2', arguments = 'build')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
