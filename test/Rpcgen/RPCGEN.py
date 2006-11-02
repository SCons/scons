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
cmd_opts, args = getopt.getopt(sys.argv[1:], 'chlmo:', [])
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

output = "myrpcgen.py %s -o %s rpcif.x\nmyrpcgen.py\n"
expect_clnt = output % ('-l', test.workpath('rpcif_clnt.c'))
expect_h = output % ('-h', test.workpath('rpcif.h'))
expect_svc = output % ('-m', test.workpath('rpcif_svc.c'))
expect_xdr = output % ('-c', test.workpath('rpcif_xdr.c'))

test.must_match('rpcif_clnt.c', expect_clnt)
test.must_match('rpcif.h', expect_h)
test.must_match('rpcif_svc.c', expect_svc)
test.must_match('rpcif_xdr.c', expect_xdr)



rpcgen = test.where_is('rpcgen')
if rpcgen:

    test.subdir('do_rpcgen')

    test.write('SConstruct', """\
import os
env = Environment(ENV=os.environ)
env.Program('rpcclnt', ['rpcclnt.c', 'do_rpcgen/rpcif_clnt.c'])
env.RPCGenHeader('do_rpcgen/rpcif')
env.RPCGenClient('do_rpcgen/rpcif')
env.RPCGenService('do_rpcgen/rpcif')
env.RPCGenXDR('do_rpcgen/rpcif')
""")

    test.write(['do_rpcgen', 'rpcif.x'], """\
program RPCTEST_IF
{
  version RPCTEST_IF_VERSION
  {
    int START(unsigned long) = 1;
    int STOP(unsigned long) = 2;
    int STATUS(unsigned long) = 3;
  } = 1; /* version */
} = 0xfeedf00d; /* portmap program ID */
""")

# Following test tries to make sure it can compile and link, but when
# it's run it doesn't actually invoke any rpc operations because that
# would have significant dependencies on network configuration,
# portmapper, etc. that aren't necessarily appropriate for an scons
# test.

    test.write('rpcclnt.c', """\
#include <rpc/rpc.h>
#include <rpc/pmap_clnt.h>
#include "do_rpcgen/rpcif.h"

int main(int argc, char **args) {
  const char* const SERVER = "localhost";
  CLIENT *cl;
  int *rslt;
  unsigned long arg = 0;
  if (argc > 2) {
    cl = clnt_create( SERVER, RPCTEST_IF, RPCTEST_IF_VERSION, "udp" );
    if (cl == 0 ) { return 1; }
    rslt = start_1(&arg, cl);
    if (*rslt == 0) { clnt_perror( cl, SERVER ); return 1; }
    clnt_destroy(cl);
  } else
    printf("Hello!\\n");
  return 0;
}
""")


    test.run()

    test.run(program=test.workpath('rpcclnt'+_exe))

    test.fail_test(not test.stdout() in ["Hello!\n", "Hello!\r\n"])



test.pass_test()
