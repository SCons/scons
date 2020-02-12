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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

fortran = test.detect('FORTRAN')

foo11 = test.workpath('work1', 'build', 'var1', 'foo1' + _exe)
foo12 = test.workpath('work1', 'build', 'var1', 'foo2' + _exe)
foo21 = test.workpath('work1', 'build', 'var2', 'foo1' + _exe)
foo22 = test.workpath('work1', 'build', 'var2', 'foo2' + _exe)
foo31 = test.workpath('work1', 'build', 'var3', 'foo1' + _exe)
foo32 = test.workpath('work1', 'build', 'var3', 'foo2' + _exe)
foo41 = test.workpath('work1', 'build', 'var4', 'foo1' + _exe)
foo42 = test.workpath('work1', 'build', 'var4', 'foo2' + _exe)
foo51 = test.workpath('build', 'var5', 'foo1' + _exe)
foo52 = test.workpath('build', 'var5', 'foo2' + _exe)

bar11 = test.workpath('work1', 'build', 'var1', 'bar1' + _exe)
bar12 = test.workpath('work1', 'build', 'var1', 'bar2' + _exe)
bar21 = test.workpath('work1', 'build', 'var2', 'bar1' + _exe)
bar22 = test.workpath('work1', 'build', 'var2', 'bar2' + _exe)
bar31 = test.workpath('work1', 'build', 'var3', 'bar1' + _exe)
bar32 = test.workpath('work1', 'build', 'var3', 'bar2' + _exe)
bar41 = test.workpath('work1', 'build', 'var4', 'bar1' + _exe)
bar42 = test.workpath('work1', 'build', 'var4', 'bar2' + _exe)
bar51 = test.workpath('build', 'var5', 'bar1' + _exe)
bar52 = test.workpath('build', 'var5', 'bar2' + _exe)

test.subdir('work1', 'work2', 'work3')

test.write(['work1', 'SConstruct'], """
DefaultEnvironment(tools=[])
src = Dir('src')
var2 = Dir('build/var2')
var3 = Dir('build/var3')
var4 = Dir('build/var4')
var5 = Dir('../build/var5')
var6 = Dir('../build/var6')

env = Environment(BUILD = 'build', SRC = 'src')

VariantDir('build/var1', src)
VariantDir(var2, src)
VariantDir(var3, src, duplicate=0)
env.VariantDir("$BUILD/var4", "$SRC", duplicate=0)
VariantDir(var5, src, duplicate=0)
VariantDir(var6, src)

env = Environment(CPPPATH='#src', FORTRANPATH='#src')
SConscript('build/var1/SConscript', "env")
SConscript('build/var2/SConscript', "env")

env = Environment(CPPPATH=src, FORTRANPATH=src)
SConscript('build/var3/SConscript', "env")
SConscript(File('SConscript', var4), "env")

env = Environment(CPPPATH='.', FORTRANPATH='.')
SConscript('../build/var5/SConscript', "env")
SConscript('../build/var6/SConscript', "env")
""")

test.subdir(['work1', 'src'])
test.write(['work1', 'src', 'SConscript'], """
import os.path
import sys

def buildIt(target, source, env):
    if not os.path.exists('build'):
        os.mkdir('build')
    f1=open(str(source[0]), 'r')
    f2=open(str(target[0]), 'w')
    f2.write(f1.read())
    f2.close()
    f1.close()
    return 0
Import("env")
env.Command(target='f2.c', source='f2.in', action=buildIt)
env.Program(target='foo2', source='f2.c')
env.Program(target='foo1', source='f1.c')
env.Command(target='f3.h', source='f3h.in', action=buildIt)
env.Command(target='f4.h', source='f4h.in', action=buildIt)
env.Command(target='f4.c', source='f4.in', action=buildIt)

env2=env.Clone(CPPPATH='.')
env2.Program(target='foo3', source='f3.c')
env2.Program(target='foo4', source='f4.c')

try:
    fortran = env.subst('$FORTRAN')
except:
    fortran = None

if fortran and env.Detect(fortran):
    if sys.platform =='win32':
        env_prog=Environment(tools=['mingw'], 
        # BUILD = env['BUILD'], SRC = ENV['src'],
        CPPPATH=env['CPPPATH'], FORTRANPATH=env['FORTRANPATH'] )
    else:
        env_prog=env.Clone()

    env.Command(target='b2.f', source='b2.in', action=buildIt)
    env_prog.Program(target='bar2', source='b2.f')
    env_prog.Program(target='bar1', source='b1.f')
""")

