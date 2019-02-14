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
Test that $M4 and $M4FLAGS work as expected.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mym4.py', """
import sys
contents = sys.stdin.read()
sys.stdout.write(contents.replace('M4', 'mym4.py'))
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['m4'],
                  M4 = r'%(_python_)s mym4.py')
env.M4(target = 'aaa.x', source = 'aaa.x.m4')
""" % locals())

test.write('aaa.x.m4', """\
line 1
M4
line 3
""")

test.run()

test.must_match(test.workpath('aaa.x'), os.linesep.join(["line 1", "mym4.py", "line 3", ""]))

m4 = test.where_is('m4')

if not m4:
    test.skip_test('M4 not found found; skipping test.\n')

test.file_fixture('wrapper.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
foo = Environment(tools=['m4'],
                  M4=r'%(m4)s', M4FLAGS='-DFFF=fff')
m4 = foo.Dictionary('M4')
bar = Environment(tools=['m4'],
                  M4 = r'%(_python_)s wrapper.py ' + m4, M4FLAGS='-DBBB=bbb')
foo.M4(target = 'foo.x', source = 'foo.x.m4')
bar.M4(target = 'bar', source = 'bar.m4')
""" % locals())

test.write('foo.x.m4',  os.linesep.join(["line 1", "FFF", "line 3"]))

test.write('bar.m4', os.linesep.join(["line 1", "BBB", "line 3"]))

test.run(arguments = '.')
test.up_to_date(arguments = '.')

test.must_match('wrapper.out', "wrapper.py\n")

test.must_match('foo.x', os.linesep.join(["line 1", "fff", "line 3"]))

test.must_match('bar', os.linesep.join(["line 1", "bbb", "line 3"]))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
