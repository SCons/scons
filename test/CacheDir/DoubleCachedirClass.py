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
#

"""
Test that cache dir is reinitialized correctly when two cachedirs are in use
and also that the cachedirs are isolated to their own environments.

The core of the test is:
-----------------------------------------
env = Environment(tools=[])
env.CacheDir('cache1', CustomCacheDir1)
env.CacheDir('cache2', CustomCacheDir2)

cloned = env.Clone()
cloned.Command('file.out', 'file.in', Copy('$TARGET', '$SOURCE'))

env.CacheDir('cache1', CustomCacheDir1)
-----------------------------------------

Where each cachedir is printing its own name in an overridden copy_to_cache function, so
since the only command putting something to cache is in the cloned environment, we should
see only cachedir2 print since that was initialized for that env when the clone happened.
"""

import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture('double_cachedir_fixture')

test.run()

test.must_contain_single_instance_of(test.stdout(), ["INSTANCIATED CustomCacheDir2"])
test.must_contain_single_instance_of(test.stdout(), ["MY_CUSTOM_CACHEDIR_CLASS2"])
test.must_not_contain_any_line(test.stdout(), ["MY_CUSTOM_CACHEDIR_CLASS1"])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
