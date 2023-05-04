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
Test the manual QT3 builder calls.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('include', 'ui')

test.Qt_dummy_installation()

aaa_exe = 'aaa' + TestSCons._exe

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', r"""
Import("env")
sources = ['aaa.cpp', 'bbb.cpp', 'ddd.cpp', 'eee.cpp', 'main.cpp']

# normal invocation
sources.append(env.Moc('include/aaa.h'))
moc = env.Moc('bbb.cpp')
env.Ignore( moc, moc )
sources.extend(env.Uic('ui/ccc.ui')[1:])

# manual target specification
sources.append(env.Moc('moc-ddd.cpp', 'include/ddd.h',
               QT3_MOCHPREFIX='')) # Watch out !
moc = env.Moc('moc_eee.cpp', 'eee.cpp')
env.Ignore( moc, moc )
sources.extend(env.Uic(['include/uic_fff.hpp', 'fff.cpp', 'fff.moc.cpp'],
                       'ui/fff.ui')[1:])

print(list(map(str,sources)))
env.Program(target='aaa',
            source=sources,
            CPPPATH=['$CPPPATH', './include'],
            QT3_AUTOSCAN=0)
""")

test.write('aaa.cpp', r"""
#include "aaa.h"
""")

test.write(['include', 'aaa.h'], r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT;
""")

test.write('bbb.h', r"""
void bbb(void);
""")

test.write('bbb.cpp', r"""
#include "my_qobject.h"
void bbb(void) Q_OBJECT
#include "bbb.moc"
""")

test.write(['ui', 'ccc.ui'], r"""
void ccc(void)
""")

test.write('ddd.cpp', r"""
#include "ddd.h"
""")

test.write(['include', 'ddd.h'], r"""
#include "my_qobject.h"
void ddd(void) Q_OBJECT;
""")

test.write('eee.h', r"""
void eee(void);
""")

test.write('eee.cpp', r"""
#include "my_qobject.h"
void eee(void) Q_OBJECT
#include "moc_eee.cpp"
""")

test.write(['ui', 'fff.ui'], r"""
void fff(void)
""")

test.write('main.cpp', r"""
#include "aaa.h"
#include "bbb.h"
#include "ui/ccc.h"
#include "ddd.h"
#include "eee.h"
#include "uic_fff.hpp"

int main(void) {
  aaa(); bbb(); ccc(); ddd(); eee(); fff(); return 0;
}
""")

test.run(arguments=aaa_exe)

# normal invocation
test.must_exist(test.workpath('include', 'moc_aaa.cc'))
test.must_exist(test.workpath('bbb.moc'))
test.must_exist(test.workpath('ui', 'ccc.h'))
test.must_exist(test.workpath('ui', 'uic_ccc.cc'))
test.must_exist(test.workpath('ui', 'moc_ccc.cc'))

# manual target spec.
test.must_exist(test.workpath('moc-ddd.cpp'))
test.must_exist(test.workpath('moc_eee.cpp'))
test.must_exist(test.workpath('include', 'uic_fff.hpp'))
test.must_exist(test.workpath('fff.cpp'))
test.must_exist(test.workpath('fff.moc.cpp'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
