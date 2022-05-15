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

"""
Verify basic invocation of Microsoft Visual C/C++, including use
of a precompiled header with the $CCFLAGS variable.
"""


import time

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

test.skip_if_not_msvc()

test.dir_fixture('msvc_fixture')

#####
# Test the basics

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


start = time.perf_counter()
test.run(arguments='fast.obj', stderr=None)
fast = time.perf_counter() - start

start = time.perf_counter()
test.run(arguments='slow.obj', stderr=None)
slow = time.perf_counter() - start


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
