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
Verify that the swig tool generates file names that we expect.
"""

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj

test = TestSCons.TestSCons()

_python_ = TestSCons._python_

test.write('myswig.py', """\
import getopt
import sys

opts, args = getopt.getopt(sys.argv[1:], "c:o:v:")
for opt, arg in opts:
    if opt == "-c":
        pass
    elif opt == "-o":
        out = arg
    elif opt == "-v" and arg == "ersion":
        print("")
        print("SWIG Version 0.1.2")
        print("")
        print("Compiled with g++ [x86_64-pc-linux-gnu]")
        print("")
        print("Configured options: +pcre")
        print("")
        print("Please see http://www.swig.org for reporting bugs "
              "and further information")
        sys.exit(0)

with open(args[0], "r") as ifp, open(out, "w") as ofp:
    for line in ifp:
        if not line.startswith("swig"):
            ofp.write(line)
sys.exit(0)
""")

test.write('SConstruct', """\
env = Environment(tools=["default", "swig"], SWIG=[r"%(_python_)s", "myswig.py"])
print(env.subst("Using SWIG $SWIGVERSION"))
env.Program(target="test1", source="test1.i")
env.CFile(target="test2", source="test2.i")
env.Clone(SWIGFLAGS="-c++").Program(target="test3", source="test3.i")
""" % locals())

test.write('test1.i', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[]) {
        argv[argc++] = "--";
        printf("test1.i\n");
        exit (0);
}
swig
""")

test.write('test2.i', r"""test2.i
swig
""")

test.write('test3.i', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[]) {
        argv[argc++] = "--";
        printf("test3.i\n");
        exit (0);
}
swig
""")

test.run(arguments='.', stderr=None, stdout=r'.*Using SWIG 0.1.2.*',
         match=TestSCons.match_re_dotall)

test.run(program=test.workpath('test1' + _exe), stdout="test1.i\n")
test.must_exist(test.workpath('test1_wrap.c'))
test.must_exist(test.workpath('test1_wrap' + _obj))

test.must_match('test2_wrap.c', "test2.i\n", mode='r')

test.run(program=test.workpath('test3' + _exe), stdout="test3.i\n")
test.must_exist(test.workpath('test3_wrap.cc'))
test.must_exist(test.workpath('test3_wrap' + _obj))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
