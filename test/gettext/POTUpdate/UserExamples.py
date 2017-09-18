2#!/usr/bin/env python
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
End-to-end tests for POTUpdate. Assure, that the examples from user's
documentation all work.
"""

import TestSCons
from os import path

test = TestSCons.TestSCons()

if not test.where_is('xgettext'):
    test.skip_test("Could not find 'xgettext', skipping test(s).\n")

#############################################################################
# POTUpdate: Example 1
#############################################################################
test.subdir(['ex1'])
test.subdir(['ex1', 'po'])
test.write( ['ex1', 'po', 'SConstruct' ],
"""
env = Environment( tools = ['default', 'xgettext'] )
env.POTUpdate(['foo'], ['../a.cpp', '../b.cpp'])
env.POTUpdate(['bar'], ['../c.cpp', '../d.cpp'])
""")
test.write(['ex1', 'a.cpp'], """ gettext("Hello from a.cpp") """)
test.write(['ex1', 'b.cpp'], """ gettext("Hello from b.cpp") """)
test.write(['ex1', 'c.cpp'], """ gettext("Hello from c.cpp") """)
test.write(['ex1', 'd.cpp'], """ gettext("Hello from d.cpp") """)

# scons '.' does not create foo.pot nor bar.pot
test.run(arguments = '.', chdir = path.join('ex1', 'po'))
test.must_not_exist(    ['ex1', 'po', 'foo.pot'] )
test.must_not_exist(    ['ex1', 'po', 'bar.pot'] )

# scons 'foo.pot' creates foo.pot
test.run(arguments = 'foo.pot', chdir = path.join('ex1', 'po'))
test.must_exist(        ['ex1', 'po', 'foo.pot'] )
test.must_not_exist(    ['ex1', 'po', 'bar.pot'] )
test.must_contain(      ['ex1', 'po', 'foo.pot'], "Hello from a.cpp", mode='r')
test.must_contain(      ['ex1', 'po', 'foo.pot'], "Hello from b.cpp", mode='r')
test.must_not_contain(  ['ex1', 'po', 'foo.pot'], "Hello from c.cpp", mode='r')
test.must_not_contain(  ['ex1', 'po', 'foo.pot'], "Hello from d.cpp", mode='r')

# scons 'pot-update' creates foo.pot and bar.pot
test.run(arguments = 'pot-update', chdir = path.join('ex1', 'po'))
test.must_exist(        ['ex1', 'po', 'foo.pot'] )
test.must_exist(        ['ex1', 'po', 'bar.pot'] )
test.must_not_contain(  ['ex1', 'po', 'bar.pot'], "Hello from a.cpp", mode='r')
test.must_not_contain(  ['ex1', 'po', 'bar.pot'], "Hello from b.cpp", mode='r')
test.must_contain(      ['ex1', 'po', 'bar.pot'], "Hello from c.cpp", mode='r')
test.must_contain(      ['ex1', 'po', 'bar.pot'], "Hello from d.cpp", mode='r')

# scons -c does not clean anything
test.run(arguments = '-c', chdir = path.join('ex1', 'po'))
test.must_exist(        ['ex1', 'po', 'foo.pot'] )
test.must_exist(        ['ex1', 'po', 'bar.pot'] )


#############################################################################
# POTUpdate: Example 2
#############################################################################
test.subdir(['ex2'])
test.write( ['ex2', 'SConstruct'],
"""
env = Environment( tools = ['default', 'xgettext'] )
env['POTDOMAIN'] = "foo"
env.POTUpdate(source = ["a.cpp", "b.cpp"]) # Creates foo.pot ...
env.POTUpdate(POTDOMAIN = "bar", source = ["c.cpp", "d.cpp"]) # and bar.pot
""")
test.write(['ex2', 'a.cpp'], """ gettext("Hello from a.cpp") """)
test.write(['ex2', 'b.cpp'], """ gettext("Hello from b.cpp") """)
test.write(['ex2', 'c.cpp'], """ gettext("Hello from c.cpp") """)
test.write(['ex2', 'd.cpp'], """ gettext("Hello from d.cpp") """)

test.run(arguments = 'pot-update', chdir = path.join('ex2'))

test.must_exist(        ['ex2', 'foo.pot'])
test.must_contain(      ['ex2', 'foo.pot'], "Hello from a.cpp", mode='r' )
test.must_contain(      ['ex2', 'foo.pot'], "Hello from b.cpp", mode='r' )
test.must_not_contain(  ['ex2', 'foo.pot'], "Hello from c.cpp", mode='r' )
test.must_not_contain(  ['ex2', 'foo.pot'], "Hello from d.cpp", mode='r' )

test.must_exist(        ['ex2', 'bar.pot'])
test.must_not_contain(  ['ex2', 'bar.pot'], "Hello from a.cpp", mode='r' )
test.must_not_contain(  ['ex2', 'bar.pot'], "Hello from b.cpp", mode='r' )
test.must_contain(      ['ex2', 'bar.pot'], "Hello from c.cpp", mode='r' )
test.must_contain(      ['ex2', 'bar.pot'], "Hello from d.cpp", mode='r' )


#############################################################################
# POTUpdate: Example 3
#############################################################################
test.subdir(['ex3'])
test.subdir(['ex3', 'po'])
test.write( ['ex3', 'po', 'SConstruct'],
"""
# SConstruct file in 'po/' subdirectory
env = Environment( tools = ['default', 'xgettext'] )
env.POTUpdate(XGETTEXTFROM = 'POTFILES.in')
""")
test.write( ['ex3', 'po', 'POTFILES.in'],
"""
# POTFILES.in in 'po/' subdirectory
../a.cpp
../b.cpp
# end of file
""")
test.write(['ex3', 'a.cpp'], """ gettext("Hello from a.cpp") """)
test.write(['ex3', 'b.cpp'], """ gettext("Hello from b.cpp") """)

# scons 'pot-update' creates messages.pot
test.run(arguments = 'pot-update', chdir = path.join('ex3', 'po'))
test.must_exist(['ex3', 'po', 'messages.pot'])


#############################################################################
# POTUpdate: Example 4
#############################################################################
test.subdir(['ex4'])
test.subdir(['ex4', 'po'])
test.write( ['ex4', 'po', 'SConstruct'],
"""
# SConstruct file in 'po/' subdirectory
env = Environment( tools = ['default', 'xgettext'] )
env.POTUpdate(XGETTEXTFROM = 'POTFILES.in', XGETTEXTPATH='../')
""")
test.write(['ex4', 'po', 'POTFILES.in'],
"""
# POTFILES.in in 'po/' subdirectory
a.cpp
b.cpp
# end of file
""")
test.write(['ex4', 'a.cpp'], """ gettext("Hello from a.cpp") """)
test.write(['ex4', 'b.cpp'], """ gettext("Hello from b.cpp") """)

# scons 'pot-update' creates messages.pot
test.run(arguments = 'pot-update', chdir = path.join('ex4', 'po'))
test.must_exist(['ex4', 'po', 'messages.pot'])



#############################################################################
# POTUpdate: Example 5
#############################################################################
test.subdir(['ex5'])
test.subdir(['ex5', '0'])
test.subdir(['ex5', '0','1'])
test.subdir(['ex5', '0', '1', 'po'])
test.write( ['ex5', '0', '1', 'po', 'SConstruct'],
"""
# SConstruct file in '0/1/po/' subdirectory
env = Environment( tools = ['default', 'xgettext'] )
env.POTUpdate(XGETTEXTFROM = 'POTFILES.in', XGETTEXTPATH=['../', '../../'])
""")
test.write( ['ex5', '0', '1', 'po', 'POTFILES.in'],
"""
# POTFILES.in in '0/1/po/' subdirectory
a.cpp
# end of file
""")
test.write(['ex5', '0', 'a.cpp'], """ gettext("Hello from ../../a.cpp") """)
test.write(['ex5', '0', '1', 'a.cpp'], """ gettext("Hello from ../a.cpp") """)

# scons 'pot-update' creates messages.pot
test.run(arguments = 'pot-update', chdir = path.join('ex5', '0', '1', 'po'))
test.must_exist(        ['ex5', '0', '1', 'po', 'messages.pot'])
test.must_contain(      ['ex5', '0', '1', 'po', 'messages.pot'], 
                        'Hello from ../a.cpp', mode='r' )
test.must_not_contain(  ['ex5', '0', '1', 'po', 'messages.pot'], 
                        'Hello from ../../a.cpp', mode='r' )

test.write(['ex5', '0', '1', 'po', 'SConstruct'],
"""
# SConstruct file in '0/1/po/' subdirectory
env = Environment( tools = ['default', 'xgettext'] )
env.POTUpdate(XGETTEXTFROM = 'POTFILES.in', XGETTEXTPATH=['../../', '../'])
""")
test.run(arguments = 'pot-update', chdir = path.join('ex5', '0', '1', 'po'))
test.must_contain(      ['ex5', '0', '1', 'po', 'messages.pot'],
                        'Hello from ../../a.cpp', mode='r' )
test.must_not_contain(  ['ex5', '0', '1', 'po', 'messages.pot'],
                        'Hello from ../a.cpp', mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
