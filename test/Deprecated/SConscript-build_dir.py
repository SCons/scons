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
Verify that specifying a build_dir argument to SConscript still works.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConscript', """
SConscript('DummyScript', build_dir = 'build')
""")

test.write('DummyScript', """
""")

msg = """The build_dir keyword has been deprecated; use the variant_dir keyword instead."""
test.deprecated_warning('deprecated-build-dir', msg)

warning = '\nscons: warning: ' + TestSCons.re_escape(msg) \
                               + '\n' + TestSCons.file_expr

all1 = test.workpath('test', 'build', 'var1', 'all')
all2 = test.workpath('test', 'build', 'var2', 'all')
all3 = test.workpath('test', 'build', 'var3', 'all')
all4 = test.workpath('test', 'build', 'var4', 'all')
all5 = test.workpath('build', 'var5', 'all')
all6 = test.workpath('build', 'var6', 'all')
all7 = test.workpath('build', 'var7', 'all')
all8 = test.workpath('build', 'var8', 'all')
all9 = test.workpath('test', 'build', 'var9', 'src', 'all')

test.subdir('test')

test.write(['test', 'SConstruct'], """
SetOption('warn', 'deprecated-build-dir')
src = Dir('src')
alt = Dir('alt')
var1 = Dir('build/var1')
var2 = Dir('build/var2')
var3 = Dir('build/var3')
var4 = Dir('build/var4')
var5 = Dir('../build/var5')
var6 = Dir('../build/var6')
var7 = Dir('../build/var7')
var8 = Dir('../build/var8')
var9 = Dir('../build/var9')

def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as ofp:
        for src in source:
            with open(str(src), "rb") as ifp:
                ofp.write(ifp.read())

env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  BUILD='build')

Export("env")

SConscript('src/SConscript', build_dir=var1)
SConscript('src/SConscript', build_dir='build/var2', src_dir=src)

SConscript('src/SConscript', build_dir='build/var3', duplicate=0)

#XXX We can't support var4 and var5 yet, because our VariantDir linkage
#XXX is to an entire source directory.  We haven't yet generalized our
#XXX infrastructure to be able to take the SConscript file from one source
#XXX directory, but the rest of the files from a different one.
#XXX SConscript('src/SConscript', build_dir=var4, src_dir=alt, duplicate=0)

#XXX SConscript('src/SConscript', build_dir='../build/var5', src_dir='alt')
SConscript('src/SConscript', build_dir=var6)

SConscript('src/SConscript', build_dir=var7, src_dir=src, duplicate=0)
env.SConscript('src/SConscript', build_dir='../$BUILD/var8', duplicate=0)

