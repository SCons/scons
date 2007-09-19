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

# We name the files 'Tfile' so that they will sort after the SConstruct
# file regardless of whether the test is being run on a case-sensitive
# or case-insensitive system.

env.Command('Tfile.out', 'Tfile.mid', Copy('$TARGET', '$SOURCE'))
env.Command('Tfile.mid', 'Tfile.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('Tfile.in', "Tfile.in\n")

expect_stdout = test.wrap_stdout("""\
Taskmaster: '.': children:
    ['SConstruct', 'Tfile.in', 'Tfile.mid', 'Tfile.out']
    waiting on unfinished children:
    ['SConstruct', 'Tfile.in', 'Tfile.mid', 'Tfile.out']
Taskmaster: 'SConstruct': evaluating SConstruct
Taskmaster: 'Tfile.in': evaluating Tfile.in
Taskmaster: 'Tfile.mid': children:
    ['Tfile.in']
    evaluating Tfile.mid
Copy("Tfile.mid", "Tfile.in")
Taskmaster: 'Tfile.out': children:
    ['Tfile.mid']
    evaluating Tfile.out
Copy("Tfile.out", "Tfile.mid")
Taskmaster: '.': children:
    ['SConstruct', 'Tfile.in', 'Tfile.mid', 'Tfile.out']
    evaluating .
""")

test.run(arguments='--taskmastertrace=- .', stdout=expect_stdout)



test.run(arguments='-c .')



expect_stdout = test.wrap_stdout("""\
Copy("Tfile.mid", "Tfile.in")
Copy("Tfile.out", "Tfile.mid")
""")

test.run(arguments='--taskmastertrace=trace.out .', stdout=expect_stdout)

expect_trace = """\
Taskmaster: '.': children:
    ['SConstruct', 'Tfile.in', 'Tfile.mid', 'Tfile.out']
    waiting on unfinished children:
    ['SConstruct', 'Tfile.in', 'Tfile.mid', 'Tfile.out']
Taskmaster: 'SConstruct': evaluating SConstruct
Taskmaster: 'Tfile.in': evaluating Tfile.in
Taskmaster: 'Tfile.mid': children:
    ['Tfile.in']
    evaluating Tfile.mid
Taskmaster: 'Tfile.out': children:
    ['Tfile.mid']
    evaluating Tfile.out
Taskmaster: '.': children:
    ['SConstruct', 'Tfile.in', 'Tfile.mid', 'Tfile.out']
    evaluating .
"""

test.must_match('trace.out', expect_trace)

test.pass_test()
