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

import unittest
import TestCmd
import SCons.SConsign
import sys

class SConsignEntryTestCase(unittest.TestCase):

    def runTest(self):
        e = SCons.SConsign.Entry()
        assert e.timestamp == None
        assert e.csig == None
        assert e.bsig == None
        assert e.implicit == None

class BaseTestCase(unittest.TestCase):

    def runTest(self):
        class DummyModule:
            def to_string(self, sig):
                return str(sig)

            def from_string(self, sig):
                return int(sig)
            
        class DummyNode:
            path = 'not_a_valid_path'

        f = SCons.SConsign.Base()
        f.set_binfo('foo', 1, ['f1'], ['f2'], 'foo act', 'foo actsig')
        assert f.get('foo') == (None, 1, None)
        f.set_csig('foo', 2)
        assert f.get('foo') == (None, 1, 2)
        f.set_timestamp('foo', 3)
        assert f.get('foo') == (3, 1, 2)
        f.set_implicit('foo', ['bar'])
        assert f.get('foo') == (3, 1, 2)
        assert f.get_implicit('foo') == ['bar']

        f = SCons.SConsign.Base(DummyModule())
        f.set_binfo('foo', 1, ['f1'], ['f2'], 'foo act', 'foo actsig')
        assert f.get('foo') == (None, 1, None)
        f.set_csig('foo', 2)
        assert f.get('foo') == (None, 1, 2)
        f.set_timestamp('foo', 3)
        assert f.get('foo') == (3, 1, 2)
        f.set_implicit('foo', ['bar'])
        assert f.get('foo') == (3, 1, 2)
        assert f.get_implicit('foo') == ['bar']

class SConsignDBTestCase(unittest.TestCase):

    def runTest(self):
        class DummyNode:
            def __init__(self, path):
                self.path = path
        save_database = SCons.SConsign.database
        SCons.SConsign.database = {}
        try:
            d1 = SCons.SConsign.DB(DummyNode('dir1'))
            d1.set_timestamp('foo', 1)
            d1.set_binfo('foo', 2, ['f1'], ['f2'], 'foo act', 'foo actsig')
            d1.set_csig('foo', 3)
            d1.set_timestamp('bar', 4)
            d1.set_binfo('bar', 5, ['b1'], ['b2'], 'bar act', 'bar actsig')
            d1.set_csig('bar', 6)
            assert d1.get('foo') == (1, 2, 3)
            assert d1.get('bar') == (4, 5, 6)

            d2 = SCons.SConsign.DB(DummyNode('dir1'))
            d2.set_timestamp('foo', 7)
            d2.set_binfo('foo', 8, ['f3'], ['f4'], 'foo act', 'foo actsig')
            d2.set_csig('foo', 9)
            d2.set_timestamp('bar', 10)
            d2.set_binfo('bar', 11, ['b3'], ['b4'], 'bar act', 'bar actsig')
            d2.set_csig('bar', 12)
            assert d2.get('foo') == (7, 8, 9)
            assert d2.get('bar') == (10, 11, 12)
        finally:
            SCons.SConsign.database = save_database

class SConsignDirFileTestCase(unittest.TestCase):

    def runTest(self):
        class DummyModule:
            def to_string(self, sig):
                return str(sig)

            def from_string(self, sig):
                return int(sig)
            
        class DummyNode:
            path = 'not_a_valid_path'

        f = SCons.SConsign.DirFile(DummyNode(), DummyModule())
        f.set_binfo('foo', 1, ['f1'], ['f2'], 'foo act', 'foo actsig')
        assert f.get('foo') == (None, 1, None)
        f.set_csig('foo', 2)
        assert f.get('foo') == (None, 1, 2)
        f.set_timestamp('foo', 3)
        assert f.get('foo') == (3, 1, 2)
        f.set_implicit('foo', ['bar'])
        assert f.get('foo') == (3, 1, 2)
        assert f.get_implicit('foo') == ['bar']

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



def suite():
    suite = unittest.TestSuite()
    suite.addTest(SConsignEntryTestCase())
    suite.addTest(BaseTestCase())
    suite.addTest(SConsignDBTestCase())
    suite.addTest(SConsignDirFileTestCase())
    suite.addTest(SConsignFileTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)

