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
import SCons.Sig
import SCons.Sig.MD5
import SCons.Sig.TimeStamp
import sys


class DummyFile:
    """A class that simulates a file for testing purposes"""
    def __init__(self, path, contents, timestamp, builder):
        self.path = path
        self.contents = contents
        self.timestamp = timestamp
        self.builder = builder

    def modify(self, contents, timestamp):
        self.contents = contents
        self.timestamp = timestamp

class DummyNode:
    """A node workalike for testing purposes"""

    def __init__(self, file):
        self.file = file
        self.path = file.path
        self.builder = file.builder
        self.depends = []
        self.ignore = []
        self.use_signature = 1
        self.bsig = None
        self.csig = None
        self.oldtime = 0
        self.oldbsig = 0
        self.oldcsig = 0
        self.always_build = 0

    def has_builder(self):
        return self.builder

    def get_contents(self):
        # a file that doesn't exist has no contents:
        assert self.exists()

        return self.file.contents

    def get_timestamp(self):
        # a file that doesn't exist has no timestamp:
        assert self.exists()

        return self.file.timestamp

    def exists(self):
        return not self.file.contents is None

    def cached_exists(self):
        try:
            return self.exists_cache
        except AttributeError:
            self.exists_cache = self.exists()
            return self.exists_cache

    def rexists(self):
        return not self.file.contents is None

    def children(self):
        return filter(lambda x, i=self.ignore: x not in i,
                      self.sources + self.depends)

    def all_children(self):
        return self.sources + self.depends

    def current(self):
        if not self.exists():
            return 0
        return None

    def calc_signature(self, calc):
        if self.has_builder():
            return calc.bsig(self)
        else:
            return calc.csig(self)

    def set_binfo(self, bsig, bkids, bkidsigs, bact, bactsig):
        self.bsig = bsig
        self.bkids = bkids
        self.bkidsigs = bkidsigs
        self.bact = bact
        self.bactsig = bactsig

    def get_bsig(self):
        return self.bsig

    def store_bsig(self):
        pass

    def set_csig(self, csig):
        self.csig = csig

    def get_csig(self):
        return self.csig

    def store_csig(self):
        pass

    def get_prevsiginfo(self):
        return (self.oldtime, self.oldbsig, self.oldcsig)

    def get_stored_implicit(self):
        return None
    
    def store_timestamp(self):
        pass

    def get_executor(self):
        class Adapter:
            def get_contents(self):
                return 111
            def get_timestamp(self):
                return 222
        return Adapter()


def create_files(test):
    args  = [(test.workpath('f1.c'), 'blah blah', 111, 0),     #0
             (test.workpath('f1'), None, 0, 1),                #1
             (test.workpath('d1/f1.c'), 'blah blah', 111, 0),  #2
             (test.workpath('d1/f1.h'), 'blah blah', 111, 0),  #3
             (test.workpath('d1/f2.c'), 'blah blah', 111, 0),  #4
             (test.workpath('d1/f3.h'), 'blah blah', 111, 0),  #5
             (test.workpath('d1/f4.h'), 'blah blah', 111, 0),  #6
             (test.workpath('d1/f1'), None, 0, 1),             #7
             (test.workpath('d1/test.c'), 'blah blah', 111, 0),#8
             (test.workpath('d1/test.o'), None, 0, 1),         #9
             (test.workpath('d1/test'), None, 0, 1)]           #10

    files = map(lambda x: apply(DummyFile, x), args)

    return files

def create_nodes(files):
    nodes = map(DummyNode, files)

    nodes[0].sources = []
    nodes[1].sources = [nodes[0]]
    nodes[2].sources = []
    nodes[3].sources = []
    nodes[4].sources = []
    nodes[5].sources = [nodes[6]]
    nodes[6].sources = [nodes[5]]
    nodes[7].sources = [nodes[2], nodes[4], nodes[3], nodes[5]]
    nodes[8].sources = []
    nodes[9].sources = [nodes[8]]
    nodes[10].sources = [nodes[9]]

    return nodes

def current(calc, node):
    return calc.current(node, node.calc_signature(calc))

def write(calc, nodes):
    for node in nodes:
        node.oldtime = node.file.timestamp
        node.oldbsig = calc.bsig(node)
        node.oldcsig = calc.csig(node)

def clear(nodes):
    for node in nodes:
        node.csig = None
        node.bsig = None

