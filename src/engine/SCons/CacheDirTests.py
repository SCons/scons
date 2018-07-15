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

import os.path
import shutil
import sys
import unittest

from TestCmd import TestCmd

import SCons.CacheDir

built_it = None

class Action(object):
    def __call__(self, targets, sources, env, **kw):
        global built_it
        if kw.get('execute', 1):
            built_it = 1
        return 0
    def genstring(self, target, source, env):
        return str(self)
    def get_contents(self, target, source, env):
        return bytearray('','utf-8')

class Builder(object):
    def __init__(self, environment, action):
        self.env = environment
        self.action = action
        self.overrides = {}
        self.source_scanner = None
        self.target_scanner = None

class Environment(object):
    def __init__(self, cachedir):
        self.cachedir = cachedir
    def Override(self, overrides):
        return self
    def get_CacheDir(self):
        return self.cachedir

class BaseTestCase(unittest.TestCase):
    """
    Base fixtures common to our other unittest classes.
    """
    def setUp(self):
        self.test = TestCmd(workdir='')

        import SCons.Node.FS
        self.fs = SCons.Node.FS.FS()

        self._CacheDir = SCons.CacheDir.CacheDir('cache')

    def File(self, name, bsig=None, action=Action()):
        node = self.fs.File(name)
        node.builder_set(Builder(Environment(self._CacheDir), action))
        if bsig:
            node.cachesig = bsig
            #node.binfo = node.BuildInfo(node)
            #node.binfo.ninfo.bsig = bsig
        return node

    def tearDown(self):
        os.remove(os.path.join(self._CacheDir.path, 'config'))
        os.rmdir(self._CacheDir.path)
        # Should that be shutil.rmtree?

class CacheDirTestCase(BaseTestCase):
    """
    Test calling CacheDir code directly.
    """
    def test_cachepath(self):
        """Test the cachepath() method"""

        # Verify how the cachepath() method determines the name
        # of the file in cache.
        def my_collect(list):
            return list[0]
        save_collect = SCons.Util.MD5collect
        SCons.Util.MD5collect = my_collect

        try:
            name = 'a_fake_bsig'
            f5 = self.File("cd.f5", name)
            result = self._CacheDir.cachepath(f5)
            len = self._CacheDir.config['prefix_len']
            dirname = os.path.join('cache', name.upper()[:len])
            filename = os.path.join(dirname, name)
            assert result == (dirname, filename), result
        finally:
            SCons.Util.MD5collect = save_collect

class FileTestCase(BaseTestCase):
    """
    Test calling CacheDir code through Node.FS.File interfaces.
    """
    # These tests were originally in Nodes/FSTests.py and got moved
    # when the CacheDir support was refactored into its own module.
    # Look in the history for Node/FSTests.py if any of this needs
    # to be re-examined.
    def retrieve_succeed(self, target, source, env, execute=1):
        self.retrieved.append(target)
        return 0

    def retrieve_fail(self, target, source, env, execute=1):
        self.retrieved.append(target)
        return 1

    def push(self, target, source, env):
        self.pushed.append(target)
        return 0

    def test_CacheRetrieve(self):
        """Test the CacheRetrieve() function"""

        save_CacheRetrieve = SCons.CacheDir.CacheRetrieve
        self.retrieved = []

        f1 = self.File("cd.f1")
        try:
            SCons.CacheDir.CacheRetrieve = self.retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f1.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f1], self.retrieved
            assert built_it is None, built_it

            SCons.CacheDir.CacheRetrieve = self.retrieve_fail
            self.retrieved = []
            built_it = None

            r = f1.retrieve_from_cache()
            assert not r, r
            assert self.retrieved == [f1], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.CacheDir.CacheRetrieve = save_CacheRetrieve

    def test_CacheRetrieveSilent(self):
        """Test the CacheRetrieveSilent() function"""

        save_CacheRetrieveSilent = SCons.CacheDir.CacheRetrieveSilent

        SCons.CacheDir.cache_show = 1

        f2 = self.File("cd.f2", 'f2_bsig')
        try:
            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f2.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f2], self.retrieved
            assert built_it is None, built_it

            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_fail
            self.retrieved = []
            built_it = None

            r = f2.retrieve_from_cache()
            assert r is False, r
            assert self.retrieved == [f2], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.CacheDir.CacheRetrieveSilent = save_CacheRetrieveSilent

    def test_CachePush(self):
        """Test the CachePush() function"""

        save_CachePush = SCons.CacheDir.CachePush

        SCons.CacheDir.CachePush = self.push

        try:
            self.pushed = []

            cd_f3 = self.test.workpath("cd.f3")
            f3 = self.File(cd_f3)
            f3.push_to_cache()
            assert self.pushed == [], self.pushed
            self.test.write(cd_f3, "cd.f3\n")
            f3.push_to_cache()
            assert self.pushed == [f3], self.pushed

            self.pushed = []

            cd_f4 = self.test.workpath("cd.f4")
            f4 = self.File(cd_f4)
            f4.visited()
            assert self.pushed == [], self.pushed
            self.test.write(cd_f4, "cd.f4\n")
            f4.clear()
            f4.visited()
            assert self.pushed == [], self.pushed
            SCons.CacheDir.cache_force = 1
            f4.clear()
            f4.visited()
            assert self.pushed == [f4], self.pushed
        finally:
            SCons.CacheDir.CachePush = save_CachePush

    def test_warning(self):
        """Test raising a warning if we can't copy a file to cache."""

        test = TestCmd(workdir='')

        save_copy2 = shutil.copy2
        def copy2(src, dst):
            raise OSError
        shutil.copy2 = copy2
        save_mkdir = os.mkdir
        def mkdir(dir, mode=0):
            pass
        os.mkdir = mkdir
        old_warn_exceptions = SCons.Warnings.warningAsException(1)
        SCons.Warnings.enableWarningClass(SCons.Warnings.CacheWriteErrorWarning)

        try:
            cd_f7 = self.test.workpath("cd.f7")
            self.test.write(cd_f7, "cd.f7\n")
            f7 = self.File(cd_f7, 'f7_bsig')

            warn_caught = 0
            try:
                f7.push_to_cache()
            except SCons.Errors.BuildError as e:
                assert e.exc_info[0] == SCons.Warnings.CacheWriteErrorWarning
                warn_caught = 1
            assert warn_caught
        finally:
            shutil.copy2 = save_copy2
            os.mkdir = save_mkdir
            SCons.Warnings.warningAsException(old_warn_exceptions)
            SCons.Warnings.suppressWarningClass(SCons.Warnings.CacheWriteErrorWarning)

    def test_no_strfunction(self):
        """Test handling no strfunction() for an action."""

        save_CacheRetrieveSilent = SCons.CacheDir.CacheRetrieveSilent

        f8 = self.File("cd.f8", 'f8_bsig')
        try:
            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f8.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f8], self.retrieved
            assert built_it is None, built_it

            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_fail
            self.retrieved = []
            built_it = None

            r = f8.retrieve_from_cache()
            assert r is False, r
            assert self.retrieved == [f8], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.CacheDir.CacheRetrieveSilent = save_CacheRetrieveSilent

if __name__ == "__main__":
    unittest.main()
# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
