#
# Copyright (c) 2001 Steven Knight
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

import TestCmd
import SCons.Scanner.Prog
import unittest
import sys
import os.path

test = TestCmd.TestCmd(workdir = '')

test.subdir('d1', ['d1', 'd2'])

libs = [ 'l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib' ]

for h in libs:
    test.write(h, " ")

# define some helpers:

class DummyEnvironment:
    def __init__(self, **kw):
        self._dict = kw
        self._dict['LIBSUFFIX'] = '.lib'
        
    def Dictionary(self, *args):
        if not args:
            return self._dict
        elif len(args) == 1:
            return self._dict[args[0]]
        else:
            return map(lambda x, s=self: s._dict[x], args)

def deps_match(deps, libs):
    deps=map(str, deps)
    deps.sort()
    libs.sort()
    return map(os.path.normpath, deps) == \
           map(os.path.normpath,
               map(test.workpath, libs))

# define some tests:

class ProgScanTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgScan()
        deps = s.scan('dummy', env)
        assert deps_match(deps, ['l1.lib']), map(str, deps)

class ProgScanTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=map(test.workpath,
                                           ["", "d1", "d1/d2" ]),
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgScan()
        deps = s.scan('dummy', env)
        assert deps_match(deps, ['l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib' ]), map(str, deps)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ProgScanTestCase1())
    suite.addTest(ProgScanTestCase2())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
