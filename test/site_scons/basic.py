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

import TestSCons

"""
Verify basic functionality of the site_scons dir and
site_scons/site_init.py file:
Make sure the site_scons/site_init.py file gets loaded,
and make sure a tool can be loaded from the site_scons/site_tools subdir,
even when executing out of a subdirectory.
"""

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


test.write('SConstruct', """
e=Environment(tools=['default', 'mytool'])
print(e.subst('My site tool is $MYTOOL'))
""")

test.run(arguments = '-Q .',
         stdout = """Hi there, I am in site_scons/site_init.py!
My site tool is mytool
scons: `.' is up to date.\n""")



test.pass_test()

# end of file

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
