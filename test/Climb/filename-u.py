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
Verify the ability to use the -u option with the -f option to
specify a different top-level file name.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir', 'other')

test.write('main.scons', """\
DefaultEnvironment(tools=[])
print("main.scons")
SConscript('subdir/sub.scons')
""")

test.write(['subdir', 'sub.scons'], """\
print("subdir/sub.scons")
""")

read_str = """\
main.scons
subdir/sub.scons
"""

expect = "scons: Entering directory `%s'\n" % test.workpath() \
         + test.wrap_stdout(read_str = read_str,
                            build_str = "scons: `subdir' is up to date.\n")

test.run(chdir='subdir', arguments='-u -f main.scons .', stdout=expect)



expect = test.wrap_stdout(read_str = "subdir/sub.scons\n",
                          build_str = "scons: `.' is up to date.\n")

test.run(chdir='other', arguments='-u -f ../subdir/sub.scons .', stdout=expect)

test.run(chdir='other',
         arguments='-u -f %s .' % test.workpath('subdir', 'sub.scons'),
         stdout=expect)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
