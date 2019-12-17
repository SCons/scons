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
Test populating a CacheDir with the --cache-force option.
"""

import os.path
import shutil

import TestSCons

test = TestSCons.TestSCons()

test.subdir('cache', 'src')

test.write(['src', 'SConstruct'], """
DefaultEnvironment(tools=[])
def cat(env, source, target):
    target = str(target[0])
    with open('cat.out', 'a') as f:
        f.write(target + "\\n")
    with open(target, "w") as f:
        for src in source:
            with open(str(src), "r") as f2:
                f.write(f2.read())
env = Environment(tools=[], BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
CacheDir(r'%s')
""" % test.workpath('cache'))

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run(chdir = 'src', arguments = '.')

test.must_match(['src','all'],"aaa.in\nbbb.in\nccc.in\n", mode='r')
# test.fail_test(test.read(['src', 'all']) != "aaa.in\nbbb.in\nccc.in\n")
test.must_match(['src','cat.out'],"aaa.out\nbbb.out\nccc.out\nall\n", mode='r')
# test.fail_test(test.read(['src', 'cat.out']) != "aaa.out\nbbb.out\nccc.out\nall\n")

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')
test.unlink(['src', 'cat.out'])

# Verify that we now retrieve the derived files from cache,
# not rebuild them.  DO NOT CLEAN UP.
test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""))

test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

test.up_to_date(chdir = 'src', arguments = '.')

# Blow away and recreate the CacheDir, then verify that --cache-force
# repopulates the cache with the local built targets.  DO NOT CLEAN UP.
shutil.rmtree(test.workpath('cache'))
test.subdir('cache')

test.run(chdir = 'src', arguments = '--cache-force .')

test.run(chdir = 'src', arguments = '-c .')

test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""))

test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

# Blow away and recreate the CacheDir, then verify that --cache-populate
# repopulates the cache with the local built targets.  DO NOT CLEAN UP.
shutil.rmtree(test.workpath('cache'))
test.subdir('cache')

test.run(chdir = 'src', arguments = '--cache-populate .')

test.run(chdir = 'src', arguments = '-c .')

test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""))

test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

# All done.
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
