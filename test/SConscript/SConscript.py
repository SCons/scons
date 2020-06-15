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

test = TestSCons.TestSCons()

test.write('foo.py', "foo = 4\n")


test.write('SConstruct', """\
import os
import foo
from collections import UserList

assert foo.foo == 4

print("SConstruct "+ os.getcwd())
SConscript('SConscript')

x1 = "SConstruct x1"
x2 = "SConstruct x2"
x3,x4 = SConscript('SConscript1', "x1 x2")
assert x3 == "SConscript1 x3", x3
assert x4 == "SConscript1 x4", x4

(x3,x4) = SConscript('SConscript2', ["x1","x2"])
assert x3 == "SConscript2 x3", x3
assert x4 == "SConscript2 x4", x4

Export("x1 x2")
SConscript('SConscript3')
Import("x1 x2")
assert x1 == "SConscript3 x1", x1
assert x2 == "SConscript3 x2", x2

x1 = "SConstruct x1"
x2 = "SConstruct x2"
Export("x1","x2")
SConscript('SConscript4')
Import("x1"," x2")
assert x1 == "SConscript4 x1", x1
assert x2 == "SConscript4 x2", x2

subdir = Dir('subdir')
script = File('SConscript', subdir)
foo = SConscript(script)
assert foo == "subdir/SConscript foo"

SConscript('SConscript5')

x7 = "SConstruct x7"
x8 = "SConstruct x8"
x9 = SConscript('SConscript6', UserList(["x7", "x8"]))
assert x9 == "SConscript6 x9", x9

SConscript('SConscript7')
""")


test.write('SConscript', """\
# os should not be automatically imported:
assert "os" not in globals()

import os
print("SConscript " + os.getcwd())
""")

test.write('SConscript1', """
Import("x1 x2")
assert x1 == "SConstruct x1", x1
assert x2 == "SConstruct x2", x2

x3 = "SConscript1 x3"
x4 = "SConscript1 x4"
Return("x3 x4")
""")


test.write('SConscript2', """\
Import("x1","x2")
assert x1 == "SConstruct x1", x1
assert x2 == "SConstruct x2", x2
x3 = "SConscript2 x3"
x4 = "SConscript2 x4"
Return("x3","x4")
""")


test.write('SConscript3', """\
Import("x1 x2")
assert x1 == "SConstruct x1", x1
assert x2 == "SConstruct x2", x2
x1 = "SConscript3 x1"
x2 = "SConscript3 x2"

x5 = SConscript('SConscript31', "x1")
Import("x6")
assert x5 == "SConscript31 x5", x5
assert x6 == "SConscript31 x6", x6

Export("x1 x2")
""")


test.write('SConscript31', """\
Import("x1 x2")
assert x1 == "SConscript3 x1", x1
assert x2 == "SConstruct x2", x2
x5 = "SConscript31 x5"
x6 = "SConscript31 x6"
Export("x6")
Return("x5")
""")


test.write('SConscript4', """\
Import("x1", "x2")
assert x1 == "SConstruct x1", x1
assert x2 == "SConstruct x2", x2
x1 = "SConscript4 x1"
x2 = "SConscript4 x2"
Export("x1", "x2")
""")


test.subdir('subdir')
test.write(['subdir', 'SConscript'], """\
foo = 'subdir/SConscript foo'
Return('foo')
""")


test.write('SConscript5', """\
B = Builder(action = 'B')
def scan():
    pass
S = Scanner(function = scan)
A = Action("A")
""")


test.write('SConscript6', """\
Import("x7 x8")
assert x7 == "SConstruct x7", x7
assert x8 == "SConstruct x8", x8
x9 = "SConscript6 x9"
Return("x9")
""")


test.write('SConscript7', """\
result1 = ((1, 3), -4)
result2 = ((2, 3), -4)
assert result1 == SConscript(Split('foo/SConscript bar/SConscript'))
assert result1 == SConscript(['foo/SConscript', 'bar/SConscript'])
assert result1 == SConscript([File('foo/SConscript'), File('bar/SConscript')])
assert result1 == SConscript(dirs = Split('foo bar'))
assert result1 == SConscript(dirs = ['foo', 'bar'])
assert result2 == SConscript(dirs = Split('foo bar'), name = 'subscript')
assert result2 == SConscript(dirs = ['foo', 'bar'], name = 'subscript')
assert result1 == SConscript(dirs = ['foo', Dir('bar')])
assert result2 == SConscript(dirs = [Dir('foo'), 'bar'], name = 'subscript')
assert 5 == SConscript('w s/SConscript')
assert (-4, 5) == SConscript(['bar/SConscript', 'w s/SConscript'])

x1 = 3
x2 = 2
assert (3, 2) == SConscript(dirs = 'baz', exports = "x1 x2")
assert (3, 2) == SConscript('baz/SConscript', 'x1', exports = 'x2')
assert (3, 2) == SConscript('baz/SConscript', exports = 'x1 x2')
""")

fooscript = "x = %d; y = 3; Return('x y')\n"
barscript = "x = -4; Return('x')\n"

test.subdir('foo', 'bar', 'baz', 'w s')
test.write(['foo', 'SConscript'], fooscript % 1)
test.write(['foo', 'subscript'],  fooscript % 2)
test.write(['bar', 'SConscript'], barscript)
test.write(['bar', 'subscript'],  barscript)
test.write(['baz', 'SConscript'], """\
Import("x1 x2")
result = (x1, x2)
Return("result")
""")
test.write(['w s', 'SConscript'], "x = 5; Return('x')\n")


wpath = test.workpath()

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = 'SConstruct %s\nSConscript %s\n' % (wpath, wpath),
                                   build_str = "scons: `.' is up to date.\n"))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
