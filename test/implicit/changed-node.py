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
Verify that we don't throw an exception if a stored implicit
dependency has changed
"""

import TestSCons

test = TestSCons.TestSCons()


test.subdir('d',
            ['d', '1'],
            ['d', '2'],
            ['d', '3'])

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
SetOption('implicit_cache', 1)
SetOption('max_drift', 1)

def lister(target, source, env):
    import os
    with open(str(target[0]), 'w') as ofp:
        s = str(source[0])
        if os.path.isdir(s):
            for l in os.listdir(str(source[0])):
                ofp.write(l + '\\n')
        else:
            ofp.write(s + '\\n')

builder = Builder(action=lister,
                  source_factory=Dir,
                  source_scanner=DirScanner)
env = Environment(tools=[])
env['BUILDERS']['builder'] = builder
env.builder('d/xfactor', 'd/1')
env.builder('a', 'd')
""")

test.write(['d', '1', 'x'], "d/1/x\n")
test.write(['d', '1', 'y'], "d/1/y\n")
test.write(['d', '1', 'z'], "d/1/z\n")
test.write(['d', '2', 'x'], "d/2/x\n")
test.write(['d', '2', 'y'], "d/2/y\n")
test.write(['d', '2', 'z'], "d/2/x\n")
test.write(['d', '3', 'x'], "d/3/x\n")
test.write(['d', '3', 'y'], "d/3/y\n")
test.write(['d', '3', 'z'], "d/3/z\n")

test.run('--debug=stacktrace')


test.write('SConstruct', """\
SetOption('implicit_cache', 1)
SetOption('max_drift', 1)

def lister(target, source, env):
    import os.path
    with open(str(target[0]), 'w') as ofp:
        s = str(source[0])
        if os.path.isdir(s):
            for l in os.listdir(str(source[0])):
                ofp.write(l + '\\n')
        else:
            ofp.write(s + '\\n')

builder = Builder(action=lister,
                  source_factory=File)
env = Environment(tools=[])
env['BUILDERS']['builder'] = builder

env.builder('a', 'SConstruct')
""")

test.run('--debug=stacktrace')

test.pass_test()


#from os import system, rmdir, remove, mkdir, listdir
#from os.path import exists, isdir
#import sys
#
#
#def setfile(f, content):
#    with open(f, 'w') as ofp:
#        ofp.write(content)
#
#def checkfile(f, content):
#    with open(f) as fp:
#        assert fp.read().strip() == content
#
#def rm(f):
#    if exists(f):
#        if isdir(f):
#            for name in listdir(f):
#                rm(f+'/'+name)
#            rmdir(f)
#        else: remove(f)
#def clean(full=0):
#    for f in ('d','b','a','SConstruct'):
#        rm(f)
#    if full:
#        for f in ('.sconsign.dblite', 'build.py'):
#            rm(f)
#
#clean(1)
#
#clean(1)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
