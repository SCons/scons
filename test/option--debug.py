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

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(OBJSUFFIX = '.ooo', PROGSUFFIX = '.xxx')
env.Program('foo', Split('foo.c bar.c'))
""")

test.write('foo.c', r"""
#include "foo.h"
int main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("f1.c\n");
	exit (0);
}
""")

test.write('bar.c', """
#include "bar.h"
""")

test.write('foo.h', """
#ifndef FOO_H
#define FOO_H
#include "bar.h"
#endif
""")

test.write('bar.h', """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif
""")

test.run(arguments = "--debug=tree foo.xxx")

tree = """
+-foo.xxx
  +-foo.ooo
  | +-foo.c
  | +-foo.h
  | +-bar.h
  +-bar.ooo
    +-bar.c
    +-bar.h
    +-foo.h
"""

test.fail_test(string.find(test.stdout(), tree) == -1)

test.run(arguments = "--debug=tree foo.xxx")
test.fail_test(string.find(test.stdout(), tree) == -1)

stree = """
[E B   C]+-foo.xxx
[E B   C]  +-foo.ooo
[E      ]  | +-foo.c
[E      ]  | +-foo.h
[E      ]  | +-bar.h
[E B   C]  +-bar.ooo
[E      ]    +-bar.c
[E      ]    +-bar.h
[E      ]    +-foo.h
"""

test.run(arguments = "--debug=stree foo.xxx")
test.fail_test(string.find(test.stdout(), stree) == -1)

stree2 = """
 E       = exists
  R      = exists in repository only
   b     = implicit builder
   B     = explicit builder
    S    = side effect
     P   = precious
      A  = always build
       C = current

[  B    ]+-foo.xxx
[  B    ]  +-foo.ooo
[E      ]  | +-foo.c
[E      ]  | +-foo.h
[E      ]  | +-bar.h
[  B    ]  +-bar.ooo
[E      ]    +-bar.c
[E      ]    +-bar.h
[E      ]    +-foo.h
"""

test.run(arguments = '-c foo.xxx')
test.run(arguments = "--no-exec --debug=stree foo.xxx")
test.fail_test(string.find(test.stdout(), stree2) == -1)



dtree = """
+-foo.xxx
  +-foo.ooo
  +-bar.ooo
"""

test.run(arguments = "--debug=dtree foo.xxx")
test.fail_test(string.find(test.stdout(), dtree) == -1)

includes = """
+-foo.c
  +-foo.h
    +-bar.h
