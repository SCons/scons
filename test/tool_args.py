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
Test the ability to pass a dictionary of keyword arguments to
a Tool specification's generate() method.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
# Test passing kw args to Tool constructor
env1 = Environment(tools=[Tool('FooTool', toolpath=['.'], kw1='kw1val')])
print("env1['TOOL_FOO'] = "+str(env1.get('TOOL_FOO')))
print("env1['kw1'] = "+env1.get('kw1'))

# Test apply_tools taking a list of (name, kwargs_dict)
env2 = Environment(tools=[('FooTool', {'kw2':'kw2val'})], toolpath=['.'])
print("env2['TOOL_FOO'] = "+str(env2.get('TOOL_FOO')))
print("env2['kw2'] = "+env2.get('kw2'))

""")

test.write('FooTool.py', r"""\
def generate(env, **kw):
    for k in kw.keys():
        env[k] = kw[k]
    env['TOOL_FOO'] = 1
def exists(env):
    return 1
""")

test.run(arguments = '.', stdout = """\
scons: Reading SConscript files ...
env1['TOOL_FOO'] = 1
env1['kw1'] = kw1val
env2['TOOL_FOO'] = 1
env2['kw2'] = kw2val
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
