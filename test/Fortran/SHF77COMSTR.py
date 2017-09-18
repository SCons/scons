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

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

if not TestSCons.case_sensitive_suffixes('.f','.F'):
    f77pp = 'f77'
else:
    f77pp = 'f77pp'


test.write('SConstruct', """
env = Environment(SHF77COM = r'%(_python_)s mycompile.py f77 $TARGET $SOURCES',
                  SHF77COMSTR = 'Building f77 $TARGET from $SOURCES',
                  SHF77PPCOM = r'%(_python_)s mycompile.py f77pp $TARGET $SOURCES',
                  SHF77PPCOMSTR = 'Building f77pp $TARGET from $SOURCES',
                  SHOBJPREFIX='', SHOBJSUFFIX='.shobj')
env.SharedObject(source = 'test09.f77')
env.SharedObject(source = 'test10.F77')
""" % locals())

test.write('test01.f',          "A .f file.\n/*f77*/\n")
test.write('test02.F',          "A .F file.\n/*%s*/\n" % f77pp)
test.write('test03.for',        "A .for file.\n/*f77*/\n")
test.write('test04.FOR',        "A .FOR file.\n/*%s*/\n" % f77pp)
test.write('test05.ftn',        "A .ftn file.\n/*f77*/\n")
test.write('test06.FTN',        "A .FTN file.\n/*%s*/\n" % f77pp)
test.write('test07.fpp',        "A .fpp file.\n/*f77pp*/\n")
test.write('test08.FPP',        "A .FPP file.\n/*f77pp*/\n")
test.write('test09.f77',        "A .f77 file.\n/*f77*/\n")
test.write('test10.F77',        "A .F77 file.\n/*%s*/\n" % f77pp)

test.run(stdout = test.wrap_stdout("""\
Building f77 test09.shobj from test09.f77
Building %(f77pp)s test10.shobj from test10.F77
""" % locals()))

test.must_match('test09.shobj', "A .f77 file.\n")
test.must_match('test10.shobj', "A .F77 file.\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
