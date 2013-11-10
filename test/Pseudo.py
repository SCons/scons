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

test = TestSCons.TestSCons()

# Firstly, build a pseudo target and make sure we get no warnings it
# doesn't exist under any circumstances
test.write('SConstruct', """
env = Environment()
env.Pseudo(env.Command('foo.out', [], '@echo boo'))
""")

test.run(arguments='-Q', stdout = 'boo\n')

test.run(arguments='-Q --warning=target-not-built', stdout = "boo\n")

# Now do the same thing again but create the target and check we get an
# error if it exists after the build
test.write('SConstruct', """
env = Environment()
env.Pseudo(env.Command('foo.out', [], Touch('$TARGET')))
""")

test.run(arguments='-Q', stdout = 'Touch("foo.out")\n', stderr = None,
         status = 2)
test.must_contain_all_lines(test.stderr(),
                            'scons:  *** Pseudo target foo.out must not exist')
test.run(arguments='-Q --warning=target-not-built',
         stdout = 'Touch("foo.out")\n',
         stderr = None, status = 2)
test.must_contain_all_lines(test.stderr(),
                            'scons:  *** Pseudo target foo.out must not exist')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
