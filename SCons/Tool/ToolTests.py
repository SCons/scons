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

import os
import sys
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
        return self.dict.__contains__(key)
    def has_key(self, key):
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

        try:
            SCons.Tool.Tool()
        except TypeError:
            pass
        else:   # TODO pylint E0704: bare raise not inside except
            raise

        try:
            p = SCons.Tool.Tool('_does_not_exist_')
        except SCons.Errors.SConsEnvironmentError:
            pass
        else:   # TODO pylint E0704: bare raise not inside except
            raise


    def test_pathfind(self):
        """Test that find_program_path() does not alter PATH"""

        env = DummyEnvironment()
        PHONY_PATHS = [
            r'C:\cygwin64\bin',
            r'C:\cygwin\bin',
            '/usr/local/dummy/bin',
            env.PHONY_PATH,     # will be recognized by dummy WhereIs
        ]
        env['ENV'] = {}
        env['ENV']['PATH'] = '/usr/local/bin:/opt/bin:/bin:/usr/bin'
        pre_path = env['ENV']['PATH']
        _ = SCons.Tool.find_program_path(env, 'no_tool', default_paths=PHONY_PATHS)
        assert env['ENV']['PATH'] == pre_path, env['ENV']['PATH']


if __name__ == "__main__":
    suite = unittest.makeSuite(ToolTestCase, 'test_')
    TestUnit.run(suite)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
