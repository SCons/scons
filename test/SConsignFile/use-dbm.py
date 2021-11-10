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
Verify SConsignFile() when used with dbm.
"""
import os.path
import dbm
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

try:
    import dbm.ndbm
    use_dbm = 'dbm.ndbm'
except ImportError:
    test.skip_test('No dbm.ndbm in this version of Python; skipping test.\n')

test.subdir('subdir')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
sys.exit(0)
""")

database_name = test.get_sconsignname()
#
test.write('SConstruct', """
import %(use_dbm)s
SConsignFile('%(database_name)s', %(use_dbm)s)
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

# We don't check for explicit .db or other file, because base "dbm"
# can use different file extensions on different implementations.

database_name = test.get_sconsignname()
database_filename = database_name + '.dblite'
test.fail_test(
    os.path.exists(database_name) and 'dbm' not in dbm.whichdb(database_name),
    message="{} existed and wasn't any type of dbm file".format(database_name),
)
test.must_not_exist(test.workpath(database_filename))
test.must_not_exist(test.workpath('subdir', database_name))
test.must_not_exist(test.workpath('subdir', database_filename))

test.must_match('f1.out', "f1.in\n")
test.must_match('f2.out', "f2.in\n")
test.must_match(['subdir', 'f3.out'], "subdir/f3.in\n")
test.must_match(['subdir', 'f4.out'], "subdir/f4.in\n")

test.up_to_date(arguments='.')

test.fail_test(os.path.exists(database_name) and 'dbm' not in dbm.whichdb(database_name),
               message="{} existed and wasn't any type of dbm file".format(database_name))
test.must_not_exist(test.workpath(database_filename))
test.must_not_exist(test.workpath('subdir', database_name))
test.must_not_exist(test.workpath('subdir', database_filename))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
