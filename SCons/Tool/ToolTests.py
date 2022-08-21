# MIT License
#
# Copyright The SCons Foundation
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

import os
import unittest

import TestUnit

import SCons.Errors
import SCons.Tool


class DummyEnvironment:
    def __init__(self):
        self.dict = {}
    def Detect(self, progs):
        if not SCons.Util.is_List(progs):
            progs = [ progs ]
        return progs[0]
    def Append(self, **kw):
        self.dict.update(kw)
    def __getitem__(self, key):
        return self.dict[key]
    def __setitem__(self, key, val):
        self.dict[key] = val
    def __contains__(self, key):
        return key in self.dict
    def subst(self, string, *args, **kwargs):
        return string

    PHONY_PATH = "/usr/phony/bin"
    def WhereIs(self, key_program):
        # for pathfind test for Issue #3336:
        # need to fake the case where extra paths are searched, and
        # if one has a "hit" after some fails, the fails are left in
        # the environment's PATH. So construct a positive answer if
        # we see a magic known path component in PATH; answer in
        # the negative otherwise.
        paths = self['ENV']['PATH']
        if self.PHONY_PATH in paths:
            return os.path.join(self.PHONY_PATH, key_program)
        return None
    def AppendENVPath(self, pathvar, path):
        # signature matches how called from find_program_path()
        self['ENV'][pathvar] = self['ENV'][pathvar] + os.pathsep + path


class ToolTestCase(unittest.TestCase):
    def test_Tool(self):
        """Test the Tool() function"""

        env = DummyEnvironment()
        env['BUILDERS'] = {}
        env['ENV'] = {}
        env['PLATFORM'] = 'test'
        t = SCons.Tool.Tool('g++')
        t(env)
        assert (env['CXX'] == 'c++' or env['CXX'] == 'g++'), env['CXX']
        assert env['INCPREFIX'] == '-I', env['INCPREFIX']
        assert env['TOOLS'] == ['g++'], env['TOOLS']

        exc_caught = None
        try:
            SCons.Tool.Tool()
        except TypeError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

        exc_caught = None
        try:
            p = SCons.Tool.Tool('_does_not_exist_')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            # Old msg was Python-style "No tool named", check for new msg:
            assert "No tool module" in str(e), e
        assert exc_caught, "did not catch expected UserError"


    def test_pathfind(self):
        """Test that find_program_path() alters PATH only if add_path is true"""

        env = DummyEnvironment()
        PHONY_PATHS = [
            r'C:\cygwin64\bin',
            r'C:\cygwin\bin',
            '/usr/local/dummy/bin',
            env.PHONY_PATH,  # will be recognized by dummy WhereIs
        ]
        env['ENV'] = {}
        env['ENV']['PATH'] = '/usr/local/bin:/opt/bin:/bin:/usr/bin'
        pre_path = env['ENV']['PATH']
        _ = SCons.Tool.find_program_path(env, 'no_tool', default_paths=PHONY_PATHS)
        assert env['ENV']['PATH'] == pre_path, env['ENV']['PATH']

        _ = SCons.Tool.find_program_path(env, 'no_tool', default_paths=PHONY_PATHS, add_path=True)
        assert env.PHONY_PATH in env['ENV']['PATH'], env['ENV']['PATH']


if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_'
    suite = loader.loadTestsFromTestCase(ToolTestCase)
    TestUnit.run(suite)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
