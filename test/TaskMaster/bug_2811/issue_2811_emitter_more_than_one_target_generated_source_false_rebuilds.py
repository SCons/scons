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
"""
This issue requires the following.
1. Generated source file which outputs 2 (or more) files
2. Action string gets scanned providing only compiler as part of implicit scan
3. Generated file gets built. Without the bugfix only the first target's .implicit list is cleared.
4. builder/executor/action gets tried again and implicits scanned. 2nd to Nth targets end up
   with the compiler at the beginning of the implicit list and the rest of the scanned files added to that list.
5. That bimplicit gets saved into sconsign
6. Second run loads sconsign, now with generated file present a regular implicit scan occurs. This yields 2nd through
   Nth target's implicit lists changing when compared to SConsign's which have been loaded.
7. This forces rebuild of source file and this propagates to massive recompile
"""
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()
test.dir_fixture('fixture_dir')

test.run()

# Should not rebuild
test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
