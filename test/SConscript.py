#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

test.write('SConstruct', """
import os

print "SConstruct", os.getcwd()
SConscript('SConscript')

x1 = "SConstruct x1"
x2 = "SConstruct x2"
x3,x4 = SConscript('SConscript1', "x1 x2")
assert x3 == "SConscript1 x3"
assert x4 == "SConscript1 x4"


(x3,x4) = SConscript('SConscript2', ["x1","x2"])
assert x3 == "SConscript2 x3"
assert x4 == "SConscript2 x4"

Export("x1 x2")
SConscript('SConscript3')
Import("x1 x2")
assert x1 == "SConscript3 x1"
assert x2 == "SConscript3 x2"

x1 = "SConstruct x1"
x2 = "SConstruct x2"
Export("x1","x2")
SConscript('SConscript4')
Import("x1"," x2")
assert x1 == "SConscript4 x1"
assert x2 == "SConscript4 x2"

""")

test.write('SConscript', """

# os should not be automajically imported:
assert not globals().has_key("os")

import os
print "SConscript " + os.getcwd()
""")

test.write('SConscript1', """
Import("x1 x2")
assert x1 == "SConstruct x1"
assert x2 == "SConstruct x2"

x3 = "SConscript1 x3"
x4 = "SConscript1 x4"
Return("x3 x4")
""")



test.write('SConscript2', """
Import("x1","x2")
assert x1 == "SConstruct x1"
assert x2 == "SConstruct x2"
x3 = "SConscript2 x3"
x4 = "SConscript2 x4"
Return("x3","x4")
""")

test.write('SConscript3', """
Import("x1 x2")
assert x1 == "SConstruct x1"
assert x2 == "SConstruct x2"
x1 = "SConscript3 x1"
x2 = "SConscript3 x2"

x5 = SConscript('SConscript31', "x1")
Import("x6")
assert x5 == "SConscript31 x5"
assert x6 == "SConscript31 x6"

Export("x1 x2")


""")

test.write('SConscript31', """
Import("x1 x2")
assert x1 == "SConscript3 x1"
assert x2 == "SConstruct x2"
x5 = "SConscript31 x5"
x6 = "SConscript31 x6"
Export("x6")
Return("x5")
""")


test.write('SConscript4', """
Import("x1", "x2")
assert x1 == "SConstruct x1"
assert x2 == "SConstruct x2"
x1 = "SConscript4 x1"
x2 = "SConscript4 x2"
Export("x1", "x2")
""")


wpath = test.workpath()

test.run(stdout = "SConstruct %s\nSConscript %s\n" % (wpath, wpath))

test.pass_test()
