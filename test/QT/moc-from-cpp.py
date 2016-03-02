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
Create a moc file from a cpp file.
"""

import TestSCons

test = TestSCons.TestSCons()

test.Qt_dummy_installation()

##############################################################################

lib_aaa = TestSCons.lib_ + 'aaa' + TestSCons._lib
moc = 'aaa.moc'

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', """
Import("env dup")
if dup == 0: env.Append(CPPPATH=['.'])
env.StaticLibrary(target = '%s', source = ['aaa.cpp','useit.cpp'])
""" % lib_aaa)

test.write('aaa.h', r"""
void aaa(void);
""")

test.write('aaa.cpp', r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT
#include "%s"
""" % moc)

test.write('useit.cpp', r"""
#include "aaa.h"
void useit() {
  aaa();
}
""")

test.run(arguments=lib_aaa,
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.up_to_date(options = '-n', arguments = lib_aaa)

test.write('aaa.cpp', r"""
#include "my_qobject.h"
/* a change */
void aaa(void) Q_OBJECT
#include "%s"
""" % moc)

test.not_up_to_date(options = '-n', arguments = moc)

test.run(options = '-c', arguments = lib_aaa)

test.run(arguments = "variant_dir=1 " + test.workpath('build', lib_aaa),
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(arguments = "variant_dir=1 chdir=1 " + test.workpath('build', lib_aaa))

test.must_exist(test.workpath('build', moc))

test.run(arguments = "variant_dir=1 dup=0 " +
                     test.workpath('build_dup0', lib_aaa),
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.must_exist(test.workpath('build_dup0', moc))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
