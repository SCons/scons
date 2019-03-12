"""
This tests the MinGW  with MSVC tool.
"""

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

import sys

import TestSCons

test = TestSCons.TestSCons()

# MinGW is Windows only:
if sys.platform != 'win32':
    msg = "Skipping mingw test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

test.skip_if_not_msvc()

# control test: check for nologo and cl in env
test.write('SConstruct',"""
env=Environment(tools=['default'])
print('CCFLAGS=' + str(env['CCFLAGS']).strip())
print('CC=' + str(env['CC']).strip())
""")
test.run(arguments='-Q -s')
if('CCFLAGS=/nologo' not in test.stdout()
    or 'CC=cl' not in test.stdout()):
    test.fail_test()

# make sure windows msvc doesnt add bad mingw flags 
# and that gcc is selected
test.write('SConstruct',"""
env=Environment(tools=['default', 'mingw'])
print('CCFLAGS="' +  str(env['CCFLAGS']).strip() + '"')
print('CC=' +  str(env['CC']).strip())
""")
test.run(arguments='-Q -s')
if('CCFLAGS=""' not in test.stdout()
    or 'CC=gcc' not in test.stdout()):
    test.fail_test()

# msvc should overwrite the flags and use cl
test.write('SConstruct',"""
env=Environment(tools=['mingw', 'default'])
print('CCFLAGS=' + str(env['CCFLAGS']).strip())
print('CC=' + str(env['CC']).strip())
""")
test.run(arguments='-Q -s')
if('CCFLAGS=/nologo' not in test.stdout()
    or 'CC=cl' not in test.stdout()):
    test.fail_test()

# test that CCFLAGS are preserved
test.write('SConstruct',"""
env=Environment(tools=['mingw'], CCFLAGS='-myflag')
print(env['CCFLAGS'])
""")
test.run(arguments='-Q -s')
if '-myflag' not in test.stdout():
    test.fail_test()

# test that it handles a list
test.write('SConstruct',"""
env=Environment(tools=['mingw'], CCFLAGS=['-myflag', '-myflag2'])
print(str(env['CCFLAGS']))
""")
test.run(arguments='-Q -s')
if "['-myflag', '-myflag2']" not in test.stdout():
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
