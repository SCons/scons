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
Create .cpp, .h, moc_....cpp from a .ui file.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.Qt_dummy_installation()

##############################################################################

aaa_dll = TestSCons.dll_ + 'aaa' + TestSCons._dll
moc = 'moc_aaa.cc'
cpp = 'uic_aaa.cc'
obj = TestSCons.shobj_ + os.path.splitext(cpp)[0] + TestSCons._shobj
h = 'aaa.h'

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', """\
Import("env dup")
if dup == 0: env.Append(CPPPATH=['#', '.'])
env.SharedLibrary(target = 'aaa', source = ['aaa.ui', 'useit.cpp'])
""")

test.write('aaa.ui', r"""
#if defined (_WIN32) || defined(__CYGWIN__)
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
DLLEXPORT void aaa(void)
""")

test.write('useit.cpp', r"""
#include "aaa.h"
void useit() {
  aaa();
}
""")

test.run(arguments = aaa_dll)

test.up_to_date(options='-n', arguments = aaa_dll)

test.write('aaa.ui', r"""
/* a change */
#if defined (_WIN32) || defined(__CYGWIN__)
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
DLLEXPORT void aaa(void)
""")

test.not_up_to_date(options = '-n', arguments = moc)
test.not_up_to_date(options = '-n', arguments = cpp)
test.not_up_to_date(options = '-n', arguments = h)

test.run(arguments = aaa_dll)

test.write('aaa.ui', r"""
void aaa(void)
//<include>aaa.ui.h</include>
""")

# test that non-existant ui.h files are ignored (as uic does)
test.run(arguments = aaa_dll)

test.write('aaa.ui.h', r"""
/* test dependency to .ui.h */
""")

test.run(arguments = aaa_dll)

test.write('aaa.ui.h', r"""
/* changed */
""")

test.not_up_to_date(options = '-n', arguments = obj)
test.not_up_to_date(options = '-n', arguments = cpp)
test.not_up_to_date(options = '-n', arguments = h)
test.not_up_to_date(options = '-n', arguments = moc)

# clean up
test.run(arguments = '-c ' + aaa_dll)

test.run(arguments = "variant_dir=1 " +
                     test.workpath('build', aaa_dll) )

test.must_exist(test.workpath('build', moc))
test.must_exist(test.workpath('build', cpp))
test.must_exist(test.workpath('build', h))
test.must_not_exist(test.workpath(moc))
test.must_not_exist(test.workpath(cpp))
test.must_not_exist(test.workpath(h))

cppContents = test.read(test.workpath('build', cpp), mode='r')
test.fail_test(cppContents.find('#include "aaa.ui.h"') == -1)

test.run(arguments = "variant_dir=1 chdir=1 " +
                     test.workpath('build', aaa_dll) )

test.must_exist(test.workpath('build', moc))
test.must_exist(test.workpath('build', cpp))
test.must_exist(test.workpath('build', h))
test.must_not_exist(test.workpath(moc))
test.must_not_exist(test.workpath(cpp))
test.must_not_exist(test.workpath(h))

test.run(arguments = "variant_dir=1 chdir=1 dup=0 " +
                     test.workpath('build_dup0', aaa_dll) )

test.must_exist(test.workpath('build_dup0',moc))
test.must_exist(test.workpath('build_dup0',cpp))
test.must_exist(test.workpath('build_dup0',h))
test.must_not_exist(test.workpath(moc))
test.must_not_exist(test.workpath(cpp))
test.must_not_exist(test.workpath(h))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
