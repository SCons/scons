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

import SCons.SConsign
import sys
import TestCmd
import unittest

class BuildInfo:
    def __init__(self, name):
        self.name = name

class DummyModule:
    def to_string(self, sig):
        return str(sig)

    def from_string(self, sig):
        return int(sig)

class BaseTestCase(unittest.TestCase):

    def runTest(self):
        class DummyNode:
            path = 'not_a_valid_path'

        aaa = BuildInfo('aaa')
        bbb = BuildInfo('bbb')
        bbb.arg1 = 'bbb arg1'
        ccc = BuildInfo('ccc')
        ccc.arg2 = 'ccc arg2'

        f = SCons.SConsign.Base()
        f.set_entry('aaa', aaa)
        f.set_entry('bbb', bbb)

        e = f.get_entry('aaa')
        assert e == aaa, e
        assert e.name == 'aaa', e.name

        e = f.get_entry('bbb')
        assert e == bbb, e
        assert e.name == 'bbb', e.name
        assert e.arg1 == 'bbb arg1', e.arg1
        assert not hasattr(e, 'arg2'), e

        f.set_entry('bbb', ccc)
        e = f.get_entry('bbb')
        assert e.name == 'ccc', e.name
        assert not hasattr(e, 'arg1'), e
        assert e.arg2 == 'ccc arg2', e.arg1

        ddd = BuildInfo('ddd')
        eee = BuildInfo('eee')
        fff = BuildInfo('fff')
        fff.arg = 'fff arg'

        f = SCons.SConsign.Base(DummyModule())
        f.set_entry('ddd', ddd)
        f.set_entry('eee', eee)

        e = f.get_entry('ddd')
        assert e == ddd, e
        assert e.name == 'ddd', e.name

        e = f.get_entry('eee')
        assert e == eee, e
        assert e.name == 'eee', e.name
        assert not hasattr(e, 'arg'), e

        f.set_entry('eee', fff)
        e = f.get_entry('eee')
        assert e.name == 'fff', e.name
        assert e.arg == 'fff arg', e.arg

class SConsignDBTestCase(unittest.TestCase):

    def runTest(self):
        class DummyNode:
            def __init__(self, path):
                self.path = path
        save_database = SCons.SConsign.database
        SCons.SConsign.database = {}
        try:
            d1 = SCons.SConsign.DB(DummyNode('dir1'))
            d1.set_entry('aaa', BuildInfo('aaa name'))
            d1.set_entry('bbb', BuildInfo('bbb name'))
            aaa = d1.get_entry('aaa')
            assert aaa.name == 'aaa name'
            bbb = d1.get_entry('bbb')
            assert bbb.name == 'bbb name'

            d2 = SCons.SConsign.DB(DummyNode('dir1'))
            d2.set_entry('ccc', BuildInfo('ccc name'))
            d2.set_entry('ddd', BuildInfo('ddd name'))
            ccc = d2.get_entry('ccc')
            assert ccc.name == 'ccc name'
            ddd = d2.get_entry('ddd')
            assert ddd.name == 'ddd name'
        finally:
            SCons.SConsign.database = save_database

class SConsignDirFileTestCase(unittest.TestCase):

    def runTest(self):
        class DummyNode:
            path = 'not_a_valid_path'

        foo = BuildInfo('foo')
        bar = BuildInfo('bar')

        f = SCons.SConsign.DirFile(DummyNode(), DummyModule())
        f.set_entry('foo', foo)
        f.set_entry('bar', bar)

        e = f.get_entry('foo')
        assert e == foo, e
        assert e.name == 'foo', e.name

        e = f.get_entry('bar')
        assert e == bar, e
        assert e.name == 'bar', e.name
        assert not hasattr(e, 'arg'), e

        bbb = BuildInfo('bbb')
        bbb.arg = 'bbb arg'
        f.set_entry('bar', bbb)
        e = f.get_entry('bar')
        assert e.name == 'bbb', e.name
        assert e.arg == 'bbb arg', e.arg


class SConsignFileTestCase(unittest.TestCase):

    def runTest(self):
        test = TestCmd.TestCmd(workdir = '')
        file = test.workpath('sconsign_file')

        assert SCons.SConsign.database is None, SCons.SConsign.database

        SCons.SConsign.File(file)

        assert not SCons.SConsign.database is SCons.dblite, SCons.SConsign.database

        class Fake_DBM:
            def open(self, name, mode):
                self.name = name
                self.mode = mode
                return self

        fake_dbm = Fake_DBM()

        SCons.SConsign.File(file, fake_dbm)

        assert not SCons.SConsign.database is None, SCons.SConsign.database
        assert not hasattr(fake_dbm, 'name'), fake_dbm
        assert not hasattr(fake_dbm, 'mode'), fake_dbm

        SCons.SConsign.database = None

        SCons.SConsign.File(file, fake_dbm)

        assert not SCons.SConsign.database is None, SCons.SConsign.database
        assert fake_dbm.name == file, fake_dbm.name
        assert fake_dbm.mode == "c", fake_dbm.mode


class writeTestCase(unittest.TestCase):

    def runTest(self):

        class DummyNode:
            path = 'not_a_valid_path'

        test = TestCmd.TestCmd(workdir = '')
        file = test.workpath('sconsign_file')

        class Fake_DBM:
            def __setitem__(self, key, value):
                pass
            def open(self, name, mode):
                self.sync_count = 0
                return self
            def sync(self):
                self.sync_count = self.sync_count + 1

        fake_dbm = Fake_DBM()

        SCons.SConsign.database = None
        SCons.SConsign.File(file, fake_dbm)

        f = SCons.SConsign.DirFile(DummyNode(), DummyModule())

        f.set_entry('foo', BuildInfo('foo'))
        f.set_entry('bar', BuildInfo('bar'))

        SCons.SConsign.write()

        assert fake_dbm.sync_count == 1, fake_dbm.sync_count


def suite():
    suite = unittest.TestSuite()
    suite.addTest(BaseTestCase())
    suite.addTest(SConsignDBTestCase())
    suite.addTest(SConsignDirFileTestCase())
    suite.addTest(SConsignFileTestCase())
    suite.addTest(writeTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)