class SigTestBase:

    def runTest(self):

        test = TestCmd.TestCmd(workdir = '')
        test.subdir('d1')

        self.files = create_files(test)
        self.test_initial()
        self.test_built()
        self.test_modify()
        self.test_modify_same_time()

    def test_initial(self):

        nodes = create_nodes(self.files)
        calc = SCons.Sig.Calculator(self.module)

        for node in nodes:
            self.failUnless(not current(calc, node),
                            "node %s should not be current" % node.path)

        # simulate a build:
        self.files[1].modify('built', 222)
        self.files[7].modify('built', 222)
        self.files[9].modify('built', 222)
        self.files[10].modify('built', 222)

    def test_built(self):

        nodes = create_nodes(self.files)

        calc = SCons.Sig.Calculator(self.module)

        write(calc, nodes)

        for node in nodes:
            self.failUnless(current(calc, node),
                            "node %s should be current" % node.path)

    def test_modify(self):

        nodes = create_nodes(self.files)

        calc = SCons.Sig.Calculator(self.module)

        write(calc, nodes)

        #simulate a modification of some files
        self.files[0].modify('blah blah blah', 333)
        self.files[3].modify('blah blah blah', 333)
        self.files[6].modify('blah blah blah', 333)
        self.files[8].modify('blah blah blah', 333)

        clear(nodes)

        self.failUnless(not current(calc, nodes[0]), "modified directly")
        self.failUnless(not current(calc, nodes[1]), "direct source modified")
        self.failUnless(current(calc, nodes[2]))
        self.failUnless(not current(calc, nodes[3]), "modified directly")
        self.failUnless(current(calc, nodes[4]))
        self.failUnless(current(calc, nodes[5]))
        self.failUnless(not current(calc, nodes[6]), "modified directly")
        self.failUnless(not current(calc, nodes[7]), "indirect source modified")
        self.failUnless(not current(calc, nodes[8]), "modified directory")
        self.failUnless(not current(calc, nodes[9]), "direct source modified")
        self.failUnless(not current(calc, nodes[10]), "indirect source modified")

    def test_modify_same_time(self):

        nodes = create_nodes(self.files)

        calc = SCons.Sig.Calculator(self.module, 0)

        write(calc, nodes)

        #simulate a modification of some files without changing the timestamp:
        self.files[0].modify('blah blah blah blah', 333)
        self.files[3].modify('blah blah blah blah', 333)
        self.files[6].modify('blah blah blah blah', 333)
        self.files[8].modify('blah blah blah blah', 333)

        clear(nodes)

        for node in nodes:
            self.failUnless(current(calc, node),
                            "node %s should be current" % node.path)


class MD5TestCase(unittest.TestCase, SigTestBase):
    """Test MD5 signatures"""

    module = SCons.Sig.MD5

class TimeStampTestCase(unittest.TestCase, SigTestBase):
    """Test timestamp signatures"""

    module = SCons.Sig.TimeStamp

class CalcTestCase(unittest.TestCase):

    def runTest(self):
        class MySigModule:
            def collect(self, signatures):
                return reduce(lambda x, y: x + y, signatures)
            def current(self, newsig, oldsig):
                return newsig == oldsig
            def signature(self, node):
                return node.get_csig()

        class MyNode:
            def __init__(self, name, bsig, csig):
                self.name = name
                self.bsig = bsig
                self.csig = csig
                self.kids = []
                self.ignore = []
                self.builder = None
                self.use_signature = 1
            def has_builder(self):
                return not self.builder is None
            def children(self):
                return filter(lambda x, i=self.ignore: x not in i, self.kids)
            def all_children(self):
                return self.kids
            def exists(self):
                return 1
            def cached_exists(self):
                return 1
            def get_bsig(self):
                return self.bsig
            def set_binfo(self, bsig, bkids, bkidsig, bact, bactsig):
                self.bsig = bsig
                self.bkids = bkids
                self.bkidsigs = bkidsigs
                self.bact = bact
                self.bactsig = bactsig
            def get_csig(self):
                return self.csig
            def set_csig(self, csig):
                self.csig = csig
            def store_csig(self):
                pass
            def store_timestamp(self):
                pass
            def get_prevsiginfo(self):
                return 0, self.bsig, self.csig
            def get_stored_implicit(self):
                return None
            def get_timestamp(self):
                return 1
            def builder_sig_adapter(self):
                class MyAdapter:
                    def get_csig(self):
                        return 333
                    def get_timestamp(self):
                        return 444
                return MyAdapter()

        self.module = MySigModule()
        self.nodeclass = MyNode
        self.test_Calc___init__()
        self.test_Calc_bsig()
        self.test_Calc_current()

    def test_Calc___init__(self):
        self.calc = SCons.Sig.Calculator(self.module)
        assert self.calc.module == self.module

    def test_Calc_bsig(self):
        n1 = self.nodeclass('n1', 11, 12)
        n2 = self.nodeclass('n2', 22, 23)
        n3 = self.nodeclass('n3', 33, 34)
        n1.builder = 1
        n1.kids = [n2, n3]

        assert self.calc.bsig(n1) == 55

        n1.ignore = [n2]

        assert self.calc.bsig(n1) == 33

    def test_Calc_bsig(self):
        n = self.nodeclass('n', 11, 12)

        assert self.calc.csig(n) == 12

    def test_Calc_current(self):
        class NN(self.nodeclass):
            always_build = 0
            def current(self):
                return None

        nn = NN('nn', 33, 34)
        assert not self.calc.current(nn, 30)
        assert self.calc.current(nn, 33)
        nn.always_build = 1
        assert not self.calc.current(nn, 33)

