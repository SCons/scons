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
Test that the $SHLINKCOMSTR construction variable allows you to customize
the displayed linker string for programs using shared libraries.
"""

import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

test.write('SConstruct', """
env = Environment(SHCCCOM = r'%(_python_)s mycompile.py cc $TARGET $SOURCES',
                  SHLINKCOM = r'%(_python_)s mycompile.py link $TARGET $SOURCES',
                  SHLINKCOMSTR = 'Linking shared $TARGET from $SOURCES',
                  SHOBJPREFIX = '',
                  SHOBJSUFFIX = '.obj',
                  SHLIBPREFIX = '',
                  SHLIBSUFFIX = '.dll')
t1 = env.SharedObject('test1', 'test1.c')
t2 = env.SharedObject('test2', 'test2.c')
env.SharedLibrary(target = 'test3', source = [t1, t2])
""" % locals())

test.write('test1.c', """\
test1.c
/*cc*/
/*link*/
""")

test.write('test2.c', """\
test2.c
/*cc*/
/*link*/
""")

test.run(stdout = test.wrap_stdout("""\
%(_python_)s mycompile.py cc test1.obj test1.c
%(_python_)s mycompile.py cc test2.obj test2.c
Linking shared test3.dll from test1.obj test2.obj
""" % locals()))

test.must_match('test3.dll', "test1.c\ntest2.c\n")

if sys.platform == "win32":
    import SCons.Tool.MSCommon as msc
    if msc.msvc_exists():
        # Now test an actual compile and link.  Since MS Windows
        # resets the link actions, this could fail even if the above
        # test passed.
        test.write('SConstruct', """
env = Environment(CXXCOMSTR    = 'Compiling $TARGET ...',
                 SHLINKCOMSTR   = 'Shared-Linking $TARGET ...')
env.SharedLibrary('test', 'test.cpp')
""")
        test.write('test.cpp', """
int i;
""")

        test.run()
        if "Shared-Linking" not in test.stdout():
            test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
