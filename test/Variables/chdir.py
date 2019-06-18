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
Verify that we can chdir() to the directory in which an Variables
file lives by using the __name__ value.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('bin', 'subdir')

test.write('SConstruct', """\
opts = Variables('../bin/opts.cfg', ARGUMENTS)
opts.Add('VARIABLE')
Export("opts")
SConscript('subdir/SConscript')
""")

SConscript_contents = """\
Import("opts")
env = Environment()
opts.Update(env)
print("VARIABLE = "+repr(env['VARIABLE']))
"""

test.write(['bin', 'opts.cfg'], """\
import os
os.chdir(os.path.split(__name__)[0])
with open('opts2.cfg', 'r') as f:
    contents = f.read()
exec(contents)
""")

test.write(['bin', 'opts2.cfg'], """\
VARIABLE = 'opts2.cfg value'
""")

test.write(['subdir', 'SConscript'], SConscript_contents)

expect = """\
VARIABLE = 'opts2.cfg value'
"""

test.run(arguments = '-q -Q .', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
