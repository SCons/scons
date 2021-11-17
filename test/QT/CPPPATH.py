#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Test that an overwritten CPPPATH works with generated files.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('local_include')

test.Qt_dummy_installation()

aaa_exe = 'aaa' + TestSCons._exe

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', """\
Import("env")
env.Program(target = 'aaa', source = 'aaa.cpp', CPPPATH=['$CPPPATH', './local_include'])
""")

test.write('aaa.cpp', r"""
#include "aaa.h"
int main(void) { aaa(); return 0; }
""")

test.write('aaa.h', r"""
#include "my_qobject.h"
#include "local_include.h"
void aaa(void) Q_OBJECT;
""")

test.write(['local_include', 'local_include.h'], r"""
/* empty; just needs to be found */
""")

test.run(arguments='--warn=no-tool-qt-deprecated ' + aaa_exe)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
