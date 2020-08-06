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
Test that the $ZIPCOMSTR construction variable allows you to customize
the displayed string when zip is called.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

test.write('SConstruct', """
env = Environment(tools=['zip'],
                  ZIPCOM = r'%(_python_)s mycompile.py zip $TARGET $SOURCES',
                  ZIPCOMSTR = 'Zipping $TARGET from $SOURCE')
env.Zip('aaa.zip', 'aaa.in')

# Issue explained in PR #3569 - setting ZIPCOM/ZIPCOMSTR after env initialization
# is ignored and yields zip() instead of desired ZIPCOMSTR>
env2 = Environment(tools=['zip'])
env2['ZIPCOM'] = r'%(_python_)s mycompile.py zip $TARGET $SOURCES'
env2['ZIPCOMSTR']="TESTING ONE TWO THREE $TARGET from $SOURCE"
env2.Zip('aaa2.zip', 'aaa.in')

""" % locals())

test.write('aaa.in', 'aaa.in\n/*zip*/\n')

test.run(stdout = test.wrap_stdout("""\
Zipping aaa.zip from aaa.in
TESTING ONE TWO THREE aaa2.zip from aaa.in
"""))

test.must_match('aaa.zip', "aaa.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
