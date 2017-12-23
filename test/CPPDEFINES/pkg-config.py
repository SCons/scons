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
Verify merging with MergeFlags to CPPPDEFINES with various data types.
"""

import TestSCons
from SCons.Environment import Base

test = TestSCons.TestSCons()

pkg_config_path = test.where_is('pkg-config')
if not pkg_config_path:
    test.skip_test("Could not find 'pkg-config' in system PATH, skipping test.\n")
    
if Base()['PLATFORM'] == 'win32':
    test.skip_test("pkg-config test not setup for windows, skipping test.\n")

test.write('bug.pc', """\
prefix=/usr
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: bug
Description: A test case .pc file
Version: 1.2
Cflags: -DSOMETHING -DVARIABLE=2
""")

test.write('main.c', """\
int main(int argc, char *argv[])
{
  return 0;
}
""")

test.write('SConstruct', """\
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
""" + """
# http://scons.tigris.org/issues/show_bug.cgi?id=2671
# Passing test cases
env_1 = Environment(CPPDEFINES=[('DEBUG','1'), 'TEST'])
env_1.ParseConfig('PKG_CONFIG_PATH=. %(pkg_config_path)s --cflags bug')
print(env_1.subst('$_CPPDEFFLAGS'))

env_2 = Environment(CPPDEFINES=[('DEBUG','1'), 'TEST'])
env_2.MergeFlags('-DSOMETHING -DVARIABLE=2')
print(env_2.subst('$_CPPDEFFLAGS'))

# Failing test cases
env_3 = Environment(CPPDEFINES=OrderedPrintingDict([('DEBUG', 1), ('TEST', None)]))
env_3.ParseConfig('PKG_CONFIG_PATH=. %(pkg_config_path)s --cflags bug')
print(env_3.subst('$_CPPDEFFLAGS'))

env_4 = Environment(CPPDEFINES=OrderedPrintingDict([('DEBUG', 1), ('TEST', None)]))
env_4.MergeFlags('-DSOMETHING -DVARIABLE=2')
print(env_4.subst('$_CPPDEFFLAGS'))

# http://scons.tigris.org/issues/show_bug.cgi?id=1738
env_1738_1 = Environment(tools=['default'])
env_1738_1.ParseConfig('PKG_CONFIG_PATH=. %(pkg_config_path)s --cflags --libs bug')
env_1738_1.Append(CPPDEFINES={'value' : '1'})
print(env_1738_1.subst('$_CPPDEFFLAGS'))
"""%locals() )

expect_print_output="""\
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DSOMETHING -DVARIABLE=2 -Dvalue=1
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
