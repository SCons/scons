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


__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import contextlib
import sys
from io import StringIO

import TestSCons

test = TestSCons.TestSCons()

try:
    import pstats
except ImportError:
    test.skip_test('No pstats module, skipping test.\n')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
Command('file.out', 'file.in', Copy("$TARGET", "$SOURCE"))
""")

test.write('file.in', "file.in\n")

scons_prof = test.workpath('scons.prof')

test.run(arguments = "--profile=%s -h" % scons_prof)
test.must_contain_all_lines(test.stdout(), ['usage: scons [OPTION]'])

try:
    save_stdout = sys.stdout
    with contextlib.closing(StringIO()) as sys.stdout:
        stats = pstats.Stats(scons_prof)
        stats.sort_stats('time')

        stats.strip_dirs().print_stats()

        s = sys.stdout.getvalue()
finally:
    sys.stdout = save_stdout

test.must_contain_all_lines(s, ['Main.py', '_main'])



scons_prof = test.workpath('scons2.prof')

test.run(arguments = "--profile %s" % scons_prof)

try:
    save_stdout = sys.stdout
    with contextlib.closing(StringIO()) as sys.stdout:
        stats = pstats.Stats(scons_prof)
        stats.sort_stats('time')

        stats.strip_dirs().print_stats()

        s = sys.stdout.getvalue()
finally:
    sys.stdout = save_stdout

test.must_contain_all_lines(s, ['Main.py', '_main', 'FS.py'])



scons_prof = test.workpath('scons3.prof')

test.run(arguments = "--profile %s --debug=memory -h" % scons_prof)
expect = [
    'usage: scons [OPTION]',
    'Options:'
]
test.must_contain_all_lines(test.stdout(), expect)

expect = 'Memory before reading SConscript files'
lines = test.stdout().split('\n')
memory_lines = [l for l in lines if l.find(expect) != -1]

test.fail_test(len(memory_lines) != 1)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
