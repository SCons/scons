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
Verify appending to CPPPDEFINES with various data types.
See also pkg-config.py in this dir.
"""

import TestSCons

test = TestSCons.TestSCons()

# Note: we explicitly set CPPDEFPREFIX here to simplify testing on
# Windows.

test.write('SConstruct', """\
env_1738_2 = Environment(CPPDEFPREFIX='-D')
env_1738_2['CPPDEFINES'] = ['FOO']
env_1738_2.Append(CPPDEFINES={'value' : '1'})
print(env_1738_2.subst('$_CPPDEFFLAGS'))
#env_1738_2.Object('test_1738_2', 'main.c')

# https://github.com/SCons/scons/issues/2300
env_2300_1 = Environment(CPPDEFINES = 'foo', CPPDEFPREFIX='-D')
env_2300_1.Append(CPPDEFINES='bar')
print(env_2300_1.subst('$_CPPDEFFLAGS'))

env_2300_2 = Environment(CPPDEFINES = ['foo'], CPPDEFPREFIX='-D') # note the list
env_2300_2.Append(CPPDEFINES='bar')
print(env_2300_2.subst('$_CPPDEFFLAGS'))

# https://github.com/SCons/scons/issues/1152
# https://github.com/SCons/scons/issues/2900
# Python3 dicts dont preserve order. Hence we supply subclass of OrderedDict
# whose __str__ and __repr__ act like a normal dict.
from collections import OrderedDict
class OrderedPrintingDict(OrderedDict):
    def __repr__(self):
        return '{' + ', '.join(['%r: %r'%(k, v) for (k, v) in self.items()]) + '}'

    __str__ = __repr__

    # Because dict-like objects (except dict and UserDict) are not deep copied
    # directly when constructing Environment(CPPDEFINES = OrderedPrintingDict(...))
    def __semi_deepcopy__(self):
        return self.copy()

cases=[('string', 'FOO'),
       ('list', ['NAME1', 'NAME2']),
       ('list-of-2lists', [('NAME1','VAL1'), ['NAME2','VAL2']]),
       ('dict', OrderedPrintingDict([('NAME2', 'VAL2'), ('NAME3', None), ('NAME1', 'VAL1')]))
       ]

for (t1, c1) in cases:
    for (t2, c2) in cases:
        print("==== Testing CPPDEFINES, appending a %s to a %s"%(t2, t1))
        print("   orig = %s, append = %s"%(c1, c2))
        env=Environment(CPPDEFINES = c1, CPPDEFPREFIX='-D')
        env.Append(CPPDEFINES = c2)
        final=env.subst('$_CPPDEFFLAGS',source="src", target="tgt")
        print('Append:\\n\\tresult=%s\\n\\tfinal=%s'%\\
              (env['CPPDEFINES'], final))
        env=Environment(CPPDEFINES = c1, CPPDEFPREFIX='-D')
        env.AppendUnique(CPPDEFINES = c2)
        final=env.subst('$_CPPDEFFLAGS',source="src", target="tgt")
        print('AppendUnique:\\n\\tresult=%s\\n\\tfinal=%s'%\\
              (env['CPPDEFINES'], final))
""")


expect_print_output="""\
-DFOO -Dvalue=1
-Dfoo -Dbar
-Dfoo -Dbar
==== Testing CPPDEFINES, appending a string to a string
   orig = FOO, append = FOO
Append:
	result=['FOO', 'FOO']
	final=-DFOO -DFOO
AppendUnique:
	result=['FOO']
	final=-DFOO
==== Testing CPPDEFINES, appending a list to a string
   orig = FOO, append = ['NAME1', 'NAME2']
Append:
	result=['FOO', 'NAME1', 'NAME2']
	final=-DFOO -DNAME1 -DNAME2
AppendUnique:
	result=[('FOO',), ('NAME1',), ('NAME2',)]
	final=-DFOO -DNAME1 -DNAME2
