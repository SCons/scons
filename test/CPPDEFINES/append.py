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
Verify appending to CPPPDEFINES with various data types.
See also pkg-config.py in this dir.
"""

import TestSCons

test = TestSCons.TestSCons()

# Note: explicitly set CPPDEFPREFIX here to simplify testing on Windows.

# Link: fixture/SConstruct-Append
test.file_fixture(["fixture", "SConstruct-Append"], "SConstruct")

expect_print_output="""\
-DFOO -Dvalue=1
-Dfoo -Dbar
-Dfoo -Dbar
-Dfoo -Dbar -Dbaz
-Dfoo bar -Dbaz
-Dfoo -Dbar baz
-Dfoo -Dbar -Dbaz
-DMacro2=Value2 -DMacro4 -DMacro3=Value3 -DMacro1=Value1
-DMacro1=Value1
-DMacro1 -DValue1
==== Testing CPPDEFINES, appending a string to a string
   orig = 'FOO', append = 'FOO'
Append:
    result=['FOO', 'FOO']
    final=-DFOO -DFOO
AppendUnique:
    result=['FOO']
    final=-DFOO
==== Testing CPPDEFINES, appending a valuestring to a string
   orig = 'FOO', append = 'NAME1=VAL1'
Append:
    result=['FOO', 'NAME1=VAL1']
    final=-DFOO -DNAME1=VAL1
AppendUnique:
    result=['FOO', 'NAME1=VAL1']
    final=-DFOO -DNAME1=VAL1
==== Testing CPPDEFINES, appending a list to a string
   orig = 'FOO', append = ['NAME1', 'NAME2', 'NAME3']
Append:
    result=['FOO', 'NAME1', 'NAME2', 'NAME3']
    final=-DFOO -DNAME1 -DNAME2 -DNAME3
AppendUnique:
    result=['FOO', 'NAME1', 'NAME2', 'NAME3']
    final=-DFOO -DNAME1 -DNAME2 -DNAME3
==== Testing CPPDEFINES, appending a tuple to a string
   orig = 'FOO', append = ('NAME1', 'VAL1')
Append:
    result=['FOO', ('NAME1', 'VAL1')]
    final=-DFOO -DNAME1=VAL1
AppendUnique:
    result=['FOO', ('NAME1', 'VAL1')]
    final=-DFOO -DNAME1=VAL1
