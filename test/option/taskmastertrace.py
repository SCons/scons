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
Simple tests of the --taskmastertrace= option.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Command('file.out', 'file.mid', Copy('$TARGET', '$SOURCE'))
env.Command('file.mid', 'file.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('file.in', "file.in\n")

expect_stdout = test.wrap_stdout("""\
Taskmaster: '.': waiting on unstarted children:
    ['file.out', 'file.mid']
Taskmaster: 'file.mid': building
Copy("file.mid", "file.in")
Taskmaster: 'file.out': building
Copy("file.out", "file.mid")
Taskmaster: '.': building
""")

test.run(arguments='--taskmastertrace=- .', stdout=expect_stdout)



test.run(arguments='-c .')



expect_stdout = test.wrap_stdout("""\
Copy("file.mid", "file.in")
Copy("file.out", "file.mid")
""")

test.run(arguments='--taskmastertrace=trace.out .', stdout=expect_stdout)

expect_trace = """\
Taskmaster: '.': waiting on unstarted children:
    ['file.out', 'file.mid']
Taskmaster: 'file.mid': building
Taskmaster: 'file.out': building
Taskmaster: '.': building
"""

test.must_match('trace.out', expect_trace)

test.pass_test()
