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
Verify expected behavior when an implicit dependency is modified
asynchronously (that is, mid-build and without our knowledge).

Test case courtesy Greg Noel.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write(['SConstruct'], """\
import SCons.Defaults
DefaultEnvironment(tools=[])
env = Environment(tools=[]) 
env['BUILDERS']['C'] = Builder(action = Copy('$TARGET', '$SOURCE'),
                               source_scanner = SCons.Defaults.CScan)
env['BUILDERS']['Mod'] = Builder(action = r'%(_python_)s mod.py')
Alias('seq', env.C('one.c'))
Alias('seq', env.Mod('mod', 'mod.py'))
Alias('seq', env.C('two.c'))
Default('seq')
""" % locals())

test.write(['hdr.h'], """\
/* empty header */
""")

test.write(['mod.py'], """\
with open('mod', 'w') as f, open('mod.py', 'r') as ifp:
    f.write(ifp.read())
with open('hdr.h', 'w') as f:
    f.write("/* modified */\\n")
""")

test.write(['one.c'], """\
#include "hdr.h"
""")

test.write(['two.c'], """\
#include "hdr.h"
""")

# The first run builds the file 'one', then runs the 'mod' script
# (which update modifies the 'hdr.h' file) then builds the file 'two'.
test.run(arguments = 'seq')

# The 'hdr.h' file had its original contents when 'one' was built,
# and modified contents when 'two' was built.  Because we took a
# look at 'hdr.h' once, up front, we think both files are out of
# date and will rebuild both (even though 'two' is really up to date).
#
# A future enhancement might add some sort of verification mode that
# would examine 'hdr.h' again when 'two' was built, thereby avoiding
# the unnecessary rebuild.  In that case, the second line below
# will need to change to "test.up_to_date(...)".
test.not_up_to_date(arguments = 'one')
test.not_up_to_date(arguments = 'two')

# Regardless of what happened on the middle run(s), both files should
# be up to date now.
test.up_to_date(arguments = 'seq')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
