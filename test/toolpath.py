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
import sys
import time
import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def foo(env):
    env['TOOL_FOO'] = 1
    
env1 = Environment(tools=[foo, 'bar'], toolpath=['tools'])
print "env1['TOOL_FOO'] =", env1.get('TOOL_FOO')
print "env1['TOOL_BAR'] =", env1.get('TOOL_BAR')

# pick a built-in tool with pretty simple behavior
env2 = Environment(tools=['SCCS'])
print "env2['SCCS'] =", env2.get('SCCS')
print "env2['TOOL_SCCS1'] =", env2.get('TOOL_SCCS1')
print "env2['TOOL_SCCS2'] =", env2.get('TOOL_SCCS2')

env3 = Environment(tools=['SCCS'], toolpath=['.'])
print "env3['SCCS'] =", env3.get('SCCS')
print "env3['TOOL_SCCS1'] =", env3.get('TOOL_SCCS1')
print "env3['TOOL_SCCS2'] =", env3.get('TOOL_SCCS2')

env4 = Environment(tools=['SCCS'], toolpath=['tools'])
print "env4['SCCS'] =", env4.get('SCCS')
print "env4['TOOL_SCCS1'] =", env4.get('TOOL_SCCS1')
print "env4['TOOL_SCCS2'] =", env4.get('TOOL_SCCS2')

env5 = Environment(tools=['SCCS'], toolpath=['tools', '.'])
print "env5['SCCS'] =", env5.get('SCCS')
print "env5['TOOL_SCCS1'] =", env5.get('TOOL_SCCS1')
print "env5['TOOL_SCCS2'] =", env5.get('TOOL_SCCS2')

env6 = Environment(tools=['SCCS'], toolpath=['.', 'tools'])
print "env6['SCCS'] =", env6.get('SCCS')
print "env6['TOOL_SCCS1'] =", env6.get('TOOL_SCCS1')
print "env6['TOOL_SCCS2'] =", env6.get('TOOL_SCCS2')

env7 = Environment(TOOLPATH="tools", tools=['SCCS'], toolpath=['$TOOLPATH'])
print "env7['SCCS'] =", env7.get('SCCS')
print "env7['TOOL_SCCS1'] =", env7.get('TOOL_SCCS1')
print "env7['TOOL_SCCS2'] =", env7.get('TOOL_SCCS2')

env8 = Environment(tools=[])
env8.Tool('SCCS', toolpath=['tools'])
print "env8['SCCS'] =", env8.get('SCCS')
print "env8['TOOL_SCCS1'] =", env8.get('TOOL_SCCS1')
print "env8['TOOL_SCCS2'] =", env8.get('TOOL_SCCS2')

env9 = Environment(tools=[])
Tool('SCCS', toolpath=['tools'])(env9)
print "env9['SCCS'] =", env9.get('SCCS')
print "env9['TOOL_SCCS1'] =", env9.get('TOOL_SCCS1')
print "env9['TOOL_SCCS2'] =", env9.get('TOOL_SCCS2')

env0 = Environment(TOOLPATH='tools', tools=[])
env0.Tool('SCCS', toolpath=['$TOOLPATH'])
print "env0['SCCS'] =", env0.get('SCCS')
print "env0['TOOL_SCCS1'] =", env0.get('TOOL_SCCS1')
print "env0['TOOL_SCCS2'] =", env0.get('TOOL_SCCS2')
""")

test.write('SCCS.py', r"""\
def generate(env):
    env['TOOL_SCCS1'] = 1
def exists(env):
    return 1
""")

test.subdir('tools')

test.write(['tools', 'Common.py'], r"""\
One = 1
""")

test.write(['tools', 'SCCS.py'], r"""\
import Common
def generate(env):
    env['TOOL_SCCS2'] = Common.One
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
env2['SCCS'] = sccs
env2['TOOL_SCCS1'] = None
env2['TOOL_SCCS2'] = None
env3['SCCS'] = None
env3['TOOL_SCCS1'] = 1
env3['TOOL_SCCS2'] = None
env4['SCCS'] = None
env4['TOOL_SCCS1'] = None
env4['TOOL_SCCS2'] = 1
env5['SCCS'] = None
env5['TOOL_SCCS1'] = None
env5['TOOL_SCCS2'] = 1
env6['SCCS'] = None
env6['TOOL_SCCS1'] = 1
env6['TOOL_SCCS2'] = None
env7['SCCS'] = None
env7['TOOL_SCCS1'] = None
env7['TOOL_SCCS2'] = 1
env8['SCCS'] = None
env8['TOOL_SCCS1'] = None
env8['TOOL_SCCS2'] = 1
env9['SCCS'] = None
env9['TOOL_SCCS1'] = None
env9['TOOL_SCCS2'] = 1
env0['SCCS'] = None
env0['TOOL_SCCS1'] = None
env0['TOOL_SCCS2'] = 1
scons: done reading SConscript files.
scons: Building targets ...
scons: `.' is up to date.
scons: done building targets.
""")

test.pass_test()
