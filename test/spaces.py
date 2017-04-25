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
import sys
import os

test = TestSCons.TestSCons()

if sys.platform == 'win32':
    test.write('duplicate a file.bat', 'copy foo.in foo.out\n')
    copy = test.workpath('duplicate a file.bat')
else:
    test.write('duplicate a file.sh', 'cp foo.in foo.out\n')
    copy = test.workpath('duplicate a file.sh')
    os.chmod(test.workpath('duplicate a file.sh'), 0o777)
    

test.write('SConstruct', r'''
env=Environment()
env.Command("foo.out", "foo.in", [[r"%s", "$SOURCE", "$TARGET"]])
'''%copy)

test.write('foo.in', 'foo.in 1 \n')

test.run(arguments='foo.out')

test.write('SConstruct', r'''
env=Environment()
env["COPY"] = File(r"%s")
env["ENV"]
env.Command("foo.out", "foo.in", [["./$COPY", "$SOURCE", "$TARGET"]])
'''%copy)

test.write('foo.in', 'foo.in 2 \n')

test.run(arguments='foo.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
