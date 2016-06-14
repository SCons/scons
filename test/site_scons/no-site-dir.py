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
Verify use of the --no-site-dir option:
the site_scons/site_init.py script should NOT be loaded.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('site_scons', ['site_scons', 'site_tools'])

test.write(['site_scons', 'site_init.py'], """
from SCons.Script import *
print("Hi there, I am in site_scons/site_init.py!")
""")

test.write(['site_scons', 'site_tools', 'mytool.py'], """
import SCons.Tool
def generate(env):
    env['MYTOOL']='mytool'
def exists(env):
    return 1
""")

test.write(['site_scons', 'site_tools', 'm4.py'], """
import SCons.Tool
def generate(env):
    env['M4']='my_m4'
    env['M4_MINE']=1
def exists(env):
    return 1
""")

test.write('SConstruct', """
e=Environment()
""")

test.run(arguments = '-Q --no-site-dir .',
         stdout = "scons: `.' is up to date.\n")

# With --no-site-dir, shouldn't override default m4 tool

test.write('SConstruct', """
e=Environment()
print(e.subst('no site: M4 is $M4, M4_MINE is $M4_MINE'))
""")

test.run(arguments = '-Q --no-site-dir .')

not_expected = """Hi there, I am in site_scons/site_init.py!
no site: M4 is my_m4, M4_MINE is 1
scons: `.' is up to date.
"""

test.fail_test(test.stdout() == not_expected)



test.pass_test()

# end of file

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
