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
# Test error reporting
"""


import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

test.skip_if_not_msvc()

SConstruct_path = test.workpath('SConstruct')

test.write(SConstruct_path, """\
env = Environment()
env['PDB'] = File('test.pdb')
env['PCH'] = env.PCH('StdAfx.cpp')[0]
if int(ARGUMENTS.get('SET_PCHSTOP')):
    env['PCHSTOP'] = File('StdAfx.h')
env.Program('test', 'test.cpp')
""")



expect_stderr = r'''
scons: \*\*\* The PCHSTOP construction must be defined if PCH is defined.
''' + TestSCons.file_expr

test.run(arguments='SET_PCHSTOP=0', status=2, stderr=expect_stderr)



expect_stderr = r'''
scons: \*\*\* The PCHSTOP construction variable must be a string: .+
''' + TestSCons.file_expr

test.run(arguments='SET_PCHSTOP=1', status=2, stderr=expect_stderr)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
