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
Test creation from a copied environment that already has QT variables.
This makes sure the tool initialization is re-entrant.
"""

import TestSCons

test = TestSCons.TestSCons()

test.Qt_dummy_installation('qt')

test.write(['qt', 'include', 'foo5.h'], """\
#include <stdio.h>
void
foo5(void)
{
#ifdef  FOO
    printf("qt/include/foo5.h\\n");
#endif
}
""")

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', """\
Import("env")
env = env.Clone(tools=['qt3'])
env.Program('main', 'main.cpp', CPPDEFINES=['FOO'], LIBS=[])
""")

test.write('main.cpp', r"""
#include "foo5.h"
int main(void) { foo5(); return 0; }
""")

test.run(arguments="--warn=no-tool-qt-deprecated")

test.run(
    arguments='--warn=no-tool-qt-deprecated',
    program=test.workpath('main' + TestSCons._exe),
    stdout='qt/include/foo5.h\n',
)
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
