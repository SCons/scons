#
# Copyright (c) 2001, 2002 Steven Knight
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

import os.path
import string
import sys
import types
import unittest

import TestCmd
import SCons.Scanner.Prog

test = TestCmd.TestCmd(workdir = '')

test.subdir('d1', ['d1', 'd2'])

libs = [ 'l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib' ]

for h in libs:
    test.write(h, " ")

# define some helpers:

class DummyTarget:
    def __init__(self, cwd=None):
        self.cwd = cwd

class DummyEnvironment:
    def __init__(self, **kw):
        self._dict = kw
        self._dict['LIBSUFFIXES'] = '.lib'
        
    def Dictionary(self, *args):
        if not args:
            return self._dict
        elif len(args) == 1:
            return self._dict[args[0]]
        else:
            return map(lambda x, s=self: s._dict[x], args)
    def __getitem__(self,key):
        return self.Dictionary()[key]

    def __setitem__(self,key,value):
        self.Dictionary()[key] = value

    def __delitem__(self,key):
        del self.Dictionary()[key]

    def subst(self, s):
        return s

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
        deps = s.scan('dummy', env, DummyTarget())
        assert deps_match(deps, ['l1.lib']), map(str, deps)

class ProgScanTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=map(test.workpath,
                                           ["", "d1", "d1/d2" ]),
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgScan()
        deps = s.scan('dummy', env, DummyTarget())
        assert deps_match(deps, ['l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib' ]), map(str, deps)

class ProgScanTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[test.workpath("d1/d2"),
                                        test.workpath("d1")],
                               LIBS=string.split('l2 l3'))
        s = SCons.Scanner.Prog.ProgScan()
        deps = s.scan('dummy', env, DummyTarget())
        assert deps_match(deps, ['d1/l2.lib', 'd1/d2/l3.lib']), map(str, deps)

class ProgScanTestCase5(unittest.TestCase):
    def runTest(self):
        class SubstEnvironment(DummyEnvironment):
            def subst(self, arg, path=test.workpath("d1")):
                if arg == "blah":
                    return test.workpath("d1")
                else:
                    return arg
        env = SubstEnvironment(LIBPATH=[ "blah" ],
                               LIBS=string.split('l2 l3'))
        s = SCons.Scanner.Prog.ProgScan()
        deps = s.scan('dummy', env, DummyTarget())
        assert deps_match(deps, [ 'd1/l2.lib' ]), map(str, deps)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ProgScanTestCase1())
    suite.addTest(ProgScanTestCase2())
    suite.addTest(ProgScanTestCase3())
    suite.addTest(ProgScanTestCase5())
    if hasattr(types, 'UnicodeType'):
        code = """if 1:
            class ProgScanTestCase4(unittest.TestCase):
                def runTest(self):
                    env = DummyEnvironment(LIBPATH=[test.workpath("d1/d2"),
                                                    test.workpath("d1")],
                                           LIBS=string.split(u'l2 l3'))
                    s = SCons.Scanner.Prog.ProgScan()
                    deps = s.scan('dummy', env, DummyTarget())
                    assert deps_match(deps, ['d1/l2.lib', 'd1/d2/l3.lib']), map(str, deps)
            suite.addTest(ProgScanTestCase4())
            \n"""
        exec code
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
