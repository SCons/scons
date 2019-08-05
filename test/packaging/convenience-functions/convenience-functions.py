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
Test the FindInstalledFiles() and the FindSourceFiles() functions.
"""

import os.path
import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture("image")

bin_f1 = os.path.join('bin', 'f1')
bin_f2 = os.path.join('bin', 'f2')

bin__f1 = bin_f1.replace('\\', '\\\\')
bin__f2 = bin_f2.replace('\\', '\\\\')

expect_read = """\
['SConstruct', 'f1', 'f2', 'f3']
['%(bin__f1)s', '%(bin__f2)s']
""" % locals()

expect_build = """\
Install file: "f1" as "%(bin_f1)s"
Install file: "f2" as "%(bin_f2)s"
""" % locals()

expected = test.wrap_stdout(read_str = expect_read, build_str = expect_build)

test.run(stdout=expected)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
