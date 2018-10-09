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
Test that an appended relative CPPPATH works with generated files.

This is basically the same as CPPPATH.py, but the include path
is env.Append-ed and everything goes into sub directory "sub".
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('sub', ['sub', 'local_include'])

test.Qt_dummy_installation()

aaa_exe = os.path.join('sub', 'aaa' + TestSCons._exe)

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', r"""
SConscript('sub/SConscript')
""")

test.write(['sub', 'SConscript'], r"""
Import("env")
env.Append(CPPPATH=['./local_include'])
env.Program(target = 'aaa', source = 'aaa.cpp')
""")

test.write(['sub', 'aaa.cpp'], r"""
#include "aaa.h"
int main(void) { aaa(); return 0; }
""")

test.write(['sub', 'aaa.h'], r"""
#include "my_qobject.h"
#include "local_include.h"
void aaa(void) Q_OBJECT;
""")

test.write(['sub', 'local_include', 'local_include.h'], r"""
/* empty; just needs to be found */
""")

test.run(arguments = aaa_exe)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
