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


import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def foo(env):
    env['TOOL_FOO'] = 1

env1 = Environment(tools=[foo, 'bar'], toolpath=['tools'])
print("env1['TOOL_FOO'] = %s"%env1.get('TOOL_FOO'))
print("env1['TOOL_BAR'] = %s"%env1.get('TOOL_BAR'))

# pick a built-in tool with pretty simple behavior
env2 = Environment(tools=['zip'])
print("env2['ZIP'] = %s"%env2.get('ZIP'))
print("env2['TOOL_zip1'] = %s"%env2.get('TOOL_zip1'))
print("env2['TOOLDIR_zip'] = %s"%env2.get('TOOLDIR_zip'))

# Only find tools in current dir, or Scons.Tool.TOOLNAME
env3 = Environment(tools=['zip'], toolpath=['.'])
print("env3['ZIP'] = %s"%env3.get('ZIP'))
print("env3['TOOL_zip1'] = %s"%env3.get('TOOL_zip1'))
print("env3['TOOLDIR_zip'] = %s"%env3.get('TOOLDIR_zip'))

env4 = Environment(tools=['zip'], toolpath=['tools'])
print("env4['ZIP'] = %s"%env4.get('ZIP'))
print("env4['TOOL_zip1'] = %s"%env4.get('TOOL_zip1'))
print("env4['TOOLDIR_zip'] = %s"%env4.get('TOOLDIR_zip'))

# Should pick up from tools dir, and then current dir
env5 = Environment(tools=['zip'], toolpath=['tools', '.'])
print("env5['ZIP'] = %s"%env5.get('ZIP'))
print("env5['TOOL_zip1'] = %s"%env5.get('TOOL_zip1'))
print("env5['TOOLDIR_zip'] = %s"%env5.get('TOOLDIR_zip'))


# Should pick up from current dir, and then tools dir
env6 = Environment(tools=['zip'], toolpath=['.', 'tools'])
print("env6['ZIP'] = %s"%env6.get('ZIP'))
print("env6['TOOL_zip1'] = %s"%env6.get('TOOL_zip1'))
print("env6['TOOLDIR_zip'] = %s"%env6.get('TOOLDIR_zip'))

env7 = Environment(TOOLPATH="tools", tools=['zip'], toolpath=['$TOOLPATH'])
print("env7['ZIP'] = %s"%env7.get('ZIP'))
print("env7['TOOL_zip1'] = %s"%env7.get('TOOL_zip1'))
print("env7['TOOLDIR_zip'] = %s"%env7.get('TOOLDIR_zip'))

env8 = Environment(tools=[])
env8.Tool('zip', toolpath=['tools'])
print("env8['ZIP'] = %s"%env8.get('ZIP'))
print("env8['TOOL_zip1'] = %s"%env8.get('TOOL_zip1'))
print("env8['TOOLDIR_zip'] = %s"%env8.get('TOOLDIR_zip'))

env9 = Environment(tools=[])
Tool('zip', toolpath=['tools'])(env9)
print("env9['ZIP'] = %s"%env9.get('ZIP'))
print("env9['TOOL_zip1'] = %s"%env9.get('TOOL_zip1'))
print("env9['TOOLDIR_zip'] = %s"%env9.get('TOOLDIR_zip'))

env0 = Environment(TOOLPATH='tools', tools=[])
env0.Tool('zip', toolpath=['$TOOLPATH'])
print("env0['ZIP'] = %s"%env0.get('ZIP'))
print("env0['TOOL_zip1'] = %s"%env0.get('TOOL_zip1'))
print("env0['TOOLDIR_zip'] = %s"%env0.get('TOOLDIR_zip'))

base = Environment(tools=[], toolpath=['tools'])
derived = base.Clone(tools=['bar'])
print("derived['TOOL_BAR'] = %s"%derived.get('TOOL_BAR'))
""")

test.write('zip.py', r"""
def generate(env):
    env['TOOL_zip1'] = 1
def exists(env):
    return 1
""",mode='w')

test.subdir('tools')

test.write(['tools', 'Common.py'], r"""\
One = 1
""")

test.write(['tools', 'zip.py'], r"""\
import Common
def generate(env):
    env['TOOLDIR_zip'] = Common.One
def exists(env):
    return Common.One
""")

test.write(['tools', 'bar.py'], r"""\
def generate(env):
    env['TOOL_BAR'] = 1
def exists(env):
    return 1
""")

test.run(arguments = '.', stdout = """\
scons: Reading SConscript files ...
env1['TOOL_FOO'] = 1
env1['TOOL_BAR'] = 1
env2['ZIP'] = zip
env2['TOOL_zip1'] = None
env2['TOOLDIR_zip'] = None
env3['ZIP'] = None
env3['TOOL_zip1'] = 1
env3['TOOLDIR_zip'] = None
env4['ZIP'] = None
env4['TOOL_zip1'] = None
env4['TOOLDIR_zip'] = 1
env5['ZIP'] = None
env5['TOOL_zip1'] = None
env5['TOOLDIR_zip'] = 1
env6['ZIP'] = None
env6['TOOL_zip1'] = 1
env6['TOOLDIR_zip'] = None
env7['ZIP'] = None
env7['TOOL_zip1'] = None
env7['TOOLDIR_zip'] = 1
env8['ZIP'] = None
env8['TOOL_zip1'] = None
env8['TOOLDIR_zip'] = 1
env9['ZIP'] = None
env9['TOOL_zip1'] = None
env9['TOOLDIR_zip'] = 1
env0['ZIP'] = None
env0['TOOL_zip1'] = None
env0['TOOLDIR_zip'] = 1
derived['TOOL_BAR'] = 1
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
