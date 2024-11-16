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
Verify that a Variables file in a different directory can import
a module in that directory.
"""

import TestSCons

test = TestSCons.TestSCons()

workpath = test.workpath('')

test.subdir('bin', 'subdir')

test.write('SConstruct', """\
_ = DefaultEnvironment(tools=[])
opts = Variables('../bin/opts.cfg', ARGUMENTS)
opts.Add('VARIABLE')
Export("opts")
SConscript('subdir/SConscript')
""")

SConscript_contents = """\
Import("opts")
env = Environment(tools=[])
opts.Update(env)
print("VARIABLE = %s"%env.get('VARIABLE'))
"""

test.write(['bin', 'opts.cfg'], """\
from local_options import VARIABLE
""")

test.write(['bin', 'local_options.py'], """\
VARIABLE = 'bin/local_options.py'
""")

test.write(['subdir', 'SConscript'], SConscript_contents)

expect = "VARIABLE = bin/local_options.py\n"

test.run(arguments='-q -Q .', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
