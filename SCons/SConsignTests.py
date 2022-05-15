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

import TestCmd

import SCons.dblite
import SCons.SConsign
from SCons.Util import get_hash_format, get_current_hash_algorithm_used

class BuildInfo:
    def merge(self, object):
        pass

class DummySConsignEntry:
    def __init__(self, name):
        self.name = name
        self.binfo = BuildInfo()
    def convert_to_sconsign(self):
        self.c_to_s = 1
    def convert_from_sconsign(self, dir, name):
        self.c_from_s = 1

class FS:
    def __init__(self, top):
        self.Top = top
        self.Top.repositories = []

class DummyNode:
    def __init__(self, path='not_a_valid_path', binfo=None):
        self.path = path
        self.tpath = path
        self.fs = FS(self)
        self.binfo = binfo
    def get_stored_info(self):
        return self.binfo
    def get_binfo(self):
        return self.binfo
    def get_internal_path(self):
        return self.path
    def get_tpath(self):
        return self.tpath

class SConsignTestCase(unittest.TestCase):
    def setUp(self):
        self.save_cwd = os.getcwd()
        self.test = TestCmd.TestCmd(workdir = '')
        os.chdir(self.test.workpath(''))
    def tearDown(self):
        self.test.cleanup()
        SCons.SConsign.Reset()
        os.chdir(self.save_cwd)

class BaseTestCase(SConsignTestCase):

    def test_Base(self):
        aaa = DummySConsignEntry('aaa')
        bbb = DummySConsignEntry('bbb')
        bbb.arg1 = 'bbb arg1'
        ccc = DummySConsignEntry('ccc')
        ccc.arg2 = 'ccc arg2'

        f = SCons.SConsign.Base()
        f.set_entry('aaa', aaa)
        f.set_entry('bbb', bbb)

        #f.merge()

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

        ddd = DummySConsignEntry('ddd')
        eee = DummySConsignEntry('eee')
        fff = DummySConsignEntry('fff')
        fff.arg = 'fff arg'

        f = SCons.SConsign.Base()
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

    def test_store_info(self):
        aaa = DummySConsignEntry('aaa')
        bbb = DummySConsignEntry('bbb')
        bbb.arg1 = 'bbb arg1'
        ccc = DummySConsignEntry('ccc')
        ccc.arg2 = 'ccc arg2'

        f = SCons.SConsign.Base()
        f.store_info('aaa', DummyNode('aaa', aaa))
        f.store_info('bbb', DummyNode('bbb', bbb))

        try:
            e = f.get_entry('aaa')
        except KeyError:
            pass
        else:
            raise Exception("unexpected entry %s" % e)

        try:
            e = f.get_entry('bbb')
        except KeyError:
            pass
        else:
            raise Exception("unexpected entry %s" % e)

        f.merge()

        e = f.get_entry('aaa')
        assert e == aaa, "aaa = %s, e = %s" % (aaa, e)
        assert e.name == 'aaa', e.name

        e = f.get_entry('bbb')
        assert e == bbb, "bbb = %s, e = %s" % (bbb, e)
        assert e.name == 'bbb', e.name
        assert e.arg1 == 'bbb arg1', e.arg1
        assert not hasattr(e, 'arg2'), e

        f.store_info('bbb', DummyNode('bbb', ccc))

        e = f.get_entry('bbb')
        assert e == bbb, e
        assert e.name == 'bbb', e.name
        assert e.arg1 == 'bbb arg1', e.arg1
        assert not hasattr(e, 'arg2'), e

        f.merge()

        e = f.get_entry('bbb')
        assert e.name == 'ccc', e.name
        assert not hasattr(e, 'arg1'), e
        assert e.arg2 == 'ccc arg2', e.arg1

        ddd = DummySConsignEntry('ddd')
        eee = DummySConsignEntry('eee')
        fff = DummySConsignEntry('fff')
        fff.arg = 'fff arg'

        f = SCons.SConsign.Base()
        f.store_info('ddd', DummyNode('ddd', ddd))
        f.store_info('eee', DummyNode('eee', eee))

        f.merge()

        e = f.get_entry('ddd')
        assert e == ddd, e
        assert e.name == 'ddd', e.name

        e = f.get_entry('eee')
        assert e == eee, e
        assert e.name == 'eee', e.name
        assert not hasattr(e, 'arg'), e

        f.store_info('eee', DummyNode('eee', fff))

        e = f.get_entry('eee')
        assert e == eee, e
        assert e.name == 'eee', e.name
        assert not hasattr(e, 'arg'), e

        f.merge()

        e = f.get_entry('eee')
        assert e.name == 'fff', e.name
        assert e.arg == 'fff arg', e.arg

