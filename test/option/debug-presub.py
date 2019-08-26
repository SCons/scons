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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
with open(sys.argv[2], "wb") as f, open(sys.argv[1], "rb") as infp:
    f.write(infp.read())
sys.exit(0)
""")

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as infp:
                f.write(infp.read())
FILE = Builder(action="$FILECOM")
TEMP = Builder(action="$TEMPCOM")
LIST = Builder(action="$LISTCOM")
FUNC = Builder(action=cat)
env = Environment(tools=[],
                  PYTHON=r'%(_python_)s',
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

env2 = Environment(PYTHON=r'%(_python_)s',
                   CCCOM="$PYTHON cat.py $SOURCES $TARGET")
env2.Object('file20.obj', 'file20.c')
""" % locals())

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

test.write('file20.c', "file20.c\n")

expect = """\
Building file01.out with action:
  $PYTHON cat.py $SOURCES $TARGET
%(_python_)s cat.py file01.in file01.out
Building file02.out with action:
  $PYTHON cat.py $SOURCES $TARGET
%(_python_)s cat.py file02.in file02.out
Building file03.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file03.in temp
Building file03.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file03.out
Building file04.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file04.in temp
Building file04.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file04.out
Building file05.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file05.in temp
Building file05.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file05.out
Building file06.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file06.in temp
Building file06.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file06.out
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
%(_python_)s cat.py file11.in file11.out
Building file12.out with action:
  $PYTHON cat.py $SOURCES $TARGET
%(_python_)s cat.py file12.in file12.out
Building file13.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file13.in temp
Building file13.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file13.out
Building file14.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file14.in temp
Building file14.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file14.out
Building file15.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file15.in temp
Building file15.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file15.out
Building file16.out with action:
  $PYTHON cat.py $SOURCES temp
%(_python_)s cat.py file16.in temp
Building file16.out with action:
  $PYTHON cat.py temp $TARGET
%(_python_)s cat.py temp file16.out
Building file17.out with action:
  cat(target, source, env)
cat(["file17.out"], ["file17.in"])
Building file18.out with action:
  cat(target, source, env)
cat(["file18.out"], ["file18.in"])
Building file20.obj with action:
  $PYTHON cat.py $SOURCES $TARGET
%(_python_)s cat.py file20.c file20.obj
""" % locals()

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

test.must_match('file20.obj', "file20.c\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
