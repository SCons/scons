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

import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()



test.write('myrpcgen.py', """
import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'chlmo:x', [])
for opt, arg in cmd_opts:
    if opt == '-o': out = arg
with open(out, 'w') as ofp:
    ofp.write(" ".join(sys.argv) + "\\n")
    for a in args:
        with open(a, 'r') as ifp:
            contents = ifp.read()
        ofp.write(contents.replace('RPCGEN', 'myrpcgen.py'))
sys.exit(0)
""")

test.write('SConstruct', """\
env = Environment(RPCGEN = r'%(_python_)s myrpcgen.py',
                  RPCGENHEADERFLAGS = '-x',
                  tools=['default', 'rpcgen'])
env.RPCGenHeader('rpcif')
env.RPCGenClient('rpcif')
env.RPCGenService('rpcif')
env.RPCGenXDR('rpcif')
""" % locals())

test.write('rpcif.x', """\
RPCGEN
""")

test.run()

output          = "myrpcgen.py %s -o %s rpcif.x\nmyrpcgen.py\n"
output_h        = "myrpcgen.py %s -x -o %s rpcif.x\nmyrpcgen.py\n"

expect_clnt     = output   % ('-l', test.workpath('rpcif_clnt.c'))
expect_h        = output_h % ('-h', test.workpath('rpcif.h'))
expect_svc      = output   % ('-m', test.workpath('rpcif_svc.c'))
expect_xdr      = output   % ('-c', test.workpath('rpcif_xdr.c'))

test.must_contain('rpcif_clnt.c', expect_clnt, mode='r')
test.must_contain('rpcif.h',      expect_h, mode='r')
test.must_contain('rpcif_svc.c',  expect_svc, mode='r')
test.must_contain('rpcif_xdr.c',  expect_xdr, mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
