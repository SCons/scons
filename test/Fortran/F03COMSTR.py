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
    f03pp = 'f03'
else:
    f03pp = 'f03pp'


test.write('SConstruct', """
env = Environment(F03COM = r'%(_python_)s mycompile.py f03 $TARGET $SOURCES',
                  F03COMSTR = 'Building f03 $TARGET from $SOURCES',
                  F03PPCOM = r'%(_python_)s mycompile.py f03pp $TARGET $SOURCES',
                  F03PPCOMSTR = 'Building f03pp $TARGET from $SOURCES',
                  OBJSUFFIX='.obj')
env.Object(source = 'test01.f03')
env.Object(source = 'test02.F03')
""" % locals())

test.write('test01.f03',        "A .f03 file.\n/*f03*/\n")
test.write('test02.F03',        "A .F03 file.\n/*%s*/\n" % f03pp)

test.run(stdout = test.wrap_stdout("""\
Building f03 test01.obj from test01.f03
Building %(f03pp)s test02.obj from test02.F03
""" % locals()))

test.must_match('test01.obj', "A .f03 file.\n")
test.must_match('test02.obj', "A .F03 file.\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
