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
Test that the $LINKCOMSTR construction variable allows you to customize
the displayed linker string.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

test.write('SConstruct', """
env = Environment(LINKCOM = r'%(_python_)s mycompile.py link $TARGET $SOURCES',
                  LINKCOMSTR = 'Linking $TARGET from $SOURCES',
                  OBJSUFFIX = '.obj',
                  PROGSUFFIX = '.exe')
env.Program(target = 'test1', source = ['test1.obj', 'test2.obj'])
""" % locals())

test.write('test1.obj', """\
test1.obj
/*link*/
""")

test.write('test2.obj', """\
test2.obj
/*link*/
""")

test.run(stdout = test.wrap_stdout("""\
Linking test1.exe from test1.obj test2.obj
"""))

test.must_match('test1.exe', "test1.obj\ntest2.obj\n")

# Now test an actual compile and link.  Since MS Windows
# resets the link actions, this could fail even if the above
# test passed.
test.write('SConstruct', """
env = Environment(CXXCOMSTR    = 'Compiling $TARGET ...',
                  LINKCOMSTR   = 'Linking $TARGET ...')
env.Program('test', 'test.cpp')
""")

test.write('test.cpp', """
int main(int argc, char **argv) {}
""")

test.run()
if "Linking" not in test.stdout():
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
