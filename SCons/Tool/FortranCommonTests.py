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
# from typing import Dict, Any

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import unittest

import SCons.Node.FS
import SCons.Warnings
import SCons.Tool.FortranCommon

import TestCmd

original = os.getcwd()

test = TestCmd.TestCmd(workdir='')

os.chdir(test.workpath(''))


class DummyEnvironment:
    dictionary = None  # type: Dict[Any, Any]

    def __init__(self, list_cpp_path):
        self.path = list_cpp_path
        self.fs = SCons.Node.FS.FS(test.workpath(''))
        self.dictionary = {}

    def __contains__(self, key):
        return key in self.dictionary

    def __getitem__(self, key):
        return self.dictionary[key]

    def __setitem__(self, key, value):
        self.dictionary[key] = value

    def __delitem__(self, key):
        del self.dictionary[key]

    def subst(self, arg, target=None, source=None, conv=None):
        if arg[0] == '$':
            return self[arg[1:]]
        return arg

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


class FortranScannerSubmodulesTestCase(unittest.TestCase):
    def runTest(self):
        """
        Check that test_1.f90 and test_2.f90 which have interface specifications
        Don't generate targets for those modules listed in the interface section
        """

        test.dir_fixture('fortran_unittests')
        env = DummyEnvironment([test.workpath('modules')])
        env['FORTRANMODDIR'] = 'modules'
        env['FORTRANMODSUFFIX'] = '.mod'
        emitter = SCons.Tool.FortranCommon._fortranEmitter
        # path = s.path(env)

        for fort in ['test_1.f90', 'test_2.f90']:
            file_base, _ = os.path.splitext(fort)
            file_mod = '%s.mod' % file_base
            f = env.File(fort)
            (target, source) = emitter([], [f, ], env)

            # print("Targets:%s\nSources:%s"%([str(a) for a in target], [str(a) for a in source]))

            # should only be 1 target and 1 source
            self.assertEqual(len(target), 1,
                             msg="More than 1 target: %d [%s]" % (len(target), [str(t) for t in target]))
            self.assertEqual(len(source), 1,
                             msg="More than 1 source: %d [%s]" % (len(source), [str(t) for t in source]))

            # target should be file_base.mod
            self.assertEqual(str(target[0]).endswith(file_mod), True,
                             msg="Target[0]=%s doesn't end with '%s'" % (str(target[0]), file_mod))

            # source should be file_base .f90
            self.assertEqual(str(source[0]).endswith(fort), True,
                             msg="Source[0]=%s doesn't end with '%s'" % (str(source[0]), fort))


if __name__ == "__main__":
    unittest.main()