==== Testing CPPDEFINES, appending a list-of-2lists to a string
   orig = 'FOO', append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
    result=['FOO', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DFOO -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
    result=['FOO', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DFOO -DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a string
   orig = 'FOO', append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
    result=['FOO', ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DFOO -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=['FOO', ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DFOO -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a string to a valuestring
   orig = 'NAME1=VAL1', append = 'FOO'
Append:
    result=['NAME1=VAL1', 'FOO']
    final=-DNAME1=VAL1 -DFOO
AppendUnique:
    result=['NAME1=VAL1', 'FOO']
    final=-DNAME1=VAL1 -DFOO
==== Testing CPPDEFINES, appending a valuestring to a valuestring
   orig = 'NAME1=VAL1', append = 'NAME1=VAL1'
Append:
    result=['NAME1=VAL1', 'NAME1=VAL1']
    final=-DNAME1=VAL1 -DNAME1=VAL1
AppendUnique:
    result=['NAME1=VAL1']
    final=-DNAME1=VAL1
==== Testing CPPDEFINES, appending a list to a valuestring
   orig = 'NAME1=VAL1', append = ['NAME1', 'NAME2', 'NAME3']
Append:
    result=['NAME1=VAL1', 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1=VAL1 -DNAME1 -DNAME2 -DNAME3
AppendUnique:
    result=['NAME1=VAL1', 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1=VAL1 -DNAME1 -DNAME2 -DNAME3
==== Testing CPPDEFINES, appending a tuple to a valuestring
   orig = 'NAME1=VAL1', append = ('NAME1', 'VAL1')
Append:
    result=['NAME1=VAL1', ('NAME1', 'VAL1')]
    final=-DNAME1=VAL1 -DNAME1=VAL1
AppendUnique:
    result=['NAME1=VAL1']
    final=-DNAME1=VAL1
==== Testing CPPDEFINES, appending a list-of-2lists to a valuestring
   orig = 'NAME1=VAL1', append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
    result=['NAME1=VAL1', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
    result=['NAME1=VAL1', ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a valuestring
   orig = 'NAME1=VAL1', append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
    result=['NAME1=VAL1', ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=['NAME1=VAL1', ('NAME2', 'VAL2'), ('NAME3', None)]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3
==== Testing CPPDEFINES, appending a string to a list
   orig = ['NAME1', 'NAME2', 'NAME3'], append = 'FOO'
Append:
    result=['NAME1', 'NAME2', 'NAME3', 'FOO']
    final=-DNAME1 -DNAME2 -DNAME3 -DFOO
AppendUnique:
    result=['NAME1', 'NAME2', 'NAME3', 'FOO']
    final=-DNAME1 -DNAME2 -DNAME3 -DFOO
==== Testing CPPDEFINES, appending a valuestring to a list
   orig = ['NAME1', 'NAME2', 'NAME3'], append = 'NAME1=VAL1'
Append:
    result=['NAME1', 'NAME2', 'NAME3', 'NAME1=VAL1']
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=['NAME1', 'NAME2', 'NAME3', 'NAME1=VAL1']
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a list to a list
   orig = ['NAME1', 'NAME2', 'NAME3'], append = ['NAME1', 'NAME2', 'NAME3']
Append:
    result=['NAME1', 'NAME2', 'NAME3', 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1 -DNAME2 -DNAME3
AppendUnique:
    result=['NAME1', 'NAME2', 'NAME3']
    final=-DNAME1 -DNAME2 -DNAME3
==== Testing CPPDEFINES, appending a tuple to a list
   orig = ['NAME1', 'NAME2', 'NAME3'], append = ('NAME1', 'VAL1')
Append:
    result=['NAME1', 'NAME2', 'NAME3', ('NAME1', 'VAL1')]
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=['NAME1', 'NAME2', 'NAME3', ('NAME1', 'VAL1')]
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a list-of-2lists to a list
   orig = ['NAME1', 'NAME2', 'NAME3'], append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
    result=['NAME1', 'NAME2', 'NAME3', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
    result=['NAME1', 'NAME2', 'NAME3', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a list
   orig = ['NAME1', 'NAME2', 'NAME3'], append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
    result=['NAME1', 'NAME2', 'NAME3', ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=['NAME1', 'NAME2', 'NAME3', ('NAME2', 'VAL2'), ('NAME1', 'VAL1')]
    final=-DNAME1 -DNAME2 -DNAME3 -DNAME2=VAL2 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a string to a tuple
   orig = ('NAME1', 'VAL1'), append = 'FOO'
Append:
    result=[('NAME1', 'VAL1'), 'FOO']
    final=-DNAME1=VAL1 -DFOO
AppendUnique:
    result=[('NAME1', 'VAL1'), 'FOO']
    final=-DNAME1=VAL1 -DFOO
==== Testing CPPDEFINES, appending a valuestring to a tuple
   orig = ('NAME1', 'VAL1'), append = 'NAME1=VAL1'
Append:
    result=[('NAME1', 'VAL1'), 'NAME1=VAL1']
    final=-DNAME1=VAL1 -DNAME1=VAL1
AppendUnique:
    result=[('NAME1', 'VAL1')]
    final=-DNAME1=VAL1
==== Testing CPPDEFINES, appending a list to a tuple
   orig = ('NAME1', 'VAL1'), append = ['NAME1', 'NAME2', 'NAME3']
Append:
    result=[('NAME1', 'VAL1'), 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1=VAL1 -DNAME1 -DNAME2 -DNAME3
AppendUnique:
    result=[('NAME1', 'VAL1'), 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1=VAL1 -DNAME1 -DNAME2 -DNAME3
==== Testing CPPDEFINES, appending a tuple to a tuple
   orig = ('NAME1', 'VAL1'), append = ('NAME1', 'VAL1')
Append:
    result=[('NAME1', 'VAL1'), ('NAME1', 'VAL1')]
    final=-DNAME1=VAL1 -DNAME1=VAL1
AppendUnique:
    result=[('NAME1', 'VAL1')]
    final=-DNAME1=VAL1
==== Testing CPPDEFINES, appending a list-of-2lists to a tuple
   orig = ('NAME1', 'VAL1'), append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
    result=[('NAME1', 'VAL1'), ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a tuple
   orig = ('NAME1', 'VAL1'), append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
    result=[('NAME1', 'VAL1'), ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=[('NAME1', 'VAL1'), ('NAME2', 'VAL2'), ('NAME3', None)]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3
==== Testing CPPDEFINES, appending a string to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = 'FOO'
Append:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'FOO']
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DFOO
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'FOO']
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DFOO
==== Testing CPPDEFINES, appending a valuestring to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = 'NAME1=VAL1'
Append:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'NAME1=VAL1']
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1=VAL1
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a list to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = ['NAME1', 'NAME2', 'NAME3']
Append:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1 -DNAME2 -DNAME3
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1 -DNAME2 -DNAME3
==== Testing CPPDEFINES, appending a tuple to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = ('NAME1', 'VAL1')
Append:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], ('NAME1', 'VAL1')]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1=VAL1
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a list-of-2lists to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], ('NAME3', None)]
    final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3
==== Testing CPPDEFINES, appending a string to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = 'FOO'
Append:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), 'FOO']
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DFOO
AppendUnique:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), 'FOO']
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DFOO
==== Testing CPPDEFINES, appending a valuestring to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = 'NAME1=VAL1'
Append:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), 'NAME1=VAL1']
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1=VAL1
AppendUnique:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a list to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = ['NAME1', 'NAME2', 'NAME3']
Append:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), 'NAME1', 'NAME2', 'NAME3']
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1 -DNAME2 -DNAME3
AppendUnique:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), 'NAME1', 'NAME2']
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1 -DNAME2
==== Testing CPPDEFINES, appending a tuple to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = ('NAME1', 'VAL1')
Append:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), ('NAME1', 'VAL1')]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1=VAL1
AppendUnique:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a list-of-2lists to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a dict to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1'), ('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
    result=[('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]
    final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
"""

build_output="scons: `.' is up to date.\n"
expect = test.wrap_stdout(build_str=build_output, read_str=expect_print_output)
test.run(arguments='.', stdout=expect)
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
