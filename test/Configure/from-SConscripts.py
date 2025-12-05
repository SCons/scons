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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""
Make sure we can call Configure() from subsidiary SConscript calls.

This was broken at one point when we were using the internal
sconscript_reading flag (which is basically a hint for whether or not
we're in a Builder call) as a semaphore, not a counter.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = SConscript('x.scons')
""")

test.write('x.scons', """\
env = SConscript('y.scons')
config = env.Configure()
env = config.Finish()
Return('env')
""")

test.write('y.scons', """\
env = Environment(tools=[])
Return('env')
""")

test.run(arguments = '.')

test.pass_test()
