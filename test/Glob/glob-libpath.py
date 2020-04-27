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

"""
Verify that Glob() in a subdir doesn't corrupt LIBPATH.
See bug #2184, "Glob pollutes LIBPATH" from Ian P. Cardenas.
Test output should not contain -Lsrc/util.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src', ['src', 'util'])

test.write('SConstruct', """\
base_env = Environment()
Export('base_env')
swat = base_env.SConscript('src/SConscript', variant_dir='build')
Default(swat)
""")

test.write('SConstruct', """\
base_env = Environment()
Export('base_env')
swat = base_env.SConscript('src/SConscript', variant_dir='build')
Default(swat)
""")

test.write(['src', 'SConscript'], """Import('base_env')

libutil = base_env.SConscript('util/SConscript')

env = base_env.Clone()
env.AppendUnique( LIBPATH = 'util')
env.AppendUnique( LIBS = libutil )

swat = env.Program( 'main', 'main.cpp' )

Return('swat')
""")

test.write(['src', 'main.cpp'], """int main(void) { return 0; }
""")


test.write(['src', 'util', 'SConscript'], """Import('base_env')
libutil = base_env.Library('util', Glob('*.cpp'))
Return('libutil')
""")

test.write(['src', 'util', 'util.cpp'], """int i=0;
""")

test.run(arguments = '-Q .')
if not test.match_re_dotall(test.stdout(), r".*(-L|/LIBPATH:)build[/\\]util.*"):
    print(repr(test.stdout())+" should contain -Lbuild/util or /LIBPATH:build\\util")
    test.fail_test()
if test.match_re_dotall(test.stdout(), r".*(-L|/LIBPATH:)src[/\\]util.*"):
    print(repr(test.stdout())+" should not contain -Lsrc/util or /LIBPATH:src\\util")
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
