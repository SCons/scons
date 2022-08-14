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
Verify behavior of the MD5-timestamp Decider() setting when combined with Repository() usage
"""

import os
import stat

import TestSCons

test = TestSCons.TestSCons()

test.subdir('Repository', 'work')
repository = test.workpath('Repository')

test.write(['Repository','content1.in'], "content1.in 1\n")
test.write(['Repository','content2.in'], "content2.in 1\n")
test.write(['Repository','content3.in'], "content3.in 1\n")
# test.writable('Repository', 0)

test.write(['work','SConstruct'], """\
Repository(r'%s')
DefaultEnvironment(tools=[])
m = Environment(tools=[])
m.Decider('MD5-timestamp')
m.Command('content1.out', 'content1.in', Copy('$TARGET', '$SOURCE'))
m.Command('content2.out', 'content2.in', Copy('$TARGET', '$SOURCE'))
m.Command('content3.out', 'content3.in', Copy('$TARGET', '$SOURCE'))
""" % repository)

test.run(chdir='work',arguments='.')
test.up_to_date(chdir='work',arguments='.')

test.sleep()  # delay for timestamps
test.write(['Repository','content1.in'], "content1.in 2\n")
test.touch(['Repository','content2.in'])
time_content = os.stat(os.path.join(repository,'content3.in'))[stat.ST_MTIME]
test.write(['Repository','content3.in'], "content3.in 2\n")
test.touch(['Repository','content3.in'], time_content)

# We should only see content1.out rebuilt.  The timestamp of content2.in
# has changed, but its content hasn't, so the follow-on content check says
# to not rebuild it.  The content of content3.in has changed, but that's
# masked by the fact that its timestamp is the same as the last run.

expect = test.wrap_stdout("""\
Copy("content1.out", "%s")
""" % os.path.join(repository, 'content1.in'))

test.run(chdir='work', arguments='.', stdout=expect)
test.up_to_date(chdir='work', arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
