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
Make sure, that the examples given in user guide all work.
"""

import TestSCons
import os

test = TestSCons.TestSCons()

test.write('SConstruct',
"""
env = Environment( tools = ['default', 'xgettext'] )
env['POTDOMAIN'] = "foo"
env.POTUpdate(source = ["a.cpp", "b.cpp"]) # Creates foo.pot ...
env.POTUpdate(POTDOMAIN = "bar", source = ["c.cpp", "d.cpp"]) # and bar.pot
""")
test.write('a.cpp', """ gettext("Hello from a.cpp") """)
test.write('b.cpp', """ gettext("Hello from b.cpp") """)
test.write('c.cpp', """ gettext("Hello from c.cpp") """)
test.write('d.cpp', """ gettext("Hello from d.cpp") """)

test.run(arguments = 'pot-update')

test.must_exist('foo.pot')
test.must_contain('foo.pot', "Hello from a.cpp")
test.must_contain('foo.pot', "Hello from b.cpp")
test.must_not_contain('foo.pot', "Hello from c.cpp")
test.must_not_contain('foo.pot', "Hello from d.cpp")

test.must_exist('bar.pot')
test.must_not_contain('bar.pot', "Hello from a.cpp")
test.must_not_contain('bar.pot', "Hello from b.cpp")
test.must_contain('bar.pot', "Hello from c.cpp")
test.must_contain('bar.pot', "Hello from d.cpp")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
