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
Test Qt creation from a copied empty environment.
"""

import TestSCons

test = TestSCons.TestSCons()

test.Qt_dummy_installation('qt')

test.write('SConstruct', """\
orig = Environment()
env = orig.Clone(QTDIR = r'%s',
                 QT_LIB = r'%s',
                 QT_MOC = r'%s',
                 QT_UIC = r'%s',
                 tools=['qt'])
env.Program('main', 'main.cpp', CPPDEFINES=['FOO'], LIBS=[])
""" % (test.QT, test.QT_LIB, test.QT_MOC, test.QT_UIC))

test.write('main.cpp', r"""
#include "foo6.h"
int main(void) { foo6(); return 0; }
""")

test.write(['qt', 'include', 'foo6.h'], """\
#include <stdio.h>
void
foo6(void)
{
#ifdef  FOO
    printf("qt/include/foo6.h\\n");
#endif
}
""")

# we can receive warnings about a non detected qt (empty QTDIR)
# these are not critical, but may be annoying.
test.run(stderr=None)

test.run(program = test.workpath('main' + TestSCons._exe),
         stderr = None,
         stdout = 'qt/include/foo6.h\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
