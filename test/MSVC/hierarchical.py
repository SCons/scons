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
Verify use of Visual Studio with a hierarchical build.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

test.skip_if_not_msvc()

test.subdir('src', 'build', 'out')

test.write('SConstruct', """
VariantDir('build', 'src', duplicate=0)
SConscript('build/SConscript')
""")

test.write('src/SConscript',"""
import os
# TODO:  this is order-dependent (putting 'mssdk' second or third breaks),
# and ideally we shouldn't need to specify the tools= list anyway.
env = Environment(tools=['mssdk', 'msvc', 'mslink'])
env.Append(CPPPATH=os.environ.get('INCLUDE', ''),
           LIBPATH=os.environ.get('LIB', ''))
env['PCH'] = 'StdAfx.pch'
env['PDB'] = '#out/test.pdb'
env['PCHSTOP'] = 'StdAfx.h'
env.PCH('StdAfx.cpp')
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

test.run(arguments='out', stderr=None)

test.must_exist(test.workpath('out/test.pdb'))
test.must_exist(test.workpath('build/StdAfx.pch'))
test.must_exist(test.workpath('build/StdAfx.obj'))

test.run(arguments='-c out')

test.must_not_exist(test.workpath('out/test.pdb'))
test.must_not_exist(test.workpath('build/StdAfx.pch'))
test.must_not_exist(test.workpath('build/StdAfx.obj'))



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
