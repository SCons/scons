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
Test the ability to configure the $MIDLCOM construction variable.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mymidl.py', """
import os.path
import sys
base = os.path.splitext(sys.argv[1])[0]
with open(sys.argv[1], 'w') as out_tlb, open(base + '.h', 'w') as out_h, open(base + '_i.c', 'w') as out_c:
    for f in sys.argv[2:]:
        with open(f, 'r') as ifp:
            for l in [l for l in ifp.readlines() if l != '/*midl*/\\n']:
                out_tlb.write(l)
                out_h.write(l)
                out_c.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools=['default', 'midl'],
                  MIDLCOM = r'%(_python_)s mymidl.py $TARGET $SOURCES')
env.TypeLibrary(target = 'aaa', source = 'aaa.idl')
""" % locals())

test.write('aaa.idl', "aaa.idl\n/*midl*/\n")

test.run(arguments = '.')

test.must_match('aaa.tlb', "aaa.idl\n", mode='r')
test.must_match('aaa.h', "aaa.idl\n", mode='r')
test.must_match('aaa_i.c', "aaa.idl\n", mode='r')

test.up_to_date(options = '--debug=explain', arguments = 'aaa.tlb')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
