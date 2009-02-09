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
Verify that when a source file is generated and the -j option is used,
the source file correctly gets re-scanned for implicit dependencies
after it's built.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()
env['BUILDERS']['COPY'] = Builder(action = Copy("$TARGET", "$SOURCE"))

env.COPY('a.c', 'a.in')
env.COPY('b.c', 'b.in')

env.StaticLibrary('lib', ['a.c', 'b.c'])
""")

test.write("a.in", """\
#include "a.h"
""")

test.write("b.in", """\
#include "b.h"
""")

test.write("a.h", """\
char *A_FILE = "b.in";
""")

test.write("b.h", """\
char *B_FILE = "b.in";
""")

test.run(arguments = '-j4 .',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

# If the dependencies weren't re-scanned properly, the .h files won't
# show up in the previous run's dependency lists, and the .o files and
# library will get rebuilt here.
test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
