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
Validate that $FORTRANMODDIR values get expanded correctly on Fortran
command lines relative to the appropriate subdirectory.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('subdir',
            ['subdir', 'src'],
            ['subdir', 'build'])

test.write('myfortran.py', r"""
import getopt
import os
import sys
comment = ('#' + sys.argv[1]).encode()
length = len(comment)
opts, args = getopt.getopt(sys.argv[2:], 'cM:o:')
for opt, arg in opts:
    if opt == '-o': out = arg
    elif opt == '-M': modsubdir = arg
import os
with open(out, 'wb') as ofp, open(args[0], 'rb') as ifp:
    for l in ifp.readlines():
        if l[:7] == b'module ':
            module = modsubdir + os.sep + l[7:-1].decode() + '.mod'
            with open(module, 'wb') as f:
                f.write(('myfortran.py wrote %s\n' % module).encode())
        if l[:length] != comment:
            ofp.write(l)
sys.exit(0)
""")

test.write('myar.py', """\
import sys
with open(sys.argv[1], 'wb') as ofp:
    for s in sys.argv[2:]:
        with open(s, 'rb') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""")

test.write('SConstruct', """\
env = Environment(FORTRANMODDIRPREFIX = '-M',
                  FORTRANMODDIR = 'modules',
                  FORTRAN = r'%(_python_)s myfortran.py fortran',
                  AR = 'myar.py',
                  ARCOM = r'%(_python_)s $AR $TARGET $SOURCES',
                  RANLIBCOM = '')
Export('env')
objs = SConscript('subdir/SConscript')
env.Library('bidule', objs)
""" % locals())

test.write(['subdir', 'SConscript'], """\
Import('env')

env['FORTRANMODDIR'] = 'build'
sources = ['src/modfile.f']
objs = env.Object(sources)
Return("objs")
""")

test.write(['subdir', 'src', 'modfile.f'], """\
#fortran comment
module somemodule

integer :: nothing

end module
""")


test.run(arguments = '.')

somemodule = os.path.join('subdir', 'build', 'somemodule.mod')

expect = "myfortran.py wrote %s\n" % somemodule

test.must_match(['subdir', 'build', 'somemodule.mod'], expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