test.write(['work1', 'src', 'f1.c'], r"""
#include <stdio.h>
#include <stdlib.h>

#include "f1.h"

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf(F1_STR);
        exit (0);
}
""")

test.write(['work1', 'src', 'f2.in'], r"""
#include <stdio.h>
#include <stdlib.h>

#include "f2.h"

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf(F2_STR);
        exit (0);
}
""")

test.write(['work1', 'src', 'f3.c'], r"""
#include <stdio.h>
#include <stdlib.h>

#include "f3.h"

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf(F3_STR);
        exit (0);
}
""")

test.write(['work1', 'src', 'f4.in'], r"""
#include <stdio.h>
#include <stdlib.h>

#include "f4.h"

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf(F4_STR);
        exit (0);
}
""")

test.write(['work1', 'src', 'f1.h'], r"""
#define F1_STR "f1.c\n"
""")

test.write(['work1', 'src', 'f2.h'], r"""
#define F2_STR "f2.c\n"
""")

test.write(['work1', 'src', 'f3h.in'], r"""
#define F3_STR "f3.c\n"
""")

test.write(['work1', 'src', 'f4h.in'], r"""
#define F4_STR "f4.c\n"
""")

test.write(['work1', 'src', 'b1.f'], r"""
      PROGRAM FOO
      INCLUDE 'b1.for'
      STOP
      END
""")

test.write(['work1', 'src', 'b2.in'], r"""
      PROGRAM FOO
      INCLUDE 'b2.for'
      STOP
      END
""")

test.write(['work1', 'src', 'b1.for'], r"""
      PRINT *, 'b1.for'
""")

test.write(['work1', 'src', 'b2.for'], r"""
      PRINT *, 'b2.for'
""")

# Some releases of freeBSD seem to have library complaints about
# tempnam().  Filter out these annoying messages before checking for
# error output.
def blank_output(err):
    if not err:
        return 1
    stderrlines = [l for l in err.split('\n') if l]
    msg = "warning: tempnam() possibly used unsafely"
    stderrlines = [l for l in stderrlines if l.find(msg) == -1]
    return len(stderrlines) == 0

test.run(chdir='work1', arguments = '. ../build', stderr=None)

test.fail_test(not blank_output(test.stderr()))

test.run(program = foo11, stdout = "f1.c\n")
test.run(program = foo12, stdout = "f2.c\n")
test.run(program = foo21, stdout = "f1.c\n")
test.run(program = foo22, stdout = "f2.c\n")
test.run(program = foo31, stdout = "f1.c\n")
test.run(program = foo32, stdout = "f2.c\n")
test.run(program = foo41, stdout = "f1.c\n")
test.run(program = foo42, stdout = "f2.c\n")
test.run(program = foo51, stdout = "f1.c\n")
test.run(program = foo52, stdout = "f2.c\n")

if fortran:
    test.run(program = bar11, stdout = " b1.for\n")
    test.run(program = bar12, stdout = " b2.for\n")
    test.run(program = bar21, stdout = " b1.for\n")
    test.run(program = bar22, stdout = " b2.for\n")
    test.run(program = bar31, stdout = " b1.for\n")
    test.run(program = bar32, stdout = " b2.for\n")
    test.run(program = bar41, stdout = " b1.for\n")
    test.run(program = bar42, stdout = " b2.for\n")
    test.run(program = bar51, stdout = " b1.for\n")
    test.run(program = bar52, stdout = " b2.for\n")

test.run(chdir='work1', arguments='. ../build', stdout=test.wrap_stdout("""\
scons: `.' is up to date.
scons: `%s' is up to date.
""" % test.workpath('build')))

import os
import stat
def equal_stats(x,y):
    x = os.stat(x)
    y = os.stat(y)
    return (stat.S_IMODE(x[stat.ST_MODE]) == stat.S_IMODE(y[stat.ST_MODE]) and
            x[stat.ST_MTIME] ==  y[stat.ST_MTIME])

