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
Verify that an Alias for a VariantDir()'s source directory works as
expected.

This tests for a 0.96.93 bug uncovered by the LilyPond project's build.

The specific problem is that, in 0.96.93, the simple act of trying to
disambiguate a target file in the VariantDir() would call srcnode(), which
would create a "phantom" Node for the target in the *source* directory:

        +-minimal
          +-python
            +-foo               <= this doesn't belong!
            +-foo.py
            +-out-scons
              +-foo             <= this is all right
              +-foo.py

As part of deciding if the 'minimal' Alias is up-to-date, the 'python'
source directory would get scanned for files, including the "phantom"
'python/foo' target Node.  Since this didn't exist, the build would die:

    scons: *** Source `python/foo' not found, needed by target `minimal'.  Stop.

The specific 0.96.94 solution was to make the Node.FS.Entry.disambiguate()
smarter about looking on disk.  Future versions may solve this in other
ways as the architecture evolves, of course, but this will still make
for good test case regardless.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('python')

test.write('SConstruct', """\
import os.path

env = Environment()

def at_copy_ext(target, source, env):
    n = str(source[0])
    with open(n, 'rb') as f:
        s = f.read()
    e = os.path.splitext(n)[1]
    t = str(target[0]) + e
    with open(t, 'wb') as f:
        f.write(s)

AT_COPY_EXT = Builder(action=at_copy_ext, src_suffix=['.py', '.sh',])
env.Append(BUILDERS={'AT_COPY_EXT': AT_COPY_EXT})

env.Alias('minimal', ['python'])

Export('env')

b = 'python/out-scons'

env.VariantDir(b, 'python', duplicate=0)

SConscript(b + '/SConscript')
""")

test.write(['python', 'SConscript'], """\
Import('env')
env.AT_COPY_EXT('foo.py')
""")

test.write(['python', 'foo.py'], 'python/foo.py\n')

test.run('minimal')

test.must_match(['python', 'out-scons', 'foo.py'], "python/foo.py\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
