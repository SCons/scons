#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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
import sys
import os.path
import os
import TestCmd
import time

test = TestSCons.TestSCons(match = TestCmd.match_re)

if sys.platform != 'win32':
    test.pass_test()

#####
# Test the basics

test.write('SConstruct',"""
env=Environment()
env['PCH'] = env.PCH('StdAfx.cpp')[0]
env['PDB'] = File('test.pdb')
env['PCHSTOP'] = 'StdAfx.h'
env.Program('test', 'test.cpp')

env.Object('fast', 'foo.cpp')
env.Object('slow', 'foo.cpp', PCH=0)
""")

test.write('test.cpp', '''
#include "StdAfx.h"

int main(void) 
{ 
    return 1;
}
''')

test.write('foo.cpp', '''
#include "StdAfx.h"
''')

test.write('StdAfx.h', '''
#include <windows.h>
''')

test.write('StdAfx.cpp', '''
#include "StdAfx.h"
''')

test.run(arguments='test.exe')

test.fail_test(not os.path.exists(test.workpath('test.pdb')))
test.fail_test(not os.path.exists(test.workpath('StdAfx.pch')))
test.fail_test(not os.path.exists(test.workpath('StdAfx.obj')))

test.run(arguments='-c .')

test.fail_test(os.path.exists(test.workpath('test.pdb')))
test.fail_test(os.path.exists(test.workpath('StdAfx.pch')))
test.fail_test(os.path.exists(test.workpath('StdAfx.obj')))

test.run(arguments='test.exe')

test.fail_test(not os.path.exists(test.workpath('test.pdb')))
test.fail_test(not os.path.exists(test.workpath('StdAfx.pch')))
test.fail_test(not os.path.exists(test.workpath('StdAfx.obj')))

test.run(arguments='-c test.pdb')
test.fail_test(os.path.exists(test.workpath('test.exe')))
test.fail_test(os.path.exists(test.workpath('test.obj')))
test.fail_test(os.path.exists(test.workpath('test.pdb')))
test.fail_test(os.path.exists(test.workpath('StdAfx.pch')))
test.fail_test(os.path.exists(test.workpath('StdAfx.obj')))

test.run(arguments='StdAfx.pch')

test.fail_test(not os.path.exists(test.workpath('test.pdb')))
test.fail_test(not os.path.exists(test.workpath('StdAfx.pch')))
test.fail_test(not os.path.exists(test.workpath('StdAfx.obj')))

start = time.time()
test.run(arguments='fast.obj')
fast = time.time() - start

start = time.time()
test.run(arguments='slow.obj')
slow = time.time() - start

# using precompiled headers should be significantly faster
assert fast < slow*0.75


##########
# Test a hierarchical build

test.subdir('src', 'build', 'out')

test.write('SConstruct',"""
BuildDir('build', 'src', duplicate=0)
SConscript('build/SConscript')
""")

test.write('src/SConscript',"""
env=Environment()
env['PCH'] = env.PCH('StdAfx.cpp')[0]
env['PDB'] = File('#out/test.pdb')
env['PCHSTOP'] = 'StdAfx.h'
env.Program('#out/test.exe', 'test.cpp')
""")

test.write('src/test.cpp', '''
#include "StdAfx.h"

int main(void) 
{ 
    return 1;
}
''')

test.write('src/StdAfx.h', '''
#include <windows.h>
''')

test.write('src/StdAfx.cpp', '''
#include "StdAfx.h"
''')

test.run(arguments='out')

test.fail_test(not os.path.exists(test.workpath('out/test.pdb')))
test.fail_test(not os.path.exists(test.workpath('build/StdAfx.pch')))
test.fail_test(not os.path.exists(test.workpath('build/StdAfx.obj')))

test.run(arguments='-c out')

test.fail_test(os.path.exists(test.workpath('out/test.pdb')))
test.fail_test(os.path.exists(test.workpath('build/StdAfx.pch')))
test.fail_test(os.path.exists(test.workpath('build/StdAfx.obj'))) 

#####
# Test error reporting

test.write('SConstruct',"""
env=Environment()
env['PCH'] = env.PCH('StdAfx.cpp')
env['PDB'] = File('test.pdb')
env['PCHSTOP'] = 'StdAfx.h'
env.Program('test', 'test.cpp')
""")

test.run(status=2, stderr=r'''
SCons error: The PCH construction variable must be a File instance: .+
File "SConstruct", line 6, in \?
''')

test.write('SConstruct',"""
env=Environment()
env['PCH'] = env.PCH('StdAfx.cpp')[0]
env['PDB'] = 'test.pdb'
env['PCHSTOP'] = 'StdAfx.h'
env.Program('test', 'test.cpp')
""")

test.run(status=2, stderr='''
SCons error: The PDB construction variable must be a File instance: test.pdb
File "SConstruct", line 6, in \?
''')

test.write('SConstruct',"""
env=Environment()
env['PCH'] = env.PCH('StdAfx.cpp')[0]
env['PDB'] = File('test.pdb')
env.Program('test', 'test.cpp')
""")

test.run(status=2, stderr='''
SCons error: The PCHSTOP construction must be defined if PCH is defined.
File "SConstruct", line 5, in \?
''')

test.write('SConstruct',"""
env=Environment()
env['PCH'] = env.PCH('StdAfx.cpp')[0]
env['PDB'] = File('test.pdb')
env['PCHSTOP'] = File('StdAfx.h')
env.Program('test', 'test.cpp')
""")

test.run(status=2, stderr='''
SCons error: The PCHSTOP construction variable must be a string: .+
File "SConstruct", line 6, in \?
''')

test.pass_test()





