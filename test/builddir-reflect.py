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
This test validates the correct operation of a BuildDir specification
in avoiding reflection: reflection is the case where the build_dir is
located under the corresponding source dir, and trying to use elements
in the build_dir as sources for that same build dir.

Test based on bug #1055521 filed by Gary Oberbrunner.
"""

import os.path
import re

import TestSCons

test = TestSCons.TestSCons()
python = TestSCons.python
re_python = re.escape(python)

test.write("mycc.py", """
print 'Compile'
""")

test.write("mylink.py", """
print 'Link'
""")

sconstruct = """
env = Environment(CC = r'%(python)s mycc.py',
                  LINK = r'%(python)s mylink.py',
                  INCPREFIX = 'INC_',
                  INCSUFFIX = '_CNI',
                  CPPPATH='%(cpppath)s')  # note no leading '#'
Export("env")
SConscript('SConscript', build_dir="dir1/dir2", src_dir=".")
"""

test.write('SConscript', """\
Import("env")
env.Program("foo", "src1/foo.c")
Default(".")
""")

test.write('foo.h', '#define HI_STR "hello, there!"\n')

test.subdir('src1')

test.write(['src1', 'foo.c'], """\
#include <stdio.h>
#include "foo.h"
main() { printf(HI_STR);}
""")

# Test the bad cpppath; make sure it doesn't reflect dir1/dir2/foo.h
# into dir1/dir2/dir1/dir2/foo.h, and make sure the target/message for
# builds is correct.

cpppath = 'dir1/dir2'   # note, no leading '#'
test.write('SConstruct', sconstruct % locals() )

targets = re.escape(os.path.join('dir1', 'dir2'))
INC_CNI = re.escape(os.path.join('INC_dir1', 'dir2', 'dir1', 'dir2_CNI'))

# The .* after mycc\\.py below handles /nologo flags from Visual C/C++.
test.run(arguments = '',
         stdout=test.wrap_stdout("""\
scons: building associated BuildDir targets: %(targets)s
%(re_python)s mycc\\.py.* %(INC_CNI)s .+
Compile
%(re_python)s mylink\\.py .+
Link
""" % locals()),
         match=TestSCons.match_re,
         )

test.must_exist(['dir1', 'dir2', 'foo.h'])
test.must_exist(['dir1', 'dir2', 'src1', 'foo.c'])
test.must_not_exist(['dir1', 'dir2', 'dir1', 'dir2', 'foo.h'])

import shutil
shutil.rmtree('dir1', ignore_errors=1)
test.must_not_exist('dir1')

# Now test the good cpppath and make sure everything looks right.

cpppath = '#dir1/dir2'   # note leading '#'
test.write('SConstruct', sconstruct % locals() )

INC_CNI = re.escape(os.path.join('INC_dir1', 'dir2_CNI'))

# The .* after mycc\\.py below handles /nologo flags from Visual C/C++.
test.run(arguments = '',
         stdout=test.wrap_stdout("""\
scons: building associated BuildDir targets: %(targets)s
%(re_python)s mycc\\.py.* %(INC_CNI)s .+
Compile
%(re_python)s mylink\\.py .+
Link
""" % locals()),
         match=TestSCons.match_re,
         )

test.must_exist(['dir1', 'dir2', 'foo.h'])
test.must_exist(['dir1', 'dir2', 'src1', 'foo.c'])
test.must_not_exist(['dir1', 'dir2', 'dir1', 'dir2', 'foo.h'])


test.pass_test()
