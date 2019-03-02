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

_python_ = TestSCons._python_

_exe = TestSCons._exe
_obj = TestSCons._obj

test = TestSCons.TestSCons()

test.subdir('cache', 'src1', 'src2')

test.write(['src1', 'build.py'], r"""
import sys
with open('cat.out', 'a') as f:
    f.write(sys.argv[1] + "\n")
with open(sys.argv[1], 'w') as f:
    for src in sys.argv[2:]:
        with open(src, 'r') as f2:
            f.write(f2.read())
""")

cache = test.workpath('cache')

test.write(['src1', 'SConstruct'], """
DefaultEnvironment(tools=[])
def cat(env, source, target):
    target = str(target[0])
    with open('cat.out', 'a') as f:
        f.write(target + "\\n")
    with open(target, "w") as f:
        for src in source:
            with open(str(src), "r") as f2:
                f.write(f2.read())
env = Environment(tools=[], 
                  BUILDERS={'Internal':Builder(action=cat),
                            'External':Builder(action=r'%(_python_)s build.py $TARGET $SOURCES')})
env.External('aaa.out', 'aaa.in')
env.External('bbb.out', 'bbb.in')
env.Internal('ccc.out', 'ccc.in')
env.Internal('all', ['aaa.out', 'bbb.out', 'ccc.out'])
CacheDir(r'%(cache)s')
""" % locals())

test.write(['src1', 'aaa.in'], "aaa.in\n")
test.write(['src1', 'bbb.in'], "bbb.in\n")
test.write(['src1', 'ccc.in'], "ccc.in\n")

# Verify that a normal build works correctly, and clean up.
# This should populate the cache with our derived files.
test.run(chdir = 'src1', arguments = '.')

test.must_match(['src1', 'all'], "aaa.in\nbbb.in\nccc.in\n", mode='r')

test.must_match(['src1', 'cat.out'], "aaa.out\nbbb.out\nccc.out\nall\n", mode='r')

test.up_to_date(chdir = 'src1', arguments = '.')

test.run(chdir = 'src1', arguments = '-c .')
test.unlink(['src1', 'cat.out'])

# Verify that we now retrieve the derived files from cache,
# not rebuild them.  Then clean up.
test.run(chdir = 'src1', arguments = '.', stdout = test.wrap_stdout("""\
Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""))

test.must_not_exist(test.workpath('src1', 'cat.out'))

test.up_to_date(chdir = 'src1', arguments = '.')

test.run(chdir = 'src1', arguments = '-c .')

# Verify that using --cache-show reports the files as being rebuilt,
# even though we actually fetch them from the cache.  Then clean up.
expect = test.wrap_stdout("""\
%(_python_)s build.py aaa.out aaa.in
%(_python_)s build.py bbb.out bbb.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
""" % locals())

test.run(chdir = 'src1', arguments = '--cache-show .', stdout = expect)

test.must_not_exist(test.workpath('src1', 'cat.out'))

test.up_to_date(chdir = 'src1', arguments = '.')

test.run(chdir = 'src1', arguments = '-c .')

# Verify that using --cache-show -n reports the files as being rebuilt,
# even though we don't actually fetch them from the cache.  No need to
# clean up.
expect = test.wrap_stdout("""\
%(_python_)s build.py aaa.out aaa.in
%(_python_)s build.py bbb.out bbb.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
""" % locals())

test.run(chdir = 'src1', arguments = '--cache-show -n .', stdout = expect)

test.must_not_exist(test.workpath('src1', 'cat.out'))

test.must_not_exist(test.workpath('src1', 'aaa.out'))
test.must_not_exist(test.workpath('src1', 'bbb.out'))
test.must_not_exist(test.workpath('src1', 'ccc.out'))
test.must_not_exist(test.workpath('src1', 'all'))

# Verify that using --cache-show -s doesn't report anything, even though
# we do fetch the files from the cache.  No need to clean up.
test.run(chdir = 'src1',
         arguments = '--cache-show -s .',
         stdout = "")

test.must_match(['src1', 'all'], "aaa.in\nbbb.in\nccc.in\n", mode='r')
test.must_not_exist(test.workpath('src1', 'cat.out'))

#
hello_exe = 'hello' + _exe
hello_obj = 'hello' + _obj
src2_hello = test.workpath('src2', hello_exe)

test.write(['src2', 'SConstruct'], """
env = Environment()
env.Program('hello.c')
CacheDir(r'%s')
""" % (test.workpath('cache')))

test.write(['src2', 'hello.c'], r"""\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("src2/hello.c\n");
        exit (0);
}
""")

# Normal build.
test.run(chdir = 'src2', arguments = '.')

test.run(program = src2_hello, stdout = "src2/hello.c\n")

test.up_to_date(chdir = 'src2', arguments = '.')

test.run(chdir = 'src2', arguments = '-c .')

# Verify that using --cache-show doesn't blow up.
# Don't bother checking the output, since we verified the correct
# behavior above.  We just want to make sure the canonical Program()
# invocation works with --cache-show.
test.run(chdir = 'src2', arguments = '--cache-show .')

test.run(program = src2_hello, stdout = "src2/hello.c\n")

test.up_to_date(chdir = 'src2', arguments = '.')

# All done.
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
