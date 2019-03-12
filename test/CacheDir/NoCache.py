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
Verify that the NoCache environment method works.
"""

import TestSCons, os.path

test = TestSCons.TestSCons()

test.subdir('cache', 'alpha', 'beta')

sconstruct = """
DefaultEnvironment(tools=[])
import os
CacheDir(r'%s')


# This is bad form, but the easiest way to produce a test case.
# Obviously, this could be cached if the inputs were passed in a
# reasonable fashion.
g = '%s'

def ActionWithUndeclaredInputs(target,source,env):
    with open(target[0].get_abspath(),'w') as f:
        f.write(g)

Command('foo_cached', [], ActionWithUndeclaredInputs)
NoCache(Command('foo_notcached', [], ActionWithUndeclaredInputs))
Command('bar_cached', [], ActionWithUndeclaredInputs)
Command('bar_notcached', [], ActionWithUndeclaredInputs)
NoCache('bar_notcached')

# Make sure NoCache doesn't vomit when applied to a Dir
NoCache(Command(Dir('aoeu'), [], Mkdir('$TARGET')))
"""

test.write('alpha/SConstruct', sconstruct % (test.workpath('cache'), 'alpha'))

test.write('beta/SConstruct', sconstruct % (test.workpath('cache'), 'beta'))

# First build, would populate the cache without NoCache
test.run(chdir = 'alpha', arguments = '.')

# Second build, without NoCache there would be a cache hit
test.run(chdir = 'beta', arguments = '.')

test.must_match(['beta','foo_cached'],      'alpha')
test.must_match(['beta','foo_notcached'],   'beta')
test.must_match(['beta','bar_cached'],      'alpha')
test.must_match(['beta','bar_notcached'],   'beta')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