# This tests the fact that if you specify a src_dir that is above
# the dir a SConscript is in, that we do the intuitive thing, i.e.,
# we set the path of the SConscript accordingly.  The below is
# equivalent to saying:
#
# VariantDir('build/var9', '.')
# SConscript('build/var9/src/SConscript')
SConscript('src/SConscript', build_dir='build/var9', src_dir='.')
""") 

test.subdir(['test', 'src'], ['test', 'alt'])

test.write(['test', 'src', 'SConscript'], """
Import("env")
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
""")

test.write('test/src/aaa.in', "test/src/aaa.in\n")
test.write('test/src/bbb.in', "test/src/bbb.in\n")
test.write('test/src/ccc.in', "test/src/ccc.in\n")

test.write('test/alt/aaa.in', "test/alt/aaa.in\n")
test.write('test/alt/bbb.in', "test/alt/bbb.in\n")
test.write('test/alt/ccc.in', "test/alt/ccc.in\n")

test.run(chdir='test', arguments = '. ../build', stderr = 7*warning)

all_src = "test/src/aaa.in\ntest/src/bbb.in\ntest/src/ccc.in\n"
all_alt = "test/alt/aaa.in\ntest/alt/bbb.in\ntest/alt/ccc.in\n"

test.must_match(all1, all_src)
test.must_match(all2, all_src)
test.must_match(all3, all_src)
#XXX We can't support var4 and var5 yet, because our VariantDir linkage
#XXX is to an entire source directory.  We haven't yet generalized our
#XXX infrastructure to be able to take the SConscript file from one source
#XXX directory, but the rest of the files from a different one.
#XXX test.must_match(all4, all_alt)
#XXX test.must_match(all5, all_alt)
test.must_match(all6, all_src)
test.must_match(all7, all_src)
test.must_match(all8, all_src)
test.must_match(all9, all_src)

import os
import stat
def equal_stats(x,y):
    x = os.stat(x)
    y = os.stat(y)
    return (stat.S_IMODE(x[stat.ST_MODE]) == stat.S_IMODE(y[stat.ST_MODE]) and
            x[stat.ST_MTIME] ==  y[stat.ST_MTIME])

# Make sure we did duplicate the source files in build/var1,
# and that their stats are the same:
for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.must_exist(test.workpath('test', 'build', 'var1', file))
    test.fail_test(not equal_stats(test.workpath('test', 'build', 'var1', file),
                                   test.workpath('test', 'src', file)))

# Make sure we did duplicate the source files in build/var2,
# and that their stats are the same:
for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.must_exist(test.workpath('test', 'build', 'var2', file))
    test.fail_test(not equal_stats(test.workpath('test', 'build', 'var2', file),
                                   test.workpath('test', 'src', file)))
 
# Make sure we didn't duplicate the source files in build/var3.
test.must_not_exist(test.workpath('test', 'build', 'var3', 'aaa.in'))
test.must_not_exist(test.workpath('test', 'build', 'var3', 'bbb.in'))
test.must_not_exist(test.workpath('test', 'build', 'var3', 'ccc.in'))
 
#XXX We can't support var4 and var5 yet, because our VariantDir linkage
#XXX is to an entire source directory.  We haven't yet generalized our
#XXX infrastructure to be able to take the SConscript file from one source
#XXX directory, but the rest of the files from a different one.
#XXX Make sure we didn't duplicate the source files in build/var4.
#XXXtest.must_not_exist(test.workpath('test', 'build', 'var4', 'aaa.in'))
#XXXtest.must_not_exist(test.workpath('test', 'build', 'var4', 'bbb.in'))
#XXXtest.must_not_exist(test.workpath('test', 'build', 'var4', 'ccc.in'))

#XXX We can't support var4 and var5 yet, because our VariantDir linkage
#XXX is to an entire source directory.  We haven't yet generalized our
#XXX infrastructure to be able to take the SConscript file from one source
#XXX directory, but the rest of the files from a different one.
#XXX Make sure we did duplicate the source files in build/var5,
#XXX and that their stats are the same:
#XXXfor file in ['aaa.in', 'bbb.in', 'ccc.in']:
#XXX    test.must_exist(test.workpath('build', 'var5', file))
#XXX    test.fail_test(not equal_stats(test.workpath('build', 'var5', file),
#XXX                                   test.workpath('test', 'src', file)))

# Make sure we did duplicate the source files in build/var6,
# and that their stats are the same:
for file in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.must_exist(test.workpath('build', 'var6', file))
    test.fail_test(not equal_stats(test.workpath('build', 'var6', file),
                                   test.workpath('test', 'src', file)))
 
# Make sure we didn't duplicate the source files in build/var7.
test.must_not_exist(test.workpath('build', 'var7', 'aaa.in'))
test.must_not_exist(test.workpath('build', 'var7', 'bbb.in'))
test.must_not_exist(test.workpath('build', 'var7', 'ccc.in'))
 
# Make sure we didn't duplicate the source files in build/var8.
test.must_not_exist(test.workpath('build', 'var8', 'aaa.in'))
test.must_not_exist(test.workpath('build', 'var8', 'bbb.in'))
test.must_not_exist(test.workpath('build', 'var8', 'ccc.in'))

###################
test.subdir('test2')

test.write(['test2', 'SConstruct'], """\
SConscript('SConscript', build_dir='Build', src_dir='.', duplicate=0)
""")

test.write(['test2', 'SConscript'], """\
env = Environment()
foo_obj = env.Object('foo.c')
env.Program('foo', [foo_obj, 'bar.c'])
""")

test.write(['test2', 'bar.c'], r"""
#include <stdio.h>
#include <stdlib.h>

void
bar(void) {
        printf("bar.c\n");
}
""")

test.write(['test2', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>

extern void
bar(void);

int
main(int argc, char *argv[]) {
        bar();
        printf("foo.c\n");
}
""")

test.run(chdir="test2", stderr = warning)

_obj = TestSCons._obj

test.must_not_exist(test.workpath('test2', 'foo' + _obj))
test.must_not_exist(test.workpath('test2', 'bar' + _obj))
test.must_exist(test.workpath('test2', 'Build', 'foo' + _obj))
test.must_exist(test.workpath('test2', 'Build', 'bar' + _obj))

###################
# Make sure that directories for subsidiary SConscript() calls
# in a build_dir get created if they don't already exist.
test.subdir('test3')

test.subdir(['test3', 'src'], ['test3', 'src', '_glscry'])

test.write(['test3', 'SConstruct'], """\
SConscript(dirs=['src'], build_dir='build', duplicate=0)
""")

test.write(['test3', 'src', 'SConscript'], """\
SConscript(dirs=['_glscry'])
""")

test.write(['test3', 'src', '_glscry', 'SConscript'], """\
""")

test.write(['test3', 'src', 'file.in'], "file.in\n")

test.write(['test3', 'src', '_glscry', 'file.in'], "file.in\n")

test.run(chdir='test3', stderr = warning)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
