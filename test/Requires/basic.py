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
Verify basic operation of the env.Requires() method for specifying
order-only prerequisites.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def append_prereq_func(target, source, env):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())
        with open('prereq.out', 'rb') as ifp:
            ofp.write(ifp.read())
    return None
append_prereq = Action(append_prereq_func)
env = Environment()
env.Requires('file.out', 'prereq.out')
env.Command('file.out', 'file.in', append_prereq)
env.Command('prereq.out', 'prereq.in', Copy('$TARGET', '$SOURCES'))
""")

test.write('file.in', "file.in 1\n")
test.write('prereq.in', "prereq.in 1\n")

# First:  build file.out.  prereq.out should be built first, and if
# not, we'll get an error when the build action tries to use it to
# build file.out.

test.run(arguments = 'file.out')

test.must_match('prereq.out', "prereq.in 1\n")
test.must_match('file.out', "file.in 1\nprereq.in 1\n")

# Update the prereq.out file.  file.out should still be up to date because
# prereq.out is not actually a dependency, so we don't detect the
# underlying change.

test.write('prereq.out', "prereq.out 2\n")

test.up_to_date(arguments = 'file.out')

# Now update the prereq.in file.  Trying to rebuild file.out should
# cause prereq.out to be updated because of the change, but file.out
# should *not* be rebuilt because, again, prereq.out isn't actually
# a dependency that causes rebuilds.

test.write('prereq.in', "prereq.in 3\n")

test.run(arguments = 'file.out')

test.must_match('prereq.out', "prereq.in 3\n")
test.must_match('file.out', "file.in 1\nprereq.in 1\n")

# Now update file.in, which will cause file.out to be rebuilt, picking
# up the change(s) to prereq.out of which we were previously oblivious.

test.write('file.in', 'file.in 4\n')

test.run(arguments = 'file.out')

test.must_match('prereq.out', "prereq.in 3\n")
test.must_match('file.out', "file.in 4\nprereq.in 3\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
