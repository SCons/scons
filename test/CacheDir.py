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
Test retrieving derived files from a CacheDir.
"""

import os.path
import shutil

import TestSCons

test = TestSCons.TestSCons()

# cache2 omitted from list in order to test automatic creation of CacheDir
# directory.
test.subdir('cache1', 'cache3', 'src', 'subdir')

test.write(['src', 'SConstruct'], """\
CacheDir(r'%s')
SConscript('SConscript')
""" % test.workpath('cache1'))

test.write(['src', 'SConscript'], """\
def cat(env, source, target):
    target = str(target[0])
    open('cat.out', 'ab').write(target + "\\n")
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
""")

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")

#############################################################################
# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run(chdir = 'src', arguments = '.')

test.must_match(['src', 'all'], "aaa.in\nbbb.in\nccc.in\n")
test.must_match(['src', 'cat.out'], "aaa.out\nbbb.out\nccc.out\nall\n")

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')
test.unlink(['src', 'cat.out'])

# Verify that we now retrieve the derived files from cache,
# not rebuild them.  Then clean up.
test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""))

test.must_not_exist(test.workpath('src', 'cat.out'))

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')

# Verify that rebuilding with -n reports that everything was retrieved
# from the cache, but that nothing really was.
test.run(chdir = 'src', arguments = '-n .', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""))

test.must_not_exist(test.workpath('src', 'aaa.out'))
test.must_not_exist(test.workpath('src', 'bbb.out'))
test.must_not_exist(test.workpath('src', 'ccc.out'))
test.must_not_exist(test.workpath('src', 'all'))

# Verify that rebuilding with -s retrieves everything from the cache
# even though it doesn't report anything.
test.run(chdir = 'src', arguments = '-s .', stdout = "")

test.must_match(['src', 'all'], "aaa.in\nbbb.in\nccc.in\n")
test.must_not_exist(test.workpath('src', 'cat.out'))

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')

# Verify that updating one input file builds its derived file and
# dependency but that the other files are retrieved from cache.
test.write(['src', 'bbb.in'], "bbb.in 2\n")

test.run(chdir = 'src', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
cat(["bbb.out"], ["bbb.in"])
Retrieved `ccc.out' from cache
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
"""))

test.must_match(['src', 'all'], "aaa.in\nbbb.in 2\nccc.in\n")
test.must_match(['src', 'cat.out'], "bbb.out\nall\n")

test.up_to_date(chdir = 'src', arguments = '.')

#############################################################################
# Now we try out BuildDir() functionality.
# This is largely cut-and-paste of the above,
# with appropriate directory modifications.

build_aaa_out = os.path.join('build', 'aaa.out')
build_bbb_out = os.path.join('build', 'bbb.out')
build_ccc_out = os.path.join('build', 'ccc.out')
build_all = os.path.join('build', 'all')

# First, clean up the source directory and start over with fresh files.
test.run(chdir = 'src', arguments = '-c .')

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")

#
test.write('SConstruct', """\
env = Environment(TWO = '2')
env.CacheDir(r'%s')
BuildDir('build', 'src', duplicate=0)
SConscript('build/SConscript')
""" % test.workpath('cache${TWO}'))

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run()

test.must_match(['build', 'all'], "aaa.in\nbbb.in\nccc.in\n")
test.must_match('cat.out', "%s\n%s\n%s\n%s\n" % (build_aaa_out, build_bbb_out, build_ccc_out, build_all))

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

test.must_not_exist(test.workpath('cat.out'))

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

test.must_match(['build', 'all'], "aaa.in\nbbb.in\nccc.in\n")
test.must_not_exist(test.workpath('cat.out'))

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

test.must_match(['build', 'all'], "aaa.in\nbbb.in 2\nccc.in\n")
test.must_match('cat.out', "%s\n%s\n" % (build_bbb_out, build_all))

test.up_to_date(arguments = '.')

#############################################################################
# Test the case (reported by Jeff Petkau, bug #694744) where a target
# is source for another target with a scanner, which used to cause us
# to push the file to the CacheDir after the build signature had already
# been cleared (as a sign that the built file should now be rescanned).

test.write(['subdir', 'SConstruct'], """\
import SCons

CacheDir(r'%s')

def docopy(target,source,env):
    data = source[0].get_contents()
    f = open(target[0].rfile().get_abspath(), "wb")
    f.write(data)
    f.close()

def sillyScanner(node, env, dirs):
    print 'This is never called (unless we build file.out)'
    return []

SillyScanner = SCons.Scanner.Base(function = sillyScanner, skeys = ['.res'])

env = Environment(tools=[],
                  SCANNERS = [SillyScanner],
                  BUILDERS = {})

r = env.Command('file.res', 'file.ma', docopy)

env.Command('file.out', r, docopy)

# make r the default. Note that we don't even try to build file.out,
# and so SillyScanner never runs. The bug is the same if we build
# file.out, though.
Default(r)
""" % test.workpath('cache3'))

test.write(['subdir', 'file.ma'], "subdir/file.ma\n")

test.run(chdir = 'subdir')

test.must_not_exist(test.workpath('cache3', 'N', 'None'))

#############################################################################
# Test that multiple target files get retrieved from cache correctly.

test.subdir('multiple', 'cache4')

test.write(['multiple', 'SConstruct'], """\
def touch(env, source, target):
    open('foo', 'w').write("")
    open('bar', 'w').write("")
CacheDir(r'%s')
env = Environment()
env.Command(['foo', 'bar'], ['input'], touch)
""" % (test.workpath('cache4')))

test.write(['multiple', 'input'], "multiple/input\n")

test.run(chdir = 'multiple')

test.must_exist(test.workpath('multiple', 'foo'))
test.must_exist(test.workpath('multiple', 'bar'))

test.run(chdir = 'multiple', arguments = '-c')

test.must_not_exist(test.workpath('multiple', 'foo'))
test.must_not_exist(test.workpath('multiple', 'bar'))

test.run(chdir = 'multiple')

test.must_exist(test.workpath('multiple', 'foo'))
test.must_exist(test.workpath('multiple', 'bar'))

# All done.
test.pass_test()
