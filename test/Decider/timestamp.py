#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Verify various interactions of the timestamp-match and timestamp-newer
Decider() settings:.
"""

import os
import stat

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
m = Environment(tools=[])
m.Decider('timestamp-match')
m.Command('match1.out', 'match1.in', Copy('$TARGET', '$SOURCE'))
m.Command('match2.out', 'match2.in', Copy('$TARGET', '$SOURCE'))
n = Environment(tools=[])
n.Decider('timestamp-newer')
n.Command('newer1.out', 'newer1.in', Copy('$TARGET', '$SOURCE'))
n.Command('newer2.out', 'newer2.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('match1.in', "match1.in\n")
test.write('match2.in', "match2.in\n")
test.write('newer1.in', "newer1.in\n")
test.write('newer2.in', "newer2.in\n")

test.run(arguments = '.')
test.up_to_date(arguments = '.')

time_match = os.stat('match2.out')[stat.ST_MTIME]
time_newer = os.stat('newer2.out')[stat.ST_MTIME]

# Now make all the source files newer than (different timestamps from)
# the last time the targets were built, and touch the target files
# of match1.out and newer1.out to see the different effects.
test.sleep()  # delay for timestamps
test.touch('match1.in')
test.touch('newer1.in')
test.touch('match2.in')
test.touch('newer2.in')

test.sleep()  # delay for timestamps
test.touch('match1.out')
test.touch('newer1.out')

# We should see both match1.out and match2.out rebuilt, because the
# source file timestamps do not match the last time they were built,
# but only newer2.out rebuilt.  newer1.out is *not* rebuilt because
# the actual target file timestamp is, in fact, newer than the
# source file (newer1.in) timestamp.

expect = test.wrap_stdout("""\
Copy("match1.out", "match1.in")
Copy("match2.out", "match2.in")
Copy("newer2.out", "newer2.in")
""")

test.run(arguments='.', stdout=expect)

# Now, for the somewhat pathological case, reset the match2.out and
# newer2.out timestamps to the older timestamp when the targets were
# first built.  This will cause newer2.out to be rebuilt, because
# the newer1.in timestamp is now newer than the older, reset target
# file timestamp, but match2.out is *not* rebuilt because its source
# file (match2.in) timestamp still exactly matches the timestamp
# recorded when the target file was last built.

test.touch('match2.out', time_match)
test.touch('newer2.out', time_newer)

expect = test.wrap_stdout("""\
Copy("newer2.out", "newer2.in")
""")

test.run(arguments='.', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
