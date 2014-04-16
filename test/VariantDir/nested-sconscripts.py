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
Test that nested SConscript files in a VariantDir don't throw
an OSError exception looking for the wrong file.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir(['src'],
            ['src', 'md'],
            ['src', 'md', 'test'])

test.write(['src', 'SConstruct'], """\
BUILD_DIR = '../build'

base_env = Environment()

for flavor in ['prod', 'debug']:
    build_env = base_env.Clone()
    # In real life, we would modify build_env appropriately here
    FLAVOR_DIR = BUILD_DIR + '/' + flavor
    Export('build_env')
    VariantDir(FLAVOR_DIR, 'md', duplicate=0)
    SConscript(FLAVOR_DIR + '/SConscript')
""")

test.write(['src', 'md', 'SConscript'], """\
SConscript('test/SConscript')
""")

test.write(['src', 'md', 'test', 'SConscript'], """\
# empty
""")

test.run(chdir='src')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
