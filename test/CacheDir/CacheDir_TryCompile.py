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
Test that CacheDir functions with TryCompile.

With Py3 there was an issue where the generated cache signature from Python Value nodes
could be bytes instead of a string which would fail when combining cache signatures
which ended up a mixture of bytes and strings.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

cache = test.workpath('cache')

test.subdir('cache', 'src')

test.write(['src', 'SConstruct'], """\
DefaultEnvironment(tools=[])
env = Environment()
env.CacheDir(r'%(cache)s')

conf = Configure(env)

conf.TryCompile('int a;', '.c')

env = conf.Finish()
""" % locals())

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run(chdir = 'src', arguments = '.')

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
