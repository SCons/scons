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

import os
import os.path
import sys
import unittest

import SCons.Scanner.Fortran
import SCons.Node.FS
import SCons.Warnings

import TestCmd

original = os.getcwd()

test = TestCmd.TestCmd(workdir = '')

os.chdir(test.workpath(''))

# create some source files and headers:

test.write('fff1.f',"""
      PROGRAM FOO
      INCLUDE 'f1.f'
      INCLUDE 'f2.f'
      STOP
      END
""")

test.write('fff2.f',"""
      PROGRAM FOO
      INCLUDE 'f2.f'
      INCLUDE 'd1/f2.f'
      INCLUDE 'd2/f2.f'
      STOP
      END
""")

test.write('fff3.f',"""
      PROGRAM FOO
      INCLUDE 'f3.f' ; INCLUDE\t'd1/f3.f'
      STOP
      END
""")


# for Emacs -> "

test.subdir('d1', ['d1', 'd2'])

headers = ['fi.f', 'never.f',
           'd1/f1.f', 'd1/f2.f', 'd1/f3.f', 'd1/fi.f',
           'd1/d2/f1.f', 'd1/d2/f2.f', 'd1/d2/f3.f',
           'd1/d2/f4.f', 'd1/d2/fi.f']

for h in headers:
    test.write(h, "\n")


test.subdir('include', 'subdir', ['subdir', 'include'])

test.write('fff4.f',"""
      PROGRAM FOO
      INCLUDE 'f4.f'
      STOP
      END
""")

test.write('include/f4.f', "\n")
test.write('subdir/include/f4.f', "\n")


test.subdir('repository', ['repository', 'include'])
test.subdir('work', ['work', 'src'])

test.write(['repository', 'include', 'iii.f'], "\n")

test.write(['work', 'src', 'fff.f'], """
      PROGRAM FOO
      INCLUDE 'iii.f'
      STOP
      END
""")

# define some helpers:

class DummyTarget:
    def __init__(self, cwd=None):
        self.cwd = cwd

class DummyEnvironment:
    def __init__(self, listCppPath):
        self.path = listCppPath
        
    def Dictionary(self, *args):
        if not args:
            return { 'F77PATH': self.path }
        elif len(args) == 1 and args[0] == 'F77PATH':
            return self.path
        else:
            raise KeyError, "Dummy environment only has F77PATH attribute."

    def __getitem__(self,key):
        return self.Dictionary()[key]

    def __setitem__(self,key,value):
        self.Dictionary()[key] = value

    def __delitem__(self,key):
        del self.Dictionary()[key]

def deps_match(self, deps, headers):
    scanned = map(os.path.normpath, map(str, deps))
    expect = map(os.path.normpath, headers)
    self.failUnless(scanned == expect, "expect %s != scanned %s" % (expect, scanned))

def make_node(filename, fs=SCons.Node.FS.default_fs):
    return fs.File(test.workpath(filename))

# define some tests:

class FortranScannerTestCase1(unittest.TestCase):
    def runTest(self):
        test.write('f1.f', "\n")
        test.write('f2.f', "      INCLUDE 'fi.f'\n")
        env = DummyEnvironment([])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff1.f', fs), env, DummyTarget())
        headers = ['f1.f', 'f2.f', 'fi.f']
        deps_match(self, deps, map(test.workpath, headers))
	test.unlink('f1.f')
	test.unlink('f2.f')

class FortranScannerTestCase2(unittest.TestCase):
    def runTest(self):
        test.write('f1.f', "\n")
        test.write('f2.f', "      INCLUDE 'fi.f'\n")
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff1.f', fs), env, DummyTarget())
        headers = ['f1.f', 'f2.f', 'fi.f']
        deps_match(self, deps, map(test.workpath, headers))
	test.unlink('f1.f')
	test.unlink('f2.f')

class FortranScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff1.f', fs), env, DummyTarget())
        headers = ['d1/f1.f', 'd1/f2.f']
        deps_match(self, deps, map(test.workpath, headers))

class FortranScannerTestCase4(unittest.TestCase):
    def runTest(self):
        test.write(['d1', 'f2.f'], "      INCLUDE 'fi.f'\n")
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff1.f', fs), env, DummyTarget())
        headers = ['d1/f1.f', 'd1/f2.f']
        deps_match(self, deps, map(test.workpath, headers))
        test.write(['d1', 'f2.f'], "\n")