class SConsignDBTestCase(SConsignTestCase):

    def test_SConsignDB(self):
        save_DataBase = SCons.SConsign.DataBase
        SCons.SConsign.DataBase = {}
        try:
            d1 = SCons.SConsign.DB(DummyNode('dir1'))
            d1.set_entry('aaa', DummySConsignEntry('aaa name'))
            d1.set_entry('bbb', DummySConsignEntry('bbb name'))

            aaa = d1.get_entry('aaa')
            assert aaa.name == 'aaa name'
            bbb = d1.get_entry('bbb')
            assert bbb.name == 'bbb name'

            d2 = SCons.SConsign.DB(DummyNode('dir2'))
            d2.set_entry('ccc', DummySConsignEntry('ccc name'))
            d2.set_entry('ddd', DummySConsignEntry('ddd name'))

            ccc = d2.get_entry('ccc')
            assert ccc.name == 'ccc name'
            ddd = d2.get_entry('ddd')
            assert ddd.name == 'ddd name'

            d31 = SCons.SConsign.DB(DummyNode('dir3/sub1'))
            d31.set_entry('eee', DummySConsignEntry('eee name'))
            d31.set_entry('fff', DummySConsignEntry('fff name'))

            eee = d31.get_entry('eee')
            assert eee.name == 'eee name'
            fff = d31.get_entry('fff')
            assert fff.name == 'fff name'

            d32 = SCons.SConsign.DB(DummyNode('dir3%ssub2' % os.sep))
            d32.set_entry('ggg', DummySConsignEntry('ggg name'))
            d32.set_entry('hhh', DummySConsignEntry('hhh name'))

            ggg = d32.get_entry('ggg')
            assert ggg.name == 'ggg name'
            hhh = d32.get_entry('hhh')
            assert hhh.name == 'hhh name'

        finally:

            SCons.SConsign.DataBase = save_DataBase

class SConsignDirFileTestCase(SConsignTestCase):

    def test_SConsignDirFile(self):
        bi_foo = DummySConsignEntry('foo')
        bi_bar = DummySConsignEntry('bar')

        f = SCons.SConsign.DirFile(DummyNode())
        f.set_entry('foo', bi_foo)
        f.set_entry('bar', bi_bar)

        e = f.get_entry('foo')
        assert e == bi_foo, e
        assert e.name == 'foo', e.name

        e = f.get_entry('bar')
        assert e == bi_bar, e
        assert e.name == 'bar', e.name
        assert not hasattr(e, 'arg'), e

        bbb = DummySConsignEntry('bbb')
        bbb.arg = 'bbb arg'

        f.set_entry('bar', bbb)

        e = f.get_entry('bar')
        assert e.name == 'bbb', e.name
        assert e.arg == 'bbb arg', e.arg


class SConsignFileTestCase(SConsignTestCase):

    def test_SConsignFile(self):
        test = self.test
        file = test.workpath('sconsign_file')

        assert SCons.SConsign.DataBase == {}, SCons.SConsign.DataBase
        if get_hash_format() is None and get_current_hash_algorithm_used() == 'md5':
            assert SCons.SConsign.DB_Name == ".sconsign", SCons.SConsign.DB_Name
        else:
            assert SCons.SConsign.DB_Name == ".sconsign_{}".format(get_current_hash_algorithm_used()), SCons.SConsign.DB_Name
        assert SCons.SConsign.DB_Module is SCons.dblite, SCons.SConsign.DB_Module

        SCons.SConsign.File(file)

        assert SCons.SConsign.DataBase == {}, SCons.SConsign.DataBase
        assert SCons.SConsign.DB_Name is file, SCons.SConsign.DB_Name
        assert SCons.SConsign.DB_Module is SCons.dblite, SCons.SConsign.DB_Module

        SCons.SConsign.File(None)

        assert SCons.SConsign.DataBase == {}, SCons.SConsign.DataBase
        assert SCons.SConsign.DB_Name is file, SCons.SConsign.DB_Name
        assert SCons.SConsign.DB_Module is None, SCons.SConsign.DB_Module

        class Fake_DBM:
            def open(self, name, mode):
                self.name = name
                self.mode = mode
                return self
            def __getitem__(self, key):
                pass
            def __setitem__(self, key, value):
                pass

        fake_dbm = Fake_DBM()

        SCons.SConsign.File(file, fake_dbm)

        assert SCons.SConsign.DataBase == {}, SCons.SConsign.DataBase
        assert SCons.SConsign.DB_Name is file, SCons.SConsign.DB_Name
        assert SCons.SConsign.DB_Module is fake_dbm, SCons.SConsign.DB_Module
        assert not hasattr(fake_dbm, 'name'), fake_dbm
        assert not hasattr(fake_dbm, 'mode'), fake_dbm

        SCons.SConsign.ForDirectory(DummyNode(test.workpath('dir')))

        assert SCons.SConsign.DataBase is not None, SCons.SConsign.DataBase
        assert fake_dbm.name == file, fake_dbm.name
        assert fake_dbm.mode == "c", fake_dbm.mode


class writeTestCase(SConsignTestCase):

    def test_write(self):

        test = self.test
        file = test.workpath('sconsign_file')

        class Fake_DBM:
            def __getitem__(self, key):
                return None
            def __setitem__(self, key, value):
                pass
            def open(self, name, mode):
                self.sync_count = 0
                return self
            def sync(self):
                self.sync_count = self.sync_count + 1

        fake_dbm = Fake_DBM()

        SCons.SConsign.DataBase = {}
        SCons.SConsign.File(file, fake_dbm)

        f = SCons.SConsign.DB(DummyNode())

        bi_foo = DummySConsignEntry('foo')
        bi_bar = DummySConsignEntry('bar')
        f.set_entry('foo', bi_foo)
        f.set_entry('bar', bi_bar)

        SCons.SConsign.write()

        assert bi_foo.c_to_s, bi_foo.c_to_s
        assert bi_bar.c_to_s, bi_bar.c_to_s

        assert fake_dbm.sync_count == 1, fake_dbm.sync_count



if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
