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
Test that switching Decider() types between MD5 and timestamp-match
does not cause unnecessary rebuilds.
"""

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

base_sconstruct_contents = """\
DefaultEnvironment(tools=[])
Decider('%s')

def build(env, target, source):
    with open(str(target[0]), 'wt') as f, open(str(source[0]), 'rt') as ifp:
        f.write(ifp.read())
B = Builder(action=build)
env = Environment(tools=[], BUILDERS = { 'B' : B })
env.B(target='switch.out', source='switch.in')
"""

def write_SConstruct(test, sig_type):
    contents = base_sconstruct_contents % sig_type
    test.write('SConstruct', contents)


# Build first MD5 checksums.
write_SConstruct(test, 'MD5')

test.write('switch.in', "switch.in\n")

switch_out_switch_in = test.wrap_stdout(r'build\(\["switch.out"\], \["switch.in"\]\)\n')

test.run(arguments='switch.out', stdout=switch_out_switch_in)

test.up_to_date(arguments='switch.out')


# Now rebuild with timestamp-match.  Because we always store timestamps,
# even when making the decision based on MD5 checksums, the build is
# still up to date.
write_SConstruct(test, 'timestamp-match')

test.up_to_date(arguments='switch.out')


# Now switch back to MD5 checksums.  When we rebuilt with the timestamp,
# it wiped out the MD5 value (because the point of timestamps is to not
# open up and checksum the contents), so the file is considered *not*
# up to date and must be rebuilt to generate a checksum.
write_SConstruct(test, 'MD5')

test.not_up_to_date(arguments='switch.out')


# And just for good measure, make sure that we now rebuild in response
# to a content change.
test.write('switch.in', "switch.in 2\n")

test.run(arguments='switch.out', stdout=switch_out_switch_in)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
