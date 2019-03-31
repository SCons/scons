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
Verify that the sconsign script generates appropriate error messages when
passed various non-existent or bad sconsign files as arguments.
"""

import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

test.write('bad1', "bad1\n")
test.write('bad2.dblite', "bad2.dblite\n")
test.write('bad3', "bad3\n")

test.run_sconsign(arguments = "-f dblite no_sconsign",
         stderr = "sconsign: \\[Errno 2\\] No such file or directory: 'no_sconsign'\n")

test.run_sconsign(arguments = "-f dblite bad1",
         stderr = "sconsign: \\[Errno 2\\] No such file or directory: 'bad1.dblite'\n")

test.run_sconsign(arguments = "-f dblite bad1.dblite",
         stderr = "sconsign: \\[Errno 2\\] No such file or directory: 'bad1.dblite'\n")

test.run_sconsign(arguments = "-f dblite bad2",
         stderr = "sconsign: ignoring invalid `dblite' file `bad2'.*\n")

test.run_sconsign(arguments = "-f dblite bad2.dblite",
         stderr = "sconsign: ignoring invalid `dblite' file `bad2.dblite'.*\n")

test.run_sconsign(arguments = "-f sconsign no_sconsign",
         stderr = "sconsign: \\[Errno 2\\] No such file or directory: 'no_sconsign'\n")

test.run_sconsign(arguments = "-f sconsign bad3",
         stderr = "sconsign: ignoring invalid .sconsign file `bad3'.*\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
