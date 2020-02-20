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
Verify basic invocation of Microsoft Visual C/C++, including use
of a precompiled header with the $CCFLAGS variable.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import time

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

test.skip_if_not_msvc()

#####
# Test the basics

test.write('SConstruct',"""
import os
DefaultEnvironment(tools=[])
# TODO:  this is order-dependent (putting 'mssdk' second or third breaks),
# and ideally we shouldn't need to specify the tools= list anyway.
env = Environment(tools=['mssdk', 'msvc', 'mslink'])
env.Append(CPPPATH=os.environ.get('INCLUDE', ''),
           LIBPATH=os.environ.get('LIB', ''),
           CCFLAGS='/DPCHDEF')
env['PDB'] = File('test.pdb')
env['PCHSTOP'] = 'StdAfx.h'
env['PCH'] = env.PCH('StdAfx.cpp')[0]
env.Program('test', ['test.cpp', env.RES('test.rc')], LIBS=['user32'])

env.Object('fast', 'foo.cpp')
env.Object('slow', 'foo.cpp', PCH=0)
""")

test.write('test.cpp', '''
#include "StdAfx.h"
#include "resource.h"

int main(void) 
{ 
    char test[1024];
    LoadString(GetModuleHandle(NULL), IDS_TEST, test, sizeof(test));
    printf("%d %s\\n", IDS_TEST, test);
    return 0;
}
''')

test.write('test.rc', '''
#include "resource.h"

STRINGTABLE DISCARDABLE 
BEGIN
    IDS_TEST "test 1"
END
''')

test.write('resource.h', '''
#define IDS_TEST 2001
''')


test.write('foo.cpp', '''
#include "StdAfx.h"
''')

test.write('StdAfx.h', '''
#include <windows.h>
#include <stdio.h>
#include "resource.h"
''')

test.write('StdAfx.cpp', '''
#include "StdAfx.h"
#ifndef PCHDEF
this line generates an error if PCHDEF is not defined!
#endif
''')

#  Visual Studio 8 has deprecated the /Yd option and prints warnings
#  about it, so ignore stderr when running SCons.

test.run(arguments='test.exe', stderr=None)

test.must_exist(test.workpath('test.exe'))
test.must_exist(test.workpath('test.res'))
test.must_exist(test.workpath('test.pdb'))
test.must_exist(test.workpath('StdAfx.pch'))
test.must_exist(test.workpath('StdAfx.obj'))

test.run(program=test.workpath('test.exe'), stdout='2001 test 1\n')

test.write('resource.h', '''
#define IDS_TEST 2002
''')
test.run(arguments='test.exe', stderr=None)
test.run(program=test.workpath('test.exe'), stdout='2002 test 1\n')

test.write('test.rc', '''
#include "resource.h"

STRINGTABLE DISCARDABLE 
BEGIN
    IDS_TEST "test 2"
END
''')
test.run(arguments='test.exe', stderr=None)
test.run(program=test.workpath('test.exe'), stdout='2002 test 2\n')

test.run(arguments='-c .')

test.must_not_exist(test.workpath('test.exe'))
test.must_not_exist(test.workpath('test.pdb'))
test.must_not_exist(test.workpath('test.res'))
test.must_not_exist(test.workpath('StdAfx.pch'))
test.must_not_exist(test.workpath('StdAfx.obj'))

test.run(arguments='test.exe', stderr=None)

test.must_exist(test.workpath('test.pdb'))
test.must_exist(test.workpath('StdAfx.pch'))
test.must_exist(test.workpath('StdAfx.obj'))

test.run(arguments='-c test.pdb')
test.must_not_exist(test.workpath('test.exe'))
test.must_not_exist(test.workpath('test.obj'))
test.must_not_exist(test.workpath('test.pdb'))
test.must_not_exist(test.workpath('StdAfx.pch'))
test.must_not_exist(test.workpath('StdAfx.obj'))

test.run(arguments='StdAfx.pch', stderr=None)

test.must_not_exist(test.workpath('test.pdb'))
test.must_exist(test.workpath('StdAfx.pch'))
test.must_exist(test.workpath('StdAfx.obj'))

test.run(arguments='-c test.exe')
test.must_not_exist(test.workpath('test.exe'))
test.must_not_exist(test.workpath('test.obj'))
test.must_not_exist(test.workpath('test.pdb'))
test.must_not_exist(test.workpath('StdAfx.pch'))
test.must_not_exist(test.workpath('StdAfx.obj'))

test.run(arguments='test.obj', stderr=None)
test.must_not_exist(test.workpath('test.pdb'))
test.must_exist(test.workpath('test.obj'))


start = time.time()
test.run(arguments='fast.obj', stderr=None)
fast = time.time() - start

start = time.time()
test.run(arguments='slow.obj', stderr=None)
slow = time.time() - start


# TODO: Reevaluate if having this part of the test makes sense any longer
# using precompiled headers should be faster
limit = slow*0.90
if fast >= limit:
    print("Using precompiled headers was not fast enough:")
    print("slow.obj:  %.3fs" % slow)
    print("fast.obj:  %.3fs (expected less than %.3fs)" % (fast, limit))
    test.fail_test()

# Modifying resource.h should cause both the resource and precompiled header to be rebuilt:
test.write('resource.h', '''
#define IDS_TEST 2003
''')

test.not_up_to_date(arguments='test.res', stderr=None)
test.not_up_to_date(arguments='StdAfx.pch', stderr=None)
test.not_up_to_date(arguments='test.exe', stderr=None)
test.run(program=test.workpath('test.exe'), stdout='2003 test 2\n')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
