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
Verify that whether or not a target gets retrieved from a CacheDir
is configurable by construction environment.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

cache = test.workpath('cache')

src_aaa_out = test.workpath('src', 'aaa.out')
src_bbb_out = test.workpath('src', 'bbb.out')
src_ccc_out = test.workpath('src', 'ccc.out')
src_cat_out = test.workpath('src', 'cat.out')
src_all = test.workpath('src', 'all')

test.subdir('cache', 'src')

test.write(['src', 'SConstruct'], """\
DefaultEnvironment(tools=[])
CacheDir(r'%(cache)s')
SConscript('SConscript')
""" % locals())

test.write(['src', 'SConscript'], """\
def cat(env, source, target):
    target = str(target[0])
    with open('cat.out', 'a') as f:
        f.write(target + "\\n")
    with open(target, "w") as f:
        for src in source:
            with open(str(src), "r") as f2:
                f.write(f2.read())
env_cache = Environment(tools=[], BUILDERS={'Cat':Builder(action=cat)})
env_nocache = env_cache.Clone()
env_nocache.CacheDir(None)
env_cache.Cat('aaa.out', 'aaa.in')
env_nocache.Cat('bbb.out', 'bbb.in')
env_cache.Cat('ccc.out', 'ccc.in')
env_nocache.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
""")

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")

# Verify that building with -n and an empty cache reports that proper
# build operations would be taken, but that nothing is actually built
# and that the cache is still empty.
test.run(chdir = 'src', arguments = '-n .', stdout = test.wrap_stdout("""\
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
"""))

test.must_not_exist(src_aaa_out)
test.must_not_exist(src_bbb_out)
test.must_not_exist(src_ccc_out)
test.must_not_exist(src_all)
# Even if you do -n, the cache will be configured.
test.fail_test(os.listdir(cache) != ['config'])

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run(chdir = 'src', arguments = '.')

test.must_match(['src', 'all'], "aaa.in\nbbb.in\nccc.in\n", mode='r')
test.must_match(src_cat_out, "aaa.out\nbbb.out\nccc.out\nall\n", mode='r')

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')
test.unlink(src_cat_out)

# Verify that we now retrieve the derived files from cache,
# not rebuild them.  Then clean up.
test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
cat(["bbb.out"], ["bbb.in"])
Retrieved `ccc.out' from cache
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
"""))

test.must_match(src_cat_out, "bbb.out\nall\n", mode='r')

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')
test.unlink(src_cat_out)

# Verify that rebuilding with -n reports that files were retrieved
# from the cache, but that nothing really was.
test.run(chdir = 'src', arguments = '-n .', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
cat(["bbb.out"], ["bbb.in"])
Retrieved `ccc.out' from cache
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
"""))

test.must_not_exist(src_aaa_out)
test.must_not_exist(src_bbb_out)
test.must_not_exist(src_ccc_out)
test.must_not_exist(src_all)

# Verify that rebuilding with -s retrieves everything from the cache
# even though it doesn't report anything.
test.run(chdir = 'src', arguments = '-s .', stdout = "")

test.must_match(['src', 'all'], "aaa.in\nbbb.in\nccc.in\n", mode='r')

test.must_match(src_cat_out, "bbb.out\nall\n", mode='r')

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')
test.unlink(src_cat_out)

# Verify that updating one input file builds its derived file and
# dependency but that the other files are retrieved from cache.
test.write(['src', 'bbb.in'], "bbb.in 2\n")

test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
cat(["bbb.out"], ["bbb.in"])
Retrieved `ccc.out' from cache
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
"""))

test.must_match(['src', 'all'], "aaa.in\nbbb.in 2\nccc.in\n", mode='r')
test.must_match(src_cat_out, "bbb.out\nall\n", mode='r')

test.up_to_date(chdir = 'src', arguments = '.')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
