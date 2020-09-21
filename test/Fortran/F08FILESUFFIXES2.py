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

import os
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.file_fixture('mylink.py')
test.file_fixture(['fixture', 'myfortran.py'])

# Test non-default file suffix: .f/.F for F08
test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  F77 = r'%(_python_)s myfortran.py f77',
                  F08 = r'%(_python_)s myfortran.py f08',
                  F08FILESUFFIXES = ['.f', '.F', '.f08', '.F08'],
                  tools = ['default', 'f08'])
env.Program(target = 'test01', source = 'test01.f')
env.Program(target = 'test02', source = 'test02.F')
env.Program(target = 'test03', source = 'test03.f08')
env.Program(target = 'test04', source = 'test04.F08')
env.Program(target = 'test05', source = 'test05.f77')
env.Program(target = 'test06', source = 'test06.F77')
""" % locals())

test.write('test01.f',   "This is a .f file.\n#link\n#f08\n")
test.write('test02.F',   "This is a .F file.\n#link\n#f08\n")
test.write('test03.f08', "This is a .f08 file.\n#link\n#f08\n")
test.write('test04.F08', "This is a .F08 file.\n#link\n#f08\n")
test.write('test05.f77', "This is a .f77 file.\n#link\n#f77\n")
test.write('test06.F77', "This is a .F77 file.\n#link\n#f77\n")

test.run(arguments = '.', stderr = None)

test.must_match('test01' + _exe, "This is a .f file.\n")
test.must_match('test02' + _exe, "This is a .F file.\n")
test.must_match('test03' + _exe, "This is a .f08 file.\n")
test.must_match('test04' + _exe, "This is a .F08 file.\n")
test.must_match('test05' + _exe, "This is a .f77 file.\n")
test.must_match('test06' + _exe, "This is a .F77 file.\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
