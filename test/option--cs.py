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
Test printing build actions when using the --cache-show option and
retrieving derived files from a CacheDir.
"""

import os.path
import shutil

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('cache', 'src')

test.write(['src', 'build.py'], r"""
import sys
open('cat.out', 'ab').write(sys.argv[1] + "\n")
file = open(sys.argv[1], 'wb')
for src in sys.argv[2:]:
    file.write(open(src, 'rb').read())
file.close()
""")

test.write(['src', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    open('cat.out', 'ab').write(target + "\\n")
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Internal':Builder(action=cat),
                            'External':Builder(action='%s build.py $TARGET $SOURCES')})
env.External('aaa.out', 'aaa.in')
env.External('bbb.out', 'bbb.in')
env.Internal('ccc.out', 'ccc.in')
env.Internal('all', ['aaa.out', 'bbb.out', 'ccc.out'])
CacheDir(r'%s')
""" % (python, test.workpath('cache')))

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run(chdir = 'src', arguments = '.')

test.fail_test(test.read(['src', 'all']) != "aaa.in\nbbb.in\nccc.in\n")

test.fail_test(test.read(['src', 'cat.out']) != "aaa.out\nbbb.out\nccc.out\nall\n")

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

test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')

# Verify that using --cache-show reports the files as being rebuilt,
# even though we actually fetch them from the cache.  Then clean up.
test.run(chdir = 'src',
         arguments = '--cache-show .',
         stdout = test.wrap_stdout("""\
%s build.py aaa.out aaa.in
%s build.py bbb.out bbb.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
""" % (python, python)))

test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

test.up_to_date(chdir = 'src', arguments = '.')

test.run(chdir = 'src', arguments = '-c .')

# Verify that using --cache-show -n reports the files as being rebuilt,
# even though we don't actually fetch them from the cache.  No need to
# clean up.
test.run(chdir = 'src',
         arguments = '--cache-show -n .',
         stdout = test.wrap_stdout("""\
%s build.py aaa.out aaa.in
%s build.py bbb.out bbb.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
""" % (python, python)))

test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

test.fail_test(os.path.exists(test.workpath('src', 'aaa.out')))
test.fail_test(os.path.exists(test.workpath('src', 'bbb.out')))
test.fail_test(os.path.exists(test.workpath('src', 'ccc.out')))
test.fail_test(os.path.exists(test.workpath('src', 'all')))

# Verify that using --cache-show -s doesn't report anything, even though
# we do fetch the files from the cache.  No need to clean up.
test.run(chdir = 'src',
         arguments = '--cache-show -s .',
         stdout = "")

test.fail_test(test.read(['src', 'all']) != "aaa.in\nbbb.in\nccc.in\n")
test.fail_test(os.path.exists(test.workpath('src', 'cat.out')))

# All done.
test.pass_test()
