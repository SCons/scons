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
    fortranpp = 'fortran'
else:
    fortranpp = 'fortranpp'


test.write('SConstruct', """
env = Environment(FORTRANCOM = r'%(_python_)s mycompile.py fortran $TARGET $SOURCES',
                  FORTRANCOMSTR = 'Building fortran $TARGET from $SOURCES',
                  FORTRANPPCOM = r'%(_python_)s mycompile.py fortranpp $TARGET $SOURCES',
                  FORTRANPPCOMSTR = 'Building fortranpp $TARGET from $SOURCES',
                  OBJSUFFIX='.obj')
env.Object(source = 'test01.f')
env.Object(source = 'test02.F')
env.Object(source = 'test03.for')
env.Object(source = 'test04.FOR')
env.Object(source = 'test05.ftn')
env.Object(source = 'test06.FTN')
env.Object(source = 'test07.fpp')
env.Object(source = 'test08.FPP')
""" % locals())

test.write('test01.f',          "A .f file.\n/*fortran*/\n")
test.write('test02.F',          "A .F file.\n/*%s*/\n" % fortranpp)
test.write('test03.for',        "A .for file.\n/*fortran*/\n")
test.write('test04.FOR',        "A .FOR file.\n/*%s*/\n" % fortranpp)
test.write('test05.ftn',        "A .ftn file.\n/*fortran*/\n")
test.write('test06.FTN',        "A .FTN file.\n/*%s*/\n" % fortranpp)
test.write('test07.fpp',        "A .fpp file.\n/*fortranpp*/\n")
test.write('test08.FPP',        "A .FPP file.\n/*fortranpp*/\n")

test.run(stdout = test.wrap_stdout("""\
Building fortran test01.obj from test01.f
Building %(fortranpp)s test02.obj from test02.F
Building fortran test03.obj from test03.for
Building %(fortranpp)s test04.obj from test04.FOR
Building fortran test05.obj from test05.ftn
Building %(fortranpp)s test06.obj from test06.FTN
Building fortranpp test07.obj from test07.fpp
Building fortranpp test08.obj from test08.FPP
""" % locals()))

test.must_match('test01.obj', "A .f file.\n")
test.must_match('test02.obj', "A .F file.\n")
test.must_match('test03.obj', "A .for file.\n")
test.must_match('test04.obj', "A .FOR file.\n")
test.must_match('test05.obj', "A .ftn file.\n")
test.must_match('test06.obj', "A .FTN file.\n")
test.must_match('test07.obj', "A .fpp file.\n")
test.must_match('test08.obj', "A .FPP file.\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
