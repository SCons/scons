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
Ensure that projects with multiple translation catalogs maintain translation
files correctly. 
"""

# There was a bug that affected the `Translate()` when no targets were provided
# explicitelly via argument list. If, for exapmle, `pkg1/SConscript` and 
# `pkg2/SConscript` scripts in some project `p1` had:
#
#       Translate(LINGUAS_FILE = 1)
#
# then target languages defined in `pkg1/LINGUAS` would affect the list of
# target languages emitted by `pkg2/SConscript` and vice versa.
#
# The pull request #64 on bitbucket fixes this. Here is the test case to
# replicate the bug.

import TestSCons
from os import path

test = TestSCons.TestSCons()

if not test.where_is('xgettext'):
    test.skip_test("could not find 'xgettext'; skipping test(s)\n")
if not test.where_is('msgmerge'):
    test.skip_test("Could not find 'msgmerge'; skipping test(s)\n")
if not test.where_is('msginit'):
    test.skip_test("could not find 'msginit'; skipping test(s)\n")
if not test.where_is('msgfmt'):
    test.skip_test("could not find 'msgfmt'; skipping test(s)\n")

#############################################################################
# Test case 1
#############################################################################
test.subdir(['tc1'])
test.write( ['tc1', 'SConstruct'],
"""
env = Environment( tools = ["default", "gettext"] )
env.Replace(POAUTOINIT = 1)
env.Replace(LINGUAS_FILE = 1)
SConscript(["pkg1/SConscript", "pkg2/SConscript"], exports = ["env"])
""")


# package `pkg1`
test.subdir(['tc1', 'pkg1'])
test.write( ['tc1', 'pkg1', 'LINGUAS'],
"""
en
pl
""")
test.write( ['tc1', 'pkg1', 'SConscript'],
"""
Import("env")
env.Translate(source = ['a.cpp'])
""")
test.write(['tc1', 'pkg1', 'a.cpp'], """ gettext("Hello from pkg1/a.cpp") """ )

# package `pkg2`
test.subdir(['tc1', 'pkg2'])
test.write( ['tc1', 'pkg2', 'LINGUAS'],
"""
de
fr
""")
test.write( ['tc1', 'pkg2', 'SConscript'],
"""
Import("env")
env.Translate(source = ['b.cpp'])
""")
test.write(['tc1', 'pkg2', 'b.cpp'], """ gettext("Hello from pkg2/b.cpp") """ )


# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'tc1', stderr = None)
test.must_exist(    ['tc1', 'pkg1', 'en.po'] )
test.must_exist(    ['tc1', 'pkg1', 'pl.po'] )
test.must_not_exist(['tc1', 'pkg1', 'de.po'] )
test.must_not_exist(['tc1', 'pkg1', 'fr.po'] )
test.must_exist(    ['tc1', 'pkg2', 'de.po'] )
test.must_exist(    ['tc1', 'pkg2', 'fr.po'] )
test.must_not_exist(['tc1', 'pkg2', 'en.po'] )
test.must_not_exist(['tc1', 'pkg2', 'pl.po'] )


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
