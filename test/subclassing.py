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
Verify that we can trivially subclass our "public" classes.  Also
verify that we can use a trivial subclass of new-style str classes
as well as UserString as Builder input.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
copy_action = Copy('$TARGET', '$SOURCE')

# Some day, we'd probably like people to be able to subclass Action and
# Builder, but that's going to take some serious class-hackery to turn
# our factory function into the class itself.
#class my_Action(Action):
#    pass
#class my_Builder(Builder):
#    pass
class my_Scanner(Scanner):
    pass
class my_Environment(Environment):
    pass
env = my_Environment()
env.Command('f0.out', 'f0.in', copy_action)

try:
    from collections import UserString
except ImportError:
    from UserString import UserString
try:
    class mystr(str):
        pass
except TypeError:
    class mystr(UserString):
        pass

Command(mystr('f1.out'),        mystr('f1.in'), copy_action)
Command(UserString('f2.out'),   UserString('f2.in'),    copy_action)

Install(mystr('install'),       mystr('f1.out'))
Install(mystr('install'),       UserString('f2.out'))
""")

test.write('f0.in', "f0.in\n")
test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")

test.run(arguments = '.')

test.must_match('f0.out',              "f0.in\n")
test.must_match(['install', 'f1.out'], "f1.in\n")
test.must_match(['install', 'f2.out'], "f2.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
