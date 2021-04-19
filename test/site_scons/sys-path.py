#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Verify that the site_scons dir is added to sys.path as an
absolute path, so it will work from a subdir.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('site_scons')
test.subdir('sub1')

test.write(['site_scons', 'testmod1.py'], """
print("Imported site_scons/testmod1.py.")
""")
test.write(['site_scons', 'testmod2.py'], """
print("Imported site_scons/testmod2.py.")
""")

test.write(['sub1', 'SConscript'], """
import testmod2 # This call did not work before the fix

""")

test.write('SConstruct', """
import testmod1 # this always worked
SConscript('sub1/SConscript')
""")

test.run(arguments = '-Q .',
         stdout = """Imported site_scons/testmod1.py.
Imported site_scons/testmod2.py.
scons: `.' is up to date.\n""")

test.pass_test()

# end of file

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
