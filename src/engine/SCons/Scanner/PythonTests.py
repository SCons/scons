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

import SCons.compat

import collections
import os
import unittest

import TestCmd

import SCons.Node.FS
import SCons.Scanner.Python

test = TestCmd.TestCmd(workdir='')
test.dir_fixture('python_scanner')

if os.path.normcase('foo') == os.path.normcase('FOO'):
    my_normpath = os.path.normcase
else:
    my_normpath = os.path.normpath


def deps_match(self, deps, headers):
    global my_normpath
    scanned = list(map(my_normpath, list(map(str, deps))))
    expect = list(map(my_normpath, headers))
    self.assertTrue(scanned == expect,
                    "expect %s != scanned %s" % (expect, scanned))


# Copied from LaTeXTests.py.
class DummyEnvironment(collections.UserDict):
    def __init__(self, **kw):
        collections.UserDict.__init__(self)
        self.data.update(kw)
        self.fs = SCons.Node.FS.FS(test.workpath(''))
        self['ENV'] = {}

    def Dictionary(self, *args):
        return self.data

    def subst(self, strSubst, target=None, source=None, conv=None):
        if strSubst[0] == '$':
            return self.data[strSubst[1:]]
        return strSubst

    def subst_list(self, strSubst, target=None, source=None, conv=None):
        if strSubst[0] == '$':
            return [self.data[strSubst[1:]]]
        return [[strSubst]]

    def subst_path(self, path, target=None, source=None, conv=None):
        if not isinstance(path, list):
            path = [path]
        return list(map(self.subst, path))

    def get_calculator(self):
        return None

    def get_factory(self, factory):
        return factory or self.fs.File

    def Dir(self, filename):
        return self.fs.Dir(filename)

    def File(self, filename):
        return self.fs.File(filename)


class PythonScannerTestPythonPath(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        env['ENV']['PYTHONPATH'] = test.workpath('')
        path = s.path(env)
        deps = s(env.File('imports_simple_package.py'), env, path)
        files = ['simple_package/__init__.py']
        deps_match(self, deps, files)


class PythonScannerTestPythonCallablePath(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        env['ENV']['PYTHONPATH'] = test.workpath('')
        deps = s(env.File('imports_simple_package.py'), env,
                 lambda : s.path(env))
        files = ['simple_package/__init__.py']
        deps_match(self, deps, files)


class PythonScannerTestImportSimplePackage(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('imports_simple_package.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py']
        deps_match(self, deps, files)

        # Repeat the test in case there are any issues caching includes.
        deps = s(node, env, path)
        deps_match(self, deps, files)


class PythonScannerTestImportSimplePackageModule1As(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('import_simple_package_module1_as.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py', 'simple_package/module1.py']
        deps_match(self, deps, files)


class PythonScannerTestImportSimplePackageModuleAs(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('import_simple_package_module1.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py', 'simple_package/module1.py']
        deps_match(self, deps, files)


class PythonScannerTestFromImportSimplePackageModule1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('from_import_simple_package_module1.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py', 'simple_package/module1.py']
        deps_match(self, deps, files)


class PythonScannerTestFromImportSimplePackageModule1As(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('from_import_simple_package_module1_as.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py', 'simple_package/module1.py']
        deps_match(self, deps, files)


class PythonScannerTestFromImportSimplePackageModulesNoSpace(
        unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('from_import_simple_package_modules_no_space.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py', 'simple_package/module1.py',
                 'simple_package/module2.py']
        deps_match(self, deps, files)


class PythonScannerTestFromImportSimplePackageModulesWithSpace(
        unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('from_import_simple_package_modules_with_space.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['simple_package/__init__.py', 'simple_package/module1.py',
                 'simple_package/module2.py']
        deps_match(self, deps, files)


class PythonScannerTestCurdirReferenceScript(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.Dir('curdir_reference').File('script.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['curdir_reference/helper.py']
        deps_match(self, deps, files)


class PythonScannerTestImportsNested3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File('imports_nested3.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['nested1/__init__.py', 'nested1/nested2/__init__.py',
                 'nested1/nested2/nested3/__init__.py']
        deps_match(self, deps, files)


class PythonScannerTestImportsGrandparentModule(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File(
            'nested1/nested2/nested3/imports_grandparent_module.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        # Note: there is some ambiguity here in what the scanner should return.
        # Relative imports require that the referenced packages have already
        # been imported.
        files = ['nested1/module.py']
        deps_match(self, deps, files)


class PythonScannerTestImportsParentModule(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File(
            'nested1/nested2/nested3/imports_parent_module.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['nested1/nested2/module.py']
        deps_match(self, deps, files)


class PythonScannerTestImportsParentThenSubmodule(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()
        s = SCons.Scanner.Python.PythonScanner
        node = env.File(
            'nested1/nested2/nested3/imports_parent_then_submodule.py')
        path = s.path(env, source=[node])
        deps = s(node, env, path)
        files = ['nested1/nested2a/module.py']
        deps_match(self, deps, files)


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
