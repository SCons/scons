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
Verify that we can call get_csig() from a function action without
causing problems.  (This messed up a lot of internal state before
the Big Signature Refactoring.)

Test case courtesy of Damyan Pepper.
"""

import TestSCons

test = TestSCons.TestSCons()

args = "--debug=explain"

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=[])

def action( source, target, env ):
    target[0].get_csig()
    f = open( str(target[0]), 'wb' )
    for s in source:
        f.write( s.get_contents() )
    f.close()

builder = env.Builder( action=action )

builder( env, target = "target.txt", source = "source.txt" )
""")

test.write("source.txt", "source.txt 1\n")

test.run(arguments=args)



test.write("source.txt", "source.txt 2")



expect_rebuild = test.wrap_stdout("""\
scons: rebuilding `target.txt' because `source.txt' changed
action(["target.txt"], ["source.txt"])
""")

test.not_up_to_date(arguments=args)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
