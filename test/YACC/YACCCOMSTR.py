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
Test that the $YACCCOMSTR construction variable allows you to customize
the displayed string when yacc is called.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

test.write('SConstruct', """
env = Environment(tools=['default', 'yacc'],
                  YACCCOM = r'%(_python_)s mycompile.py yacc $TARGET $SOURCES',
                  YACCCOMSTR = 'Yaccing $TARGET from $SOURCE')
env.CFile(target = 'aaa', source = 'aaa.y')
env.CFile(target = 'bbb', source = 'bbb.yacc')
""" % locals())

test.write('aaa.y', 'aaa.y\n/*yacc*/\n')
test.write('bbb.yacc', 'bbb.yacc\n/*yacc*/\n')

test.run(stdout = test.wrap_stdout("""\
Yaccing aaa.c from aaa.y
Yaccing bbb.c from bbb.yacc
"""))

test.must_match('aaa.c', "aaa.y\n")
test.must_match('bbb.c', "bbb.yacc\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