class FortranScannerTestCase5(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff2.f', fs), env, DummyTarget())
        headers = ['d1/d2/f2.f', 'd1/f2.f', 'd1/f2.f']
        deps_match(self, deps, map(test.workpath, headers))

class FortranScannerTestCase6(unittest.TestCase):
    def runTest(self):
        test.write('f2.f', "\n")
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff2.f', fs), env, DummyTarget())
        headers =  ['d1/d2/f2.f', 'd1/f2.f', 'f2.f']
        deps_match(self, deps, map(test.workpath, headers))
        test.unlink('f2.f')

class FortranScannerTestCase7(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1/d2"), test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff2.f', fs), env, DummyTarget())
        headers =  ['d1/d2/f2.f', 'd1/d2/f2.f', 'd1/f2.f']
        deps_match(self, deps, map(test.workpath, headers))

class FortranScannerTestCase8(unittest.TestCase):
    def runTest(self):
        test.write('f2.f', "\n")
        env = DummyEnvironment([test.workpath("d1/d2"), test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
	fs = SCons.Node.FS.FS(original)
        deps = s.scan(make_node('fff2.f', fs), env, DummyTarget())
        headers =  ['d1/d2/f2.f', 'd1/f2.f', 'f2.f']
        deps_match(self, deps, map(test.workpath, headers))
        test.unlink('f2.f')
        
class FortranScannerTestCase9(unittest.TestCase):
    def runTest(self):
        test.write('f3.f', "\n")
        env = DummyEnvironment([])
        s = SCons.Scanner.Fortran.FortranScan()
        deps = s.scan(make_node('fff3.f'), env, DummyTarget())
        
        # Make sure exists() gets called on the file node being
        # scanned, essential for cooperation with BuildDir functionality.
        assert SCons.Node.FS.default_fs.File(test.workpath('fff3.f')).created
        
        headers =  ['d1/f3.f', 'f3.f']
        deps_match(self, deps, map(test.workpath, headers))
        test.unlink('f3.f')

class FortranScannerTestCase10(unittest.TestCase):
    def runTest(self):
        fs = SCons.Node.FS.FS(test.workpath(''))
        env = DummyEnvironment(["include"])
        s = SCons.Scanner.Fortran.FortranScan(fs = fs)
        deps1 = s.scan(fs.File('fff4.f'), env, DummyTarget())
        fs.chdir(fs.Dir('subdir'))
        target = DummyTarget(fs.getcwd())
        fs.chdir(fs.Dir('..'))
        deps2 = s.scan(fs.File('#fff4.f'), env, target)
        headers1 =  ['include/f4.f']
        headers2 =  ['subdir/include/f4.f']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)

class FortranScannerTestCase11(unittest.TestCase):
    def runTest(self):
        SCons.Warnings.enableWarningClass(SCons.Warnings.DependencyWarning)
        class TestOut:
            def __call__(self, x):
                self.out = x

        to = TestOut()
        to.out = None
        SCons.Warnings._warningOut = to
        test.write('f4.f',"      INCLUDE 'not_there.f'\n")
        fs = SCons.Node.FS.FS(test.workpath(''))
        s = SCons.Scanner.Fortran.FortranScan(fs=fs)
        env = DummyEnvironment([])
        deps = s.scan(fs.File('fff4.f'), env, DummyTarget())

        # Did we catch the warning from not finding not_there.f?
        assert to.out
        
        deps_match(self, deps, [ 'f4.f' ])
        test.unlink('f4.f')

class FortranScannerTestCase12(unittest.TestCase):
    def runTest(self):
        fs = SCons.Node.FS.FS(test.workpath(''))
        fs.chdir(fs.Dir('include'))
        s = SCons.Scanner.Fortran.FortranScan(fs=fs)
        env = DummyEnvironment([])
        test.write('include/fff4.f', test.read('fff4.f'))
        deps = s.scan(fs.File('#include/fff4.f'), env, DummyTarget())
        deps_match(self, deps, ['include/f4.f'])
        test.unlink('include/fff4.f')

class FortranScannerTestCase13(unittest.TestCase):
    def runTest(self):
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.Repository(test.workpath('repository'))
        s = SCons.Scanner.Fortran.FortranScan(fs=fs)
        env = DummyEnvironment(['include'])
        deps = s.scan(fs.File('src/fff.f'), env, DummyTarget())
        deps_match(self, deps, [test.workpath('repository/include/iii.f')])
        os.chdir(test.workpath(''))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(FortranScannerTestCase1())
    suite.addTest(FortranScannerTestCase2())
    suite.addTest(FortranScannerTestCase3())
    suite.addTest(FortranScannerTestCase4())
    suite.addTest(FortranScannerTestCase5())
    suite.addTest(FortranScannerTestCase6())
    suite.addTest(FortranScannerTestCase7())
    suite.addTest(FortranScannerTestCase8())
    suite.addTest(FortranScannerTestCase9())
    suite.addTest(FortranScannerTestCase10())
    suite.addTest(FortranScannerTestCase11())
    suite.addTest(FortranScannerTestCase12())
    suite.addTest(FortranScannerTestCase13())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
