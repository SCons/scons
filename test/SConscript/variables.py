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
Test importing and exporting variables between SConscript files.
"""

import TestSCons

test = TestSCons.TestSCons()


# SConscript to detect if exported variables are intact
test.write("SConscript", """
Import(['x', 'y'])
assert x == 'x'
assert y == 'zoom'
""")

# Test exporting all global variables as a list of keys:
test.write("SConstruct", """
x = 'x'
y = 'zoom'
Export(list(globals().keys()))                         
SConscript('SConscript')
""")

test.run(arguments = ".")

# Test exporting all global variables as a list of keys in SConscript call:
test.write("SConstruct", """
x = 'x'
y = 'zoom'
SConscript('SConscript', list(globals().keys()))
""")

test.run(arguments = ".")

# Test exporting all global variables as a dictionary:
test.write("SConstruct", """
x = 'x'
y = 'zoom'
Export(globals())                         
SConscript('SConscript')
""")

test.run(arguments = ".")

# Test exporting all global variables as dictionary in SConscript call:
test.write("SConstruct", """
x = 'x'
y = 'zoom'
SConscript('SConscript', globals())
""")

test.run(arguments = ".")

# Test exporting variables as keywords:
test.write("SConstruct", """
Export(x = 'x', y = 'zoom')
""")

test.run(arguments = ".")

# Test export of local variables:
test.write("SConstruct", """
def f():
    x = 'x'
    y = 'zoom'
    Export('x', 'y')

f()
SConscript('SConscript')
""")

test.run(arguments = ".")

# Test export of local variables in SConscript call:
test.write("SConstruct", """
def f():
    x = 'x'
    y = 'zoom'
    SConscript('SConscript', ['x', 'y'])
f()
""")

test.run(arguments = ".")

# Test export of local variables as a dictionary:
test.write("SConstruct", """
def f():
    x = 'x'
    y = 'zoom'
    Export(locals())

f()
SConscript('SConscript')
""")

test.run(arguments = ".")

# Test importing all variables:
test.write("SConstruct", """
x = 'x'
y = 'zoom'
Export('x')
SConscript('SConscript', 'y')
""")

test.write("SConscript", """
Import('*')
assert x == 'x'
assert y == 'zoom'
""")

test.run(arguments = ".")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
