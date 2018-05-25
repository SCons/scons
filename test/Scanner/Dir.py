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
Verify that a simple scanner that returns Dir nodes works correctly.

Submitted as https://github.com/SCons/scons/issues/2534
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir(['src'])

test.write(['SConstruct'], """\
env = Environment()
Export('env')

env.VariantDir('build', 'src')
env.SConscript('build/SConscript.py')
""")

test.write(['src', 'SConscript.py'], """\
Import('env')

def myscanner(node, env, path):
    return [ env.Dir('#/install/dir2') ] # Gives error

def mybuilder(target, source, env):
    env.Execute(Copy(target[0], source[0]))
    return None

env['BUILDERS']['MyBuilder'] = env.Builder(action=mybuilder, source_scanner=env.Scanner(function=myscanner))

out = env.MyBuilder('outfile1', 'infile1')

env.Install('#/install/dir1', out)
env.Install('#/install/dir2','infile2')
""")

test.write(['src', 'infile1'], """\
src/infile1
""")

test.write(['src', 'infile2'], """\
src/infile2
""")

test.run(arguments = '.')

test.must_match(['install', 'dir1', 'outfile1'], "src/infile1\n")
test.must_match(['install', 'dir2', 'infile2'], "src/infile2\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