# Make sure we did duplicate the source files in build/var2,
# and that their stats are the same:
test.must_exist(['work1', 'build', 'var2', 'f1.c'])
test.must_exist(['work1', 'build', 'var2', 'f2.in'])
test.fail_test(not equal_stats(test.workpath('work1', 'build', 'var2', 'f1.c'), test.workpath('work1', 'src', 'f1.c')))
test.fail_test(not equal_stats(test.workpath('work1', 'build', 'var2', 'f2.in'), test.workpath('work1', 'src', 'f2.in')))
 
# Make sure we didn't duplicate the source files in build/var3.
test.must_not_exist(['work1', 'build', 'var3', 'f1.c'])
test.must_not_exist(['work1', 'build', 'var3', 'f2.in'])
test.must_not_exist(['work1', 'build', 'var3', 'b1.f'])
test.must_not_exist(['work1', 'build', 'var3', 'b2.in'])

# Make sure we didn't duplicate the source files in build/var4.
test.must_not_exist(['work1', 'build', 'var4', 'f1.c'])
test.must_not_exist(['work1', 'build', 'var4', 'f2.in'])
test.must_not_exist(['work1', 'build', 'var4', 'b1.f'])
test.must_not_exist(['work1', 'build', 'var4', 'b2.in'])

# Make sure we didn't duplicate the source files in build/var5.
test.must_not_exist(['build', 'var5', 'f1.c'])
test.must_not_exist(['build', 'var5', 'f2.in'])
test.must_not_exist(['build', 'var5', 'b1.f'])
test.must_not_exist(['build', 'var5', 'b2.in'])

# verify that header files in the source directory are scanned properly:
test.write(['work1', 'src', 'f1.h'], r"""
#define F1_STR "f1.c 2\n"
""")

test.write(['work1', 'src', 'f3h.in'], r"""
#define F3_STR "f3.c 2\n"
""")

test.write(['work1', 'src', 'f4h.in'], r"""
#define F4_STR "f4.c 2\n"
""")

test.run(chdir='work1', arguments = '../build/var5', stderr=None)

test.fail_test(not blank_output(test.stderr()))

test.run(program = foo51, stdout = "f1.c 2\n")
test.run(program = test.workpath('build', 'var5', 'foo3' + _exe),
                                 stdout = "f3.c 2\n")
test.run(program = test.workpath('build', 'var5', 'foo4' + _exe),
                                 stdout = "f4.c 2\n")

test.run(chdir='work1', arguments='../build/var5', stdout=test.wrap_stdout("""\
scons: `%s' is up to date.
""" % test.workpath('build', 'var5')))

#
test.write(['work2', 'SConstruct'], """\
env = Environment()
env.Program('prog.c')
""")

test.write(['work2', 'prog.c'], r"""
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("work2/prog.c\n");
        exit (0);
}
""")

test.run(chdir='work2', arguments='.')

test.up_to_date(chdir='work2', arguments='.')

#
test.write(['work2', 'SConstruct'], """\
env = Environment()
VariantDir('build', '.')
Export('env')
SConscript('build/SConscript')
""")

test.write(['work2', 'SConscript'], """\
Import('env')
env.Program('prog.c')
""")

test.run(chdir='work2', arguments='.', stderr=None)

test.fail_test(not blank_output(test.stderr()))

test.run(chdir='work2', arguments='.',
         stdout=test.wrap_stdout("""\
scons: building associated VariantDir targets: build
scons: `.' is up to date.
"""))

test.write( ['work3', 'SConstruct'], """\
SConscriptChdir(0)
VariantDir('build', '.', duplicate=1 ) 
SConscript( 'build/SConscript' )
""")

test.write( ['work3', 'SConscript'], """\
import sys
headers = ['existing.h', 'non_existing.h']
for header in headers:
    h = File( header )
    contents = h.get_text_contents()
    sys.stderr.write( '%s:%s\\n' % (header, contents))
""")

test.write( ['work3', 'existing.h'], """\
/* a header file */\
""")

test.run(chdir='work3',
         stdout=test.wrap_stdout("""\
scons: building associated VariantDir targets: build
scons: `.' is up to date.
"""),
         stderr="""\
existing.h:/* a header file */
non_existing.h:
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
