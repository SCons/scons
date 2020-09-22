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

import TestSCons

_python_ = TestSCons._python_
_obj   = TestSCons._shobj
obj_   = TestSCons.shobj_

test = TestSCons.TestSCons()

test.file_fixture(['fixture', 'myfortran.py'])

test.write('SConstruct', """
env = Environment(SHF03 = r'%(_python_)s myfortran.py g03',
                  SHFORTRAN = r'%(_python_)s myfortran.py fortran')
env.SharedObject(target = 'test01', source = 'test01.f')
env.SharedObject(target = 'test02', source = 'test02.F')
env.SharedObject(target = 'test03', source = 'test03.for')
env.SharedObject(target = 'test04', source = 'test04.FOR')
env.SharedObject(target = 'test05', source = 'test05.ftn')
env.SharedObject(target = 'test06', source = 'test06.FTN')
env.SharedObject(target = 'test07', source = 'test07.fpp')
env.SharedObject(target = 'test08', source = 'test08.FPP')
env.SharedObject(target = 'test13', source = 'test13.f03')
env.SharedObject(target = 'test14', source = 'test14.F03')
""" % locals())

test.write('test01.f',   "This is a .f file.\n#fortran\n")
test.write('test02.F',   "This is a .F file.\n#fortran\n")
test.write('test03.for', "This is a .for file.\n#fortran\n")
test.write('test04.FOR', "This is a .FOR file.\n#fortran\n")
test.write('test05.ftn', "This is a .ftn file.\n#fortran\n")
test.write('test06.FTN', "This is a .FTN file.\n#fortran\n")
test.write('test07.fpp', "This is a .fpp file.\n#fortran\n")
test.write('test08.FPP', "This is a .FPP file.\n#fortran\n")
test.write('test13.f03', "This is a .f03 file.\n#g03\n")
test.write('test14.F03', "This is a .F03 file.\n#g03\n")

test.run(arguments = '.', stderr = None)

test.must_match(obj_ + 'test01' + _obj, "This is a .f file.\n")
test.must_match(obj_ + 'test02' + _obj, "This is a .F file.\n")
test.must_match(obj_ + 'test03' + _obj, "This is a .for file.\n")
test.must_match(obj_ + 'test04' + _obj, "This is a .FOR file.\n")
test.must_match(obj_ + 'test05' + _obj, "This is a .ftn file.\n")
test.must_match(obj_ + 'test06' + _obj, "This is a .FTN file.\n")
test.must_match(obj_ + 'test07' + _obj, "This is a .fpp file.\n")
test.must_match(obj_ + 'test08' + _obj, "This is a .FPP file.\n")
test.must_match(obj_ + 'test13' + _obj, "This is a .f03 file.\n")
test.must_match(obj_ + 'test14' + _obj, "This is a .F03 file.\n")

fc = 'f03'
g03 = test.detect_tool(fc)

if g03:

    test.file_fixture('wrapper.py')

    test.write('SConstruct', """
foo = Environment(SHF03 = '%(fc)s')
shf03 = foo.Dictionary('SHF03')
bar = foo.Clone(SHF03 = r'%(_python_)s wrapper.py ' + shf03)
foo.SharedObject(target = 'foo/foo', source = 'foo.f03')
bar.SharedObject(target = 'bar/bar', source = 'bar.f03')
""" % locals())

    test.write('foo.f03', r"""
      PROGRAM FOO
      PRINT *,'foo.f03'
      STOP
      END
""")

    test.write('bar.f03', r"""
      PROGRAM BAR
      PRINT *,'bar.f03'
      STOP
      END
""")


    test.run(arguments = 'foo', stderr = None)

    test.must_not_exist('wrapper.out')

    import sys
    if sys.platform[:5] == 'sunos':
        test.run(arguments = 'bar', stderr = None)
    else:
        test.run(arguments = 'bar')

    test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
