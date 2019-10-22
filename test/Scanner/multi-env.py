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
Verifies that using the same source file in different environments
will get the proper scanner for the environment being used.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()


test.write('SConstruct', r"""
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)
input_re = re.compile(r'^input\s+(\S+)$', re.M)

scan1 = Scanner(name = 'Include',
                function = lambda N,E,P,A: A.findall(N.get_text_contents()),
                argument = include_re,
                skeys = ['.inp'])

scan2 = Scanner(name = 'Input',
                function = lambda N,E,P,A: A.findall(N.get_text_contents()),
                argument = input_re,
                skeys = ['.inp'])

env1 = Environment()
env2 = Environment()

env1.Append(SCANNERS=scan1)
env2.Append(SCANNERS=scan2)

env1.Command('frog.1', 'frog.inp', r'%(_python_)s do_incl.py $TARGET $SOURCES')
env2.Command('frog.2', 'frog.inp', r'%(_python_)s do_inp.py $TARGET $SOURCES')

""" % locals())

process = r"""
import sys

def process(infp, outfp):
    prefix = '%(command)s '
    l = len(prefix)
    for line in infp.readlines():
        if line[:l] == prefix:
            with open(line[l:-1], 'r') as f:
                process(f, outfp)
        else:
            outfp.write(line)

with open(sys.argv[2], 'r') as ifp, open(sys.argv[1], 'w') as ofp:
    process(ifp, ofp)
sys.exit(0)
"""

test.write('do_incl.py', process % { 'command' : 'include' })
test.write('do_inp.py', process % { 'command' : 'input' })

test.write('frog.inp', """\
include sound1
input sound2
""")

test.write('sound1', 'croak\n')
test.write('sound2', 'ribbet\n')

expect = test.wrap_stdout("""\
%(_python_)s do_incl.py frog.1 frog.inp
%(_python_)s do_inp.py frog.2 frog.inp
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('frog.1', 'croak\ninput sound2\n', mode='r')
test.must_match('frog.2', 'include sound1\nribbet\n', mode='r')

test.write('sound2', 'rudeep\n')

expect = test.wrap_stdout("""\
%(_python_)s do_inp.py frog.2 frog.inp
""" % locals())

test.run(arguments='.', stdout=expect)

test.must_match('frog.1', 'croak\ninput sound2\n', mode='r')
test.must_match('frog.2', 'include sound1\nrudeep\n', mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
