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
Verify use of an up-to-date Decider method through a construction
environment.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
import os.path
denv = Environment(tools=[])
env = Environment(tools=[])
n1_in = File('n1.in')
n2_in = File('n2.in')
n3_in = File('n3.in')
Command(     'ccc.out', 'ccc.in',   Copy('$TARGET', '$SOURCE'))
Command(     'n1.out',  n1_in,      Copy('$TARGET', '$SOURCE'))
denv.Command('ddd.out', 'ddd.in',   Copy('$TARGET', '$SOURCE'))
denv.Command('n2.out',  n2_in,      Copy('$TARGET', '$SOURCE'))
env.Command( 'eee.out', 'eee.in',   Copy('$TARGET', '$SOURCE'))
env.Command( 'n3.out',  n3_in,      Copy('$TARGET', '$SOURCE'))
def default_decider(dependency, target, prev_ni, repo_node=None):
    return os.path.exists('default-has-changed')
def env_decider(dependency, target, prev_ni, repo_node=None):
    return os.path.exists('env-has-changed')
def node_decider(dependency, target, prev_ni, repo_node=None):
    return os.path.exists('node-has-changed')
Decider(default_decider)
env.Decider(env_decider)
n1_in.Decider(node_decider)
n2_in.Decider(node_decider)
n3_in.Decider(node_decider)
""")

test.write('ccc.in', "ccc.in\n")
test.write('ddd.in', "ddd.in\n")
test.write('eee.in', "eee.in\n")
test.write('n1.in', "n1.in\n")
test.write('n2.in', "n2.in\n")
test.write('n3.in', "n3.in\n")



test.run(arguments = '.')

test.up_to_date(arguments = '.')



test.write('env-has-changed', "\n")

test.not_up_to_date(arguments = 'eee.out')
test.up_to_date(arguments = 'ccc.out ddd.out n1.out n2.out n3.out')

test.not_up_to_date(arguments = 'eee.out')
test.up_to_date(arguments = 'ccc.out ddd.out n1.out n2.out n3.out')

test.unlink('env-has-changed')



test.write('default-has-changed', "\n")

test.not_up_to_date(arguments = 'ccc.out ddd.out')
test.up_to_date(arguments = 'eee.out n1.out n2.out n3.out')

test.not_up_to_date(arguments = 'ccc.out ddd.out')
test.up_to_date(arguments = 'eee.out n1.out n2.out n3.out')

test.unlink('default-has-changed')



test.up_to_date(arguments = '.')

test.write('node-has-changed', "\n")

test.not_up_to_date(arguments = 'n1.out n2.out n3.out')
test.up_to_date(arguments = 'ccc.out ddd.out eee.out')

test.not_up_to_date(arguments = 'n1.out n2.out n3.out')
test.up_to_date(arguments = 'ccc.out ddd.out eee.out')

test.unlink('node-has-changed')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
