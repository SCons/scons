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
Test how we handle #includes of dangling symlinks.
"""


import TestSCons

test = TestSCons.TestSCons()

if not test.platform_has_symlink():
    test.skip_test('No os.symlink() method, no symlinks to test.\n')

foo_obj = 'foo' + TestSCons._obj

test.write('SConstruct', """
Program('foo.c')
""")

test.write('foo.c', """\
#include "foo.h"
""")

test.symlink('nonexistent', 'foo.h')

expect = """\
scons: \\*\\*\\* \\[foo.o(bj)?\\] Implicit dependency `foo.h' not found, needed by target `%s'.(  Stop.)?
"""% foo_obj

test.run(arguments = '.', status = 2, stderr = expect, 
         match=TestSCons.match_re_dotall)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
