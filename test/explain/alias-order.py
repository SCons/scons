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
Verify a lot of the basic operation of the --debug=explain option.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

args = '--debug=explain target2.dat'

test.subdir('src')
test.write(['src', 'SConstruct'],"""
DefaultEnvironment(tools=[])
env = Environment(tools=[])

def action( source, target, env ):
    f = open( str(target[0]), 'wb' )
    f.write( source[0].get_contents())
    f.close()

builder = env.Builder( action=action )

builder( env, target = "target1.dat", source = "source1.dat" )
alias = env.Alias( "alias", "source2.dat" )
builder( env, target = "target2.dat", source = ["target1.dat"] )
env.Depends( "target2.dat", alias )
"""
)

test.write(["src", "source1.dat"], "a" )
test.write(["src", "source2.dat"], "a" )

expect = test.wrap_stdout("""\
scons: building `target1.dat' because it doesn't exist
action(["target1.dat"], ["source1.dat"])
scons: building `target2.dat' because it doesn't exist
action(["target2.dat"], ["target1.dat"])
""")

test.run(chdir='src', arguments=args, stdout=expect)

test.write(["src", "source1.dat"], "b" )

expect = test.wrap_stdout("""\
scons: rebuilding `target1.dat' because `source1.dat' changed
action(["target1.dat"], ["source1.dat"])
scons: rebuilding `target2.dat' because `target1.dat' changed
action(["target2.dat"], ["target1.dat"])
""")

test.run(chdir='src', arguments=args, stdout=expect)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
