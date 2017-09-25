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
Verify that the Return() function stops processing the SConscript file
at the point is called, unless the stop= keyword argument is supplied.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
SConscript('SConscript1')
x = SConscript('SConscript2')
y, z = SConscript('SConscript3')
a4, b4 = SConscript('SConscript4')
foo, bar = SConscript('SConscript5')
for var in ['x','y','z','a4','b4','foo','bar']:
    print("%s = %s"%(var,globals()[var]))
""")

test.write('SConscript1', """\
print("line 1")
Return()
print("line 2")
""")

test.write('SConscript2', """\
print("line 3")
x = 7
Return('x')
print("line 4")
""")

test.write('SConscript3', """\
print("line 5")
y = 8
z = 9
Return('y z')
print("line 6")
""")

test.write('SConscript4', """\
a4 = 'aaa'
b4 = 'bbb'
print("line 7")
Return('a4', 'b4', stop=False)
b4 = 'b-after'
print("line 8")
""")

test.write('SConscript5', """\
foo = 'foo'
bar = 'bar'
Return(["foo", "bar"])
print("line 9")
""")

expect = """\
line 1
line 3
line 5
line 7
line 8
x = 7
y = 8
z = 9
a4 = aaa
b4 = bbb
foo = foo
bar = bar
"""

test.run(arguments = '-q -Q', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
