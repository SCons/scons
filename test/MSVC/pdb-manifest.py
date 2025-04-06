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
Verify that .pdb files work correctly in conjunction with manifest files.
"""

import TestSCons

test = TestSCons.TestSCons()
test.skip_if_not_msvc()

_exe = TestSCons._exe
_dll = TestSCons._dll
_lib = TestSCons._lib

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment()
env['WINDOWS_INSERT_DEF'] = True
env['WINDOWS_INSERT_MANIFEST'] = True
env['PDB'] = '${TARGET.base}.pdb'
env.Program('test', 'test.cpp')
env.SharedLibrary('sharedlib', 'test.cpp')
env.StaticLibrary('staticlib', 'test.cpp')
""")

test.write('test.cpp', """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv)
{
    printf("test.cpp\\n");
    exit (0);
}
""")

test.write('sharedlib.def', """\
""")

test.run(arguments = '.')
test.must_exist('test%s' % _exe)
test.must_exist('test.pdb')
test.must_exist('sharedlib%s' % _dll)
test.must_exist('sharedlib.pdb')
test.must_exist('staticlib%s' % _lib)
test.must_not_exist('staticlib.pdb')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
