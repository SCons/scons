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

import os.path
import TestSCons

test = TestSCons.TestSCons()


test.write('SConstruct', """
# Test where tools are located under site_scons/site_tools
env1 = Environment(tools=['subdir1.Site_TestTool1', 'subdir1.subdir2.Site_TestTool2', 'subdir1.Site_TestTool3'])
print("env1['Site_TestTool1'] =", env1.get('Site_TestTool1'))
print("env1['Site_TestTool2'] =", env1.get('Site_TestTool2'))
print("env1['Site_TestTool3'] =", env1.get('Site_TestTool3'))

# Test where toolpath is set in the env constructor
env2 = Environment(tools=['subdir1.Toolpath_TestTool1', 'subdir1.subdir2.Toolpath_TestTool2', 'subdir1.Toolpath_TestTool3'], toolpath=['tools'])
print("env2['Toolpath_TestTool1'] =", env2.get('Toolpath_TestTool1'))
print("env2['Toolpath_TestTool2'] =", env2.get('Toolpath_TestTool2'))
print("env2['Toolpath_TestTool3'] =", env2.get('Toolpath_TestTool3'))

base = Environment(tools=[], toolpath=['tools'])
derived = base.Clone(tools=['subdir1.Toolpath_TestTool1'])
print("derived['Toolpath_TestTool1'] =", derived.get('Toolpath_TestTool1'))
""")


# Test where tools are located under site_scons/site_tools
test.subdir('site_scons', ['site_scons', 'site_tools'])

# One level down - site_scons/site_tools
test.subdir(['site_scons', 'site_tools', 'subdir1'])
test.write(['site_scons', 'site_tools', 'subdir1', '__init__.py'], '')
test.write(['site_scons', 'site_tools', 'subdir1', 'Site_TestTool1.py'], r"""\
def generate(env):
    env['Site_TestTool1'] = 1
def exists(env):
    return 1
""")

# Two levels down - site_scons/site_tools
test.subdir(['site_scons', 'site_tools', 'subdir1', 'subdir2'])
test.write(['site_scons', 'site_tools', 'subdir1', 'subdir2', '__init__.py'], '')
test.write(['site_scons', 'site_tools', 'subdir1', 'subdir2', 'Site_TestTool2.py'], r"""\
def generate(env):
    env['Site_TestTool2'] = 1
def exists(env):
    return 1
""")

# Two levels down - site_scons/site_tools - using __init__.py within a directory
test.subdir(['site_scons', 'site_tools', 'subdir1', 'Site_TestTool3'])
test.write(['site_scons', 'site_tools', 'subdir1', 'Site_TestTool3', '__init__.py'], r"""\
def generate(env):
    env['Site_TestTool3'] = 1
def exists(env):
    return 1
""")


# Test where toolpath is set in the env constructor
test.subdir('tools')

# One level down - tools
test.subdir(['tools', 'subdir1'])
test.write(['tools', 'subdir1', '__init__.py'], '')
test.write(['tools', 'subdir1', 'Toolpath_TestTool1.py'], r"""\
def generate(env):
    env['Toolpath_TestTool1'] = 1
def exists(env):
    return 1
""")

# Two levels down - tools
test.subdir(['tools', 'subdir1', 'subdir2'])
test.write(['tools', 'subdir1', 'subdir2', '__init__.py'], '')
test.write(['tools', 'subdir1', 'subdir2', 'Toolpath_TestTool2.py'], r"""\
def generate(env):
    env['Toolpath_TestTool2'] = 1
def exists(env):
    return 1
""")

# Two levels down - tools - using __init__.py within a directory
test.subdir(['tools', 'subdir1', 'Toolpath_TestTool3'])
test.write(['tools', 'subdir1', 'Toolpath_TestTool3', '__init__.py'], r"""\
def generate(env):
    env['Toolpath_TestTool3'] = 1
def exists(env):
    return 1
""")



test.run(arguments = '.', stdout = """\
scons: Reading SConscript files ...
env1['Site_TestTool1'] = 1
env1['Site_TestTool2'] = 1
env1['Site_TestTool3'] = 1
env2['Toolpath_TestTool1'] = 1
env2['Toolpath_TestTool2'] = 1
env2['Toolpath_TestTool3'] = 1
derived['Toolpath_TestTool1'] = 1
scons: done reading SConscript files.
scons: Building targets ...
scons: `.' is up to date.
scons: done building targets.
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
