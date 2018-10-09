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
Verify that targets retrieved from CacheDir() are reported as
up-to-date by the -q option.

Thanks to dvitek for the test case.
"""

# Demonstrate a regression between 0.96.1 and 0.96.93.
#
# SCons would incorrectly believe files are stale if they were retrieved
# from the cache in a previous invocation.
#
# What this script does:
# 1. Set up two identical C project directories called 'alpha' and
#    'beta', which use the same cache
# 2. Invoke scons on 'alpha'
# 3. Invoke scons on 'beta', which successfully draws output 
#    files from the cache
# 4. Invoke scons again, asserting (with -q) that 'beta' is up to date
#
# Step 4 failed in 0.96.93.  In practice, this problem would lead to
# lots of unecessary fetches from the cache during incremental 
# builds (because they behaved like non-incremental builds).

import TestSCons

test = TestSCons.TestSCons()

test.subdir('cache', 'alpha', 'beta')

foo_c = """
int main(void){ return 0; }
"""

sconstruct = """
CacheDir(r'%s')
Program('foo', 'foo.c')
""" % test.workpath('cache')

test.write('alpha/foo.c', foo_c)
test.write('alpha/SConstruct', sconstruct)

test.write('beta/foo.c', foo_c)
test.write('beta/SConstruct', sconstruct)

# First build, populates the cache
test.run(chdir = 'alpha', arguments = '.')

# Second build, everything is a cache hit
test.run(chdir = 'beta', arguments = '.')

# Since we just built 'beta', it ought to be up to date.
test.run(chdir = 'beta', arguments = '. -q')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
