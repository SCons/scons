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

test.subdir('sub1', 'sub2')

test.write(['sub1', 'foo.py'], """
variable = "sub1/foo"
""")

test.write(['sub2', 'foo.py'], """
variable = "sub2/foo"
""")

test.write(['sub2', 'bar.py'], """
variable = "sub2/bar"
""")

test.write('SConstruct', """
import foo
print(foo.variable)
import bar
print(bar.variable)
""")

test.run(arguments = '-I sub1 -I sub2 .',
         stdout = test.wrap_stdout(read_str = 'sub1/foo\nsub2/bar\n',
                                   build_str = "scons: `.' is up to date.\n"))

test.run(arguments = '--include-dir=sub2 --include-dir=sub1 .',
         stdout = test.wrap_stdout(read_str = 'sub2/foo\nsub2/bar\n',
                                   build_str = "scons: `.' is up to date.\n"))

test.pass_test()
 

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
