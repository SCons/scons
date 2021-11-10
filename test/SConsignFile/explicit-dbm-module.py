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

"""Verify SConsignFile() when used with explicit SCons.dblite."""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

use_db = 'SCons.dblite'

test.subdir('subdir')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
sys.exit(0)
""")

test.write('SConstruct', """
import %(use_db)s
SConsignFile(dbm_module=%(use_db)s)
DefaultEnvironment(tools=[])
B = Builder(action=r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS={'B': B}, tools=[])
env.B(target='f1.out', source='f1.in')
env.B(target='f2.out', source='f2.in')
env.B(target='subdir/f3.out', source='subdir/f3.in')
env.B(target='subdir/f4.out', source='subdir/f4.in')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write(['subdir', 'f3.in'], "subdir/f3.in\n")
test.write(['subdir', 'f4.in'], "subdir/f4.in\n")

test.run()

database_name = test.get_sconsignname()
database_filename = database_name + ".dblite"

test.must_exist(test.workpath(database_filename))
test.must_not_exist(test.workpath(database_name))
test.must_not_exist(test.workpath('subdir', database_name))

test.must_match('f1.out', "f1.in\n")
test.must_match('f2.out', "f2.in\n")
test.must_match(['subdir', 'f3.out'], "subdir/f3.in\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\n")

test.up_to_date(arguments='.')

test.must_exist(test.workpath(database_filename))
test.must_not_exist(test.workpath(database_name))
test.must_not_exist(test.workpath('subdir', database_name))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
