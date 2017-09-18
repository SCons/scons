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
Test that the $ASPPCOMSTR construction variable allows you to customize
the displayed assembler string.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

test.write('SConstruct', """
env = Environment(ASPPCOM = r'%(_python_)s mycompile.py as $TARGET $SOURCE',
                  ASPPCOMSTR = 'Assembling $TARGET from $SOURCE',
                  OBJSUFFIX = '.obj')
env.Object(target = 'test1', source = 'test1.spp')
env.Object(target = 'test2', source = 'test2.SPP')
""" % locals())

test.write('test1.spp', "test1.spp\n/*as*/\n")
test.write('test2.SPP', "test2.SPP\n/*as*/\n")

test.run(stdout = test.wrap_stdout("""\
Assembling test1.obj from test1.spp
Assembling test2.obj from test2.SPP
"""))

test.must_match('test1.obj', "test1.spp\n")
test.must_match('test2.obj', "test2.SPP\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
