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
Test Qt with a copied construction environment.
"""

import string

import TestSCons

test = TestSCons.TestSCons()

test.Qt_dummy_installation()

test.Qt_create_SConstruct('SConstruct')

test.write('SConscript', """\
Import("env")
env.Append(CPPDEFINES = ['FOOBAZ'])
                                                                                
copy = env.Clone()
copy.Append(CPPDEFINES = ['MYLIB_IMPL'])
                                                                                
copy.SharedLibrary(
   target = 'MyLib',
   source = ['MyFile.cpp','MyForm.ui']
)
""")

test.write('MyFile.h', r"""
void aaa(void);
""")

test.write('MyFile.cpp', r"""
#include "MyFile.h"
void useit() {
  aaa();
}
""")

test.write('MyForm.ui', r"""
void aaa(void)
""")

test.run()

moc_MyForm = filter(lambda x: string.find(x, 'moc_MyForm') != -1,
                    string.split(test.stdout(), '\n'))

MYLIB_IMPL = filter(lambda x: string.find(x, 'MYLIB_IMPL') != -1, moc_MyForm)

if not MYLIB_IMPL:
    print "Did not find MYLIB_IMPL on moc_MyForm compilation line:"
    print test.stdout()
    test.fail_test()

test.pass_test()
