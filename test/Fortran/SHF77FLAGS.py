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
Test handling of the dialect-specific FLAGS variable for shared objects,
using a mocked compiler.
"""

import sys

import TestSCons

_python_ = TestSCons._python_
_obj = TestSCons._shobj
obj_ = TestSCons.shobj_

test = TestSCons.TestSCons()
# ref: test/Fortran/fixture/myfortran_flags.py
test.file_fixture(['fixture', 'myfortran_flags.py'])

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(SHF77=r'%(_python_)s myfortran_flags.py g77')
env.Append(SHF77FLAGS='-x')
env.SharedObject(target='test09', source='test09.f77')
env.SharedObject(target='test10', source='test10.F77')
""" % locals())

test.write('test09.f77', "This is a .f77 file.\n#g77\n")
test.write('test10.F77', "This is a .F77 file.\n#g77\n")

test.run(arguments='.', stderr=None)
test.must_match(obj_ + 'test09' + _obj, " -c -x\nThis is a .f77 file.\n")
test.must_match(obj_ + 'test10' + _obj, " -c -x\nThis is a .F77 file.\n")

test.pass_test()
