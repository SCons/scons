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
Verify that explicit use of File() Nodes in a VariantDir, followed by
*direct* creation of the file by Python in the SConscript file itself,
works correctly, with both duplicate=0 and duplicate=1.

Right now it only works if you explicitly str() the Node before the file
is created on disk, but we at least want to make sure that continues
to work.  The non-str() case, which doesn't currently work, is captured
here but commented out.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src')

test.write('SConstruct', """\
SConscript('src/SConscript', variant_dir='build0', chdir=1, duplicate=0)
SConscript('src/SConscript', variant_dir='build1', chdir=1, duplicate=1)
""")

test.write(['src', 'SConscript'], """\
#f1_in = File('f1.in')
#Command('f1.out', f1_in, Copy('$TARGET', '$SOURCE'))
#with open('f1.in', 'w') as f:
#    f.write("f1.in\\n")

f2_in = File('f2.in')
str(f2_in)
Command('f2.out', f2_in, Copy('$TARGET', '$SOURCE'))
with open('f2.in', 'w') as f:
    f.write("f2.in\\n")
""")

test.run(arguments = '--tree=all .')

#test.must_match(['build0', 'f1.out'], "f1.in\n")
test.must_match(['build0', 'f2.out'], "f2.in\n", mode='r')

#test.must_match(['build1', 'f1.out'], "f1.in\n")
test.must_match(['build1', 'f2.out'], "f2.in\n", mode='r')

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