class SConsignEntryTestCase(unittest.TestCase):

    def runTest(self):
        e = SCons.Sig.SConsignEntry()
        assert e.timestamp == None
        assert e.csig == None
        assert e.bsig == None
        assert e.implicit == None

class _SConsignTestCase(unittest.TestCase):

    def runTest(self):
        class DummyModule:
            def to_string(self, sig):
                return str(sig)

            def from_string(self, sig):
                return int(sig)
            
        class DummyNode:
            path = 'not_a_valid_path'

        f = SCons.Sig._SConsign()
        f.set_binfo('foo', 1, ['f1'], ['f2'], 'foo act', 'foo actsig')
        assert f.get('foo') == (None, 1, None)
        f.set_csig('foo', 2)
        assert f.get('foo') == (None, 1, 2)
        f.set_timestamp('foo', 3)
        assert f.get('foo') == (3, 1, 2)
        f.set_implicit('foo', ['bar'])
        assert f.get('foo') == (3, 1, 2)
        assert f.get_implicit('foo') == ['bar']

        f = SCons.Sig._SConsign(DummyModule())
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
        save_SConsign_db = SCons.Sig.SConsign_db
        SCons.Sig.SConsign_db = {}
        try:
            d1 = SCons.Sig.SConsignDB(DummyNode('dir1'))
            d1.set_timestamp('foo', 1)
            d1.set_binfo('foo', 2, ['f1'], ['f2'], 'foo act', 'foo actsig')
            d1.set_csig('foo', 3)
            d1.set_timestamp('bar', 4)
            d1.set_binfo('bar', 5, ['b1'], ['b2'], 'bar act', 'bar actsig')
            d1.set_csig('bar', 6)
            assert d1.get('foo') == (1, 2, 3)
            assert d1.get('bar') == (4, 5, 6)

            d2 = SCons.Sig.SConsignDB(DummyNode('dir1'))
            d2.set_timestamp('foo', 7)
            d2.set_binfo('foo', 8, ['f3'], ['f4'], 'foo act', 'foo actsig')
            d2.set_csig('foo', 9)
            d2.set_timestamp('bar', 10)
            d2.set_binfo('bar', 11, ['b3'], ['b4'], 'bar act', 'bar actsig')
            d2.set_csig('bar', 12)
            assert d2.get('foo') == (7, 8, 9)
            assert d2.get('bar') == (10, 11, 12)
        finally:
            SCons.Sig.SConsign_db = save_SConsign_db

class SConsignDirFileTestCase(unittest.TestCase):

    def runTest(self):
        class DummyModule:
            def to_string(self, sig):
                return str(sig)

            def from_string(self, sig):
                return int(sig)
            
        class DummyNode:
            path = 'not_a_valid_path'

        f = SCons.Sig.SConsignDirFile(DummyNode(), DummyModule())
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

        assert SCons.Sig.SConsign_db is None, SCons.Sig.SConsign_db

        SCons.Sig.SConsignFile(file)

        assert not SCons.Sig.SConsign_db is None, SCons.Sig.SConsign_db

        class Fake_DBM:
            def open(self, name, mode):
                self.name = name
                self.mode = mode
                return self

        fake_dbm = Fake_DBM()

        SCons.Sig.SConsignFile(file, fake_dbm)

        assert not SCons.Sig.SConsign_db is None, SCons.Sig.SConsign_db
        assert not hasattr(fake_dbm, 'name'), fake_dbm
        assert not hasattr(fake_dbm, 'mode'), fake_dbm

        SCons.Sig.SConsign_db = None

        SCons.Sig.SConsignFile(file, fake_dbm)

        assert not SCons.Sig.SConsign_db is None, SCons.Sig.SConsign_db
        assert fake_dbm.name == file, fake_dbm.name
        assert fake_dbm.mode == "c", fake_dbm.mode



def suite():
    suite = unittest.TestSuite()
    suite.addTest(MD5TestCase())
    suite.addTest(TimeStampTestCase())
    suite.addTest(CalcTestCase())
    suite.addTest(SConsignEntryTestCase())
    suite.addTest(_SConsignTestCase())
    suite.addTest(SConsignDBTestCase())
    suite.addTest(SConsignDirFileTestCase())
    suite.addTest(SConsignFileTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)