==== Testing CPPDEFINES, appending a list-of-2lists to a string
   orig = FOO, append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
	result=['FOO', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
	final=-DFOO -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
	result=[('FOO',), ('NAME1', 'VAL1'), ('NAME2', 'VAL2')]
	final=-DFOO -DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a string
   orig = FOO, append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
	result=['FOO', {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}]
	final=-DFOO -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
	result=['FOO', ('NAME2', 'VAL2'), 'NAME3', ('NAME1', 'VAL1')]
	final=-DFOO -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a string to a list
   orig = ['NAME1', 'NAME2'], append = FOO
Append:
	result=['NAME1', 'NAME2', 'FOO']
	final=-DNAME1 -DNAME2 -DFOO
AppendUnique:
	result=[('NAME1',), ('NAME2',), ('FOO',)]
	final=-DNAME1 -DNAME2 -DFOO
==== Testing CPPDEFINES, appending a list to a list
   orig = ['NAME1', 'NAME2'], append = ['NAME1', 'NAME2']
Append:
	result=['NAME1', 'NAME2', 'NAME1', 'NAME2']
	final=-DNAME1 -DNAME2 -DNAME1 -DNAME2
AppendUnique:
	result=[('NAME1',), ('NAME2',)]
	final=-DNAME1 -DNAME2
==== Testing CPPDEFINES, appending a list-of-2lists to a list
   orig = ['NAME1', 'NAME2'], append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
	result=['NAME1', 'NAME2', ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
	final=-DNAME1 -DNAME2 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
	result=[('NAME1',), ('NAME2',), ('NAME1', 'VAL1'), ('NAME2', 'VAL2')]
	final=-DNAME1 -DNAME2 -DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a list
   orig = ['NAME1', 'NAME2'], append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
	result=['NAME1', 'NAME2', {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}]
	final=-DNAME1 -DNAME2 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
	result=[('NAME1',), ('NAME2',), ('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1')]
	final=-DNAME1 -DNAME2 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a string to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = FOO
Append:
	result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'FOO']
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DFOO
AppendUnique:
	result=[('NAME1', 'VAL1'), ('NAME2', 'VAL2'), ('FOO',)]
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DFOO
==== Testing CPPDEFINES, appending a list to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = ['NAME1', 'NAME2']
Append:
	result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], 'NAME1', 'NAME2']
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1 -DNAME2
AppendUnique:
	result=[('NAME1', 'VAL1'), ('NAME2', 'VAL2'), ('NAME1',), ('NAME2',)]
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1 -DNAME2
==== Testing CPPDEFINES, appending a list-of-2lists to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
	result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
	result=[('NAME1', 'VAL1'), ('NAME2', 'VAL2')]
	final=-DNAME1=VAL1 -DNAME2=VAL2
==== Testing CPPDEFINES, appending a dict to a list-of-2lists
   orig = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']], append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
	result=[('NAME1', 'VAL1'), ['NAME2', 'VAL2'], {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}]
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
AppendUnique:
	result=[('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1')]
	final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a string to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = FOO
Append:
	result={'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1', 'FOO': None}
	final=-DFOO -DNAME1=VAL1 -DNAME2=VAL2 -DNAME3
AppendUnique:
	result=[('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1'), 'FOO']
	final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DFOO
==== Testing CPPDEFINES, appending a list to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = ['NAME1', 'NAME2']
Append:
	result=[('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1'), 'NAME1', 'NAME2']
	final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1 -DNAME2
AppendUnique:
	result=[('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1'), ('NAME1',), ('NAME2',)]
	final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1 -DNAME2
==== Testing CPPDEFINES, appending a list-of-2lists to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = [('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
Append:
	result=[('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1'), ('NAME1', 'VAL1'), ['NAME2', 'VAL2']]
	final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1 -DNAME1=VAL1 -DNAME2=VAL2
AppendUnique:
	result=[('NAME2', 'VAL2'), ('NAME3',), ('NAME1', 'VAL1')]
	final=-DNAME2=VAL2 -DNAME3 -DNAME1=VAL1
==== Testing CPPDEFINES, appending a dict to a dict
   orig = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}, append = {'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
Append:
	result={'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3
AppendUnique:
	result={'NAME2': 'VAL2', 'NAME3': None, 'NAME1': 'VAL1'}
	final=-DNAME1=VAL1 -DNAME2=VAL2 -DNAME3
"""

build_output="scons: `.' is up to date.\n"

expect = test.wrap_stdout(build_str=build_output,
                          read_str = expect_print_output)
test.run(arguments = '.', stdout=expect)
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
