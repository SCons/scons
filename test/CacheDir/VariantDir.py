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
Test retrieving derived files from a CacheDir when a VariantDir is used.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('cache', 'src')

cache = test.workpath('cache')
cat_out = test.workpath('cat.out')

test.write(['src', 'SConscript'], """\
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
""")

build_aaa_out = os.path.join('build', 'aaa.out')
build_bbb_out = os.path.join('build', 'bbb.out')
build_ccc_out = os.path.join('build', 'ccc.out')
build_all = os.path.join('build', 'all')

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")

#
test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=[], TWO = '2')
CacheDir(r'%s')
VariantDir('build', 'src', duplicate=0)
SConscript('build/SConscript')
""" % test.workpath('cache${TWO}'))

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run()

test.must_match(['build', 'all'], "aaa.in\nbbb.in\nccc.in\n", mode='r')
test.must_match('cat.out', "%s\n%s\n%s\n%s\n" % (build_aaa_out, build_bbb_out, build_ccc_out, build_all), mode='r')

test.up_to_date(arguments = '.')

test.run(arguments = '-c .')
test.unlink('cat.out')

# Verify that we now retrieve the derived files from cache,
# not rebuild them.  Then clean up.
test.run(stdout = test.wrap_stdout("""\
Retrieved `%s' from cache
Retrieved `%s' from cache
Retrieved `%s' from cache
Retrieved `%s' from cache
""" % (build_aaa_out, build_bbb_out, build_ccc_out, build_all)))

test.must_not_exist(cat_out)

test.up_to_date(arguments = '.')

test.run(arguments = '-c .')

# Verify that rebuilding with -n reports that everything was retrieved
# from the cache, but that nothing really was.
test.run(arguments = '-n .', stdout = test.wrap_stdout("""\
Retrieved `%s' from cache
Retrieved `%s' from cache
Retrieved `%s' from cache
Retrieved `%s' from cache
""" % (build_aaa_out, build_bbb_out, build_ccc_out, build_all)))

test.must_not_exist(test.workpath('build', 'aaa.out'))
test.must_not_exist(test.workpath('build', 'bbb.out'))
test.must_not_exist(test.workpath('build', 'ccc.out'))
test.must_not_exist(test.workpath('build', 'all'))

# Verify that rebuilding with -s retrieves everything from the cache
# even though it doesn't report anything.
test.run(arguments = '-s .', stdout = "")

test.must_match(['build', 'all'], "aaa.in\nbbb.in\nccc.in\n", mode='r')
test.must_not_exist(cat_out)

test.up_to_date(arguments = '.')

test.run(arguments = '-c .')

# Verify that updating one input file builds its derived file and
# dependency but that the other files are retrieved from cache.
test.write(['src', 'bbb.in'], "bbb.in 2\n")

test.run(stdout = test.wrap_stdout("""\
Retrieved `%s' from cache
cat(["%s"], ["%s"])
Retrieved `%s' from cache
cat(["%s"], ["%s", "%s", "%s"])
""" % (build_aaa_out,
       build_bbb_out, os.path.join('src', 'bbb.in'),
       build_ccc_out,
       build_all, build_aaa_out, build_bbb_out, build_ccc_out)))

test.must_match(['build', 'all'], "aaa.in\nbbb.in 2\nccc.in\n", mode='r')
test.must_match('cat.out', "%s\n%s\n" % (build_bbb_out, build_all), mode='r')

test.up_to_date(arguments = '.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
