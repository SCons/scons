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
Test the case (reported by Jeff Petkau, bug #694744) where a target
is source for another target with a scanner, which used to cause us
to push the file to the CacheDir after the build signature had already
been cleared (as a sign that the built file should now be rescanned).
"""


import TestSCons

test = TestSCons.TestSCons()

test.subdir('cache')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
import SCons

CacheDir(r'%s')

def docopy(target,source,env):
    data = source[0].get_contents()
    with open(target[0].rfile().get_abspath(), "wb") as f:
        f.write(data)

def sillyScanner(node, env, dirs):
    print('This is never called (unless we build file.out)')
    return []

SillyScanner = SCons.Scanner.ScannerBase(function=sillyScanner, skeys=['.res'])

env = Environment(tools=[], SCANNERS=[SillyScanner], BUILDERS={})

r = env.Command('file.res', 'file.ma', docopy)

env.Command('file.out', r, docopy)

# make r the default. Note that we don't even try to build file.out,
# and so SillyScanner never runs. The bug is the same if we build
# file.out, though.
Default(r)
""" % test.workpath('cache'))

test.write('file.ma', "file.ma\n")

test.run()

test.must_not_exist(test.workpath('cache', 'N', 'None'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