"""
test.run(arguments = "--debug=includes foo.ooo")
test.fail_test(string.find(test.stdout(), includes) == -1)

# Make sure we print the debug stuff even if there's a build failure.
test.write('bar.h', """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif
THIS SHOULD CAUSE A BUILD FAILURE
""")

test.run(arguments = "--debug=tree foo.xxx",
         status = 2,
         stderr = None)
test.fail_test(string.find(test.stdout(), tree) == -1)

test.run(arguments = "--debug=dtree foo.xxx",
         status = 2,
         stderr = None)
test.fail_test(string.find(test.stdout(), dtree) == -1)

# In an ideal world, --debug=includes would also work when there's a build
# failure, but this would require even more complicated logic to scan
# all of the intermediate nodes that get skipped when the build failure
# occurs.  On the YAGNI theory, we're just not going to worry about this
# until it becomes an issue that someone actually cares enough about.
#test.run(arguments = "--debug=includes foo.xxx",
#         status = 2,
#         stderr = None)
#test.fail_test(string.find(test.stdout(), includes) == -1)

# Restore bar.h to something good.
test.write('bar.h', """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif
""")

# These shouldn't print out anything in particular, but
# they shouldn't crash either:
test.run(arguments = "--debug=includes .")
test.run(arguments = "--debug=includes foo.c")

tree = """scons: `.' is up to date.

+-.
  +-SConstruct
  +-bar.c
  +-bar.h
  +-bar.ooo
  | +-bar.c
  | +-bar.h
  | +-foo.h
  +-foo.c
  +-foo.h
  +-foo.ooo
  | +-foo.c
  | +-foo.h
  | +-bar.h
  +-foo.xxx
    +-foo.ooo
    | +-foo.c
    | +-foo.h
    | +-bar.h
    +-bar.ooo
      +-bar.c
      +-bar.h
      +-foo.h
"""
test.run(arguments = "--debug=tree .")
test.fail_test(string.find(test.stdout(), tree) == -1)

test.run(arguments = "--debug=pdb", stdin = "n\ns\nq\n")
test.fail_test(string.find(test.stdout(), "(Pdb)") == -1)
test.fail_test(string.find(test.stdout(), "scons") == -1)

test.write('foo.c', r"""
#include "foo.h"

int main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("f1.c\n");
	exit (0);
}
""")

test.write('bar.c', """
#include "bar.h"

""")

############################
# test --debug=time

def num(match, line):
    return float(re.match(match, line).group(1))

start_time = time.time()
test.run(program=TestSCons.python, arguments='-c pass')
overhead = time.time() - start_time 

start_time = time.time()
test.run(arguments = "--debug=time .")
expected_total_time = time.time() - start_time - overhead
line = string.split(test.stdout(), '\n')

cmdline = filter(lambda x: x[:23] == "Command execution time:", line)

expected_command_time = num(r'Command execution time: (\d+\.\d+) seconds', cmdline[0])
expected_command_time = expected_command_time + num(r'Command execution time: (\d+\.\d+) seconds', cmdline[1])
expected_command_time = expected_command_time + num(r'Command execution time: (\d+\.\d+) seconds', cmdline[2])

totalline = filter(lambda x: x[:6] == "Total ", line)

total_time = num(r'Total build time: (\d+\.\d+) seconds', totalline[0])
sconscript_time = num(r'Total SConscript file execution time: (\d+\.\d+) seconds', totalline[1])
scons_time = num(r'Total SCons execution time: (\d+\.\d+) seconds', totalline[2])
command_time = num(r'Total command execution time: (\d+\.\d+) seconds', totalline[3])

def check(expected, actual, tolerance):
    return abs((expected-actual)/actual) <= tolerance

assert check(expected_command_time, command_time, 0.01)
assert check(total_time, sconscript_time+scons_time+command_time, 0.01) 
assert check(total_time, expected_total_time, 0.1)

############################
# test --debug=presub

test.write('cat.py', """\
import sys
open(sys.argv[2], "wb").write(open(sys.argv[1], "rb").read())
sys.exit(0)
""")

test.write('SConstruct', """\
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
FILE = Builder(action="$FILECOM")
TEMP = Builder(action="$TEMPCOM")
LIST = Builder(action="$LISTCOM")
FUNC = Builder(action=cat)
env = Environment(PYTHON='%s',
                  BUILDERS = {'FILE':FILE, 'TEMP':TEMP, 'LIST':LIST, 'FUNC':FUNC},
                  FILECOM="$PYTHON cat.py $SOURCES $TARGET",
                  TEMPCOM="$PYTHON cat.py $SOURCES temp\\n$PYTHON cat.py temp $TARGET",
                  LISTCOM=["$PYTHON cat.py $SOURCES temp", "$PYTHON cat.py temp $TARGET"],
                  FUNCCOM=cat)
env.Command('file01.out', 'file01.in', "$FILECOM")
env.Command('file02.out', 'file02.in', ["$FILECOM"])
env.Command('file03.out', 'file03.in', "$TEMPCOM")
env.Command('file04.out', 'file04.in', ["$TEMPCOM"])
env.Command('file05.out', 'file05.in', "$LISTCOM")
env.Command('file06.out', 'file06.in', ["$LISTCOM"])
env.Command('file07.out', 'file07.in', cat)
env.Command('file08.out', 'file08.in', "$FUNCCOM")
env.Command('file09.out', 'file09.in', ["$FUNCCOM"])
env.FILE('file11.out', 'file11.in')
env.FILE('file12.out', 'file12.in')
env.TEMP('file13.out', 'file13.in')
env.TEMP('file14.out', 'file14.in')
env.LIST('file15.out', 'file15.in')
env.LIST('file16.out', 'file16.in')
env.FUNC('file17.out', 'file17.in')
env.FUNC('file18.out', 'file18.in')
""" % TestSCons.python)

test.write('file01.in', "file01.in\n")
test.write('file02.in', "file02.in\n")
test.write('file03.in', "file03.in\n")
test.write('file04.in', "file04.in\n")
test.write('file05.in', "file05.in\n")
test.write('file06.in', "file06.in\n")
test.write('file07.in', "file07.in\n")
test.write('file08.in', "file08.in\n")
test.write('file09.in', "file09.in\n")
test.write('file11.in', "file11.in\n")
test.write('file12.in', "file12.in\n")
test.write('file13.in', "file13.in\n")
test.write('file14.in', "file14.in\n")
test.write('file15.in', "file15.in\n")
test.write('file16.in', "file16.in\n")
test.write('file17.in', "file17.in\n")
test.write('file18.in', "file18.in\n")

expect = """\
Building file01.out with action:
  $PYTHON cat.py $SOURCES $TARGET
__PYTHON__ cat.py file01.in file01.out
Building file02.out with action:
  $PYTHON cat.py $SOURCES $TARGET
__PYTHON__ cat.py file02.in file02.out
Building file03.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file03.in temp
Building file03.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file03.out
Building file04.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file04.in temp
Building file04.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file04.out
Building file05.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file05.in temp
Building file05.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file05.out
Building file06.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file06.in temp
Building file06.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file06.out
Building file07.out with action:
  cat(target, source, env)
cat(["file07.out"], ["file07.in"])
Building file08.out with action:
  cat(target, source, env)
cat(["file08.out"], ["file08.in"])
Building file09.out with action:
  cat(target, source, env)
cat(["file09.out"], ["file09.in"])
Building file11.out with action:
  $PYTHON cat.py $SOURCES $TARGET
__PYTHON__ cat.py file11.in file11.out
Building file12.out with action:
  $PYTHON cat.py $SOURCES $TARGET
__PYTHON__ cat.py file12.in file12.out
Building file13.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file13.in temp
Building file13.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file13.out
Building file14.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file14.in temp
Building file14.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file14.out
Building file15.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file15.in temp
Building file15.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file15.out
Building file16.out with action:
  $PYTHON cat.py $SOURCES temp
__PYTHON__ cat.py file16.in temp
Building file16.out with action:
  $PYTHON cat.py temp $TARGET
__PYTHON__ cat.py temp file16.out
Building file17.out with action:
  cat(target, source, env)
cat(["file17.out"], ["file17.in"])
Building file18.out with action:
  cat(target, source, env)
cat(["file18.out"], ["file18.in"])
"""
expect = string.replace(expect, '__PYTHON__', TestSCons.python)
test.run(arguments = "--debug=presub .", stdout=test.wrap_stdout(expect))

test.must_match('file01.out', "file01.in\n")
test.must_match('file02.out', "file02.in\n")
test.must_match('file03.out', "file03.in\n")
test.must_match('file04.out', "file04.in\n")
test.must_match('file05.out', "file05.in\n")
test.must_match('file06.out', "file06.in\n")
test.must_match('file07.out', "file07.in\n")
test.must_match('file08.out', "file08.in\n")
test.must_match('file09.out', "file09.in\n")
test.must_match('file11.out', "file11.in\n")
test.must_match('file12.out', "file12.in\n")
test.must_match('file13.out', "file13.in\n")
test.must_match('file14.out', "file14.in\n")
test.must_match('file15.out', "file15.in\n")
test.must_match('file16.out', "file16.in\n")
test.must_match('file17.out', "file17.in\n")
test.must_match('file18.out', "file18.in\n")

############################
# test --debug=stacktrace

test.write('SConstruct', """\
def kfile_scan(node, env, target):
    raise "kfile_scan error"

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                skeys = ['.k'])

env = Environment()
env.Append(SCANNERS = [kscan])

env.Command('foo', 'foo.k', Copy('$TARGET', '$SOURCE'))
""")

test.write('foo.k', "foo.k\n")

test.run(status = 2, stderr = "scons: *** kfile_scan error\n")

test.run(arguments = "--debug=stacktrace",
         status = 2,
         stderr = None)

stderr = test.stderr()

lines = [
    "scons: *** kfile_scan error",
    "scons: internal stack trace:",
    'raise "kfile_scan error"',
]

missing = []
for line in lines:
    if string.find(stderr, line) == -1:
        missing.append(line)

if missing:
    print "STDERR is missing the following lines:"
    print "\t" + string.join(lines, "\n\t")
    print "STDERR ====="
    print stderr
    test.fail_test(1)

test.pass_test()
