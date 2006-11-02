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

import os
import string
import sys
import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()



test.write('myrpcgen.py', """
import getopt
import string
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'chlmo:x', [])
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
output.write(string.join(sys.argv) + "\\n")
for a in args:
    contents = open(a, 'rb').read()
    output.write(string.replace(contents, 'RPCGEN', 'myrpcgen.py'))
output.close()
sys.exit(0)
""")

test.write('SConstruct', """\
env = Environment(RPCGEN = r'%(_python_)s myrpcgen.py',
                  RPCGENXDRFLAGS = '-x',
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
output_xdr      = "myrpcgen.py %s -x -o %s rpcif.x\nmyrpcgen.py\n"

expect_clnt     = output     % ('-l', test.workpath('rpcif_clnt.c'))
expect_h        = output     % ('-h', test.workpath('rpcif.h'))
expect_svc      = output     % ('-m', test.workpath('rpcif_svc.c'))
expect_xdr      = output_xdr % ('-c', test.workpath('rpcif_xdr.c'))

test.must_match('rpcif_clnt.c', expect_clnt)
test.must_match('rpcif.h',      expect_h)
test.must_match('rpcif_svc.c',  expect_svc)
test.must_match('rpcif_xdr.c',  expect_xdr)



test.pass_test()
