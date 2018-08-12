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
Test the Execute() functions clears the memoized values of affected target Nodes
when used with Delete(). Derived from
https://github.com/SCons/scons/issues/1307
"""

import TestSCons
import os.path

test = TestSCons.TestSCons()

subfn = os.path.join('sub', 'foo')

test.write('SConstruct', """\
def exists(node):
    if node.exists():
        print(str(node)+" exists")
    else:
        print(str(node)+" does not exist")

Execute(Delete('abc'))
n1 = File('abc')
exists( n1 )
Execute(Touch('abc'))
exists( n1 )
Execute(Delete('abc'))
exists( n1 )

env = Environment()
env.Execute(Delete('def'))
n2 = env.File('def')
exists( n2 )
env.Execute(Touch('def'))
exists( n2 )
env.Execute(Delete(n2))
exists( n2 )

Execute(Touch('abc'))
exists( n1 )
Execute(Move('def', 'abc'))
exists( n1 )
exists( n2 )

Execute(Copy('abc', 'def'))
exists( n1 )

n3 = File(r"%(subfn)s")
exists( n3 )
Execute(Mkdir('sub'))
Execute(Touch(r"%(subfn)s"))
exists( n3 )
""" % locals())


expect = test.wrap_stdout(read_str="""\
Delete("abc")
abc does not exist
Touch("abc")
abc exists
Delete("abc")
abc does not exist
Delete("def")
def does not exist
Touch("def")
def exists
Delete("def")
def does not exist
Touch("abc")
abc exists
Move("def", "abc")
abc does not exist
def exists
Copy("abc", "def")
abc exists
%(subfn)s does not exist
Mkdir("sub")
Touch("%(subfn)s")
%(subfn)s exists
""" % locals(), build_str = "scons: `.' is up to date.\n")

test.run(arguments = '.', stdout = expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
