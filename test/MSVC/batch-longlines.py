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
Verify operation of Visual C/C++ batch builds with long lines.

Only runs on Windows.
"""

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

_python_ = TestSCons._python_

for i in range(1,200):
    test.write('source-file-with-quite-a-long-name-maybe-unrealistic-but-who-cares-%05d.cxx'%i,
               '/* source file %d */\nint var%d;\n'%(i,i))

test.write('SConstruct', """
env = Environment(tools=['msvc', 'mslink'],
                  MSVC_BATCH=ARGUMENTS.get('MSVC_BATCH'))
env.SharedLibrary('mylib', Glob('source*.cxx'))
""" % locals())

test.run(arguments = 'MSVC_BATCH=1 .')

test.must_exist('mylib.dll')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
