#
# Copyright (c) 2001 Steven Knight
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
        self.use_signature = 1
        self.oldtime = 0
        self.oldsig = 0
        
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

    def children(self):
        return self.sources + self.depends

    def current(self):
        if not self.exists():
            return 0
        return None

    def has_signature(self):
        return hasattr(self, "sig")

    def set_signature(self, sig):
        self.sig = sig

    def get_signature(self):
        return self.sig

    def get_oldentry(self):
        return (self.oldtime, self.oldsig)


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
    nodes[2].sources = [nodes[3]]
    nodes[3].sources = []
    nodes[4].sources = [nodes[5]]
    nodes[5].sources = [nodes[6]]
    nodes[6].sources = [nodes[5]]
    nodes[7].sources = [nodes[2], nodes[4]]
    nodes[8].sources = []
    nodes[9].sources = [nodes[8]]
    nodes[10].sources = [nodes[9]]

    return nodes

def current(calc, node):
    s = calc.get_signature(node)
    return calc.current(node, s)

def write(calc, nodes):
    for node in nodes:
        node.oldtime = node.file.timestamp
        node.oldsig = calc.get_signature(node)
        

class SigTestBase:
    
    def runTest(self):

        test = TestCmd.TestCmd(workdir = '')
        test.subdir('d1')
        
        self.files = create_files(test)
        self.test_initial()
        self.test_built()
        self.test_modify()
        self.test_delete()
        
    def test_initial(self):
        
        nodes = create_nodes(self.files)
        calc = SCons.Sig.Calculator(self.module)

        for node in nodes:
            self.failUnless(not current(calc, node),
                            "none of the nodes should be current")

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
                            "all of the nodes should be current")

    def test_modify(self):

        nodes = create_nodes(self.files)

        calc = SCons.Sig.Calculator(self.module)

        write(calc, nodes)

        #simulate a modification of some files
        self.files[0].modify('blah blah blah', 333)
        self.files[3].modify('blah blah blah', 333)
        self.files[6].modify('blah blah blah', 333)
        self.files[8].modify('blah blah blah', 333)

        self.failUnless(not current(calc, nodes[0]), "modified directly")
        self.failUnless(not current(calc, nodes[1]), "direct source modified")
        self.failUnless(current(calc, nodes[2]))
        self.failUnless(not current(calc, nodes[3]), "modified directly")
        self.failUnless(current(calc, nodes[4]))
        self.failUnless(current(calc, nodes[5]))
        self.failUnless(not current(calc, nodes[6]), "modified directly")
        self.failUnless(current(calc, nodes[7]), "indirect source modified")
        self.failUnless(not current(calc, nodes[8]), "modified directory")
        self.failUnless(not current(calc, nodes[9]), "direct source modified")
        self.failUnless(not current(calc, nodes[10]), "indirect source modified")

    def test_delete(self):
        
        nodes = create_nodes(self.files)
        
        calc = SCons.Sig.Calculator(self.module)

        write(calc, nodes)

        #simulate the deletion of some files
        self.files[1].modify(None, 0)
        self.files[7].modify(None, 0)
        self.files[9].modify(None, 0)

        self.failUnless(current(calc, nodes[0]))
        self.failUnless(not current(calc, nodes[1]), "deleted")
        self.failUnless(current(calc, nodes[2]))
        self.failUnless(current(calc, nodes[3]))
        self.failUnless(current(calc, nodes[4]))
        self.failUnless(current(calc, nodes[5]))
        self.failUnless(current(calc, nodes[6]))
        self.failUnless(not current(calc, nodes[7]), "deleted")
        self.failUnless(current(calc, nodes[8]))
        self.failUnless(not current(calc, nodes[9]), "deleted")
        self.failUnless(current(calc, nodes[10]),
                        "current even though its source was deleted") 

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
                return node.get_signature()

        class MyNode:
            def __init__(self, name, sig):
                self.name = name
                self.sig = sig
                self.kids = []
                self.builder = None
                self.use_signature = 1
            def children(self):
                return self.kids
            def has_signature(self):
                return self.sig != None
            def get_signature(self):
                return self.sig
            def get_oldentry(self):
                return 0, self.sig
            def get_timestamp(self):
                return 1

        self.module = MySigModule()
        self.nodeclass = MyNode
        self.test_Calc___init__()
        self.test_Calc_collect()
        self.test_Calc_get_signature()
        self.test_Calc_current()

    def test_Calc___init__(self):
        self.calc = SCons.Sig.Calculator(self.module)
        assert self.calc.module == self.module

    def test_Calc_collect(self):
        n1 = self.nodeclass('n1', 11)
        n2 = self.nodeclass('n2', 22)
        n3 = self.nodeclass('n3', 33)
        n1.builder = 1
        n1.kids = [n2, n3]

        assert self.calc.collect(n1) == 55

    def test_Calc_get_signature(self):
        class NE(self.nodeclass):
            def exists(self):
                return 0
            def has_signature(self):
                return None
        class NN(self.nodeclass):
            def exists(self):
                return 1
            def has_signature(self):
                return None

        n1 = self.nodeclass('n1', 11)
        n1.use_signature = 0
        assert self.calc.get_signature(n1) is None

        n2 = self.nodeclass('n2', 22)
        assert self.calc.get_signature(n2) == 22

        n3 = self.nodeclass('n3', 33)
        n4 = self.nodeclass('n4', None)
        n4.builder = 1
        n4.kids = [n2, n3]
        assert self.calc.get_signature(n4) == 55

        n5 = NE('n5', 55)
        assert self.calc.get_signature(n5) is None

        n6 = NN('n6', 66)
        assert self.calc.get_signature(n6) == 66

    def test_Calc_current(self):
        class N0(self.nodeclass):
            def current(self):
                return 0
        class N1(self.nodeclass):
            def current(self):
                return 1
        class NN(self.nodeclass):
            def current(self):
                return None

        n0 = N0('n0', 11)
        assert not self.calc.current(n0, 10)
        assert not self.calc.current(n0, 11)

        n1 = N1('n1', 22)
        assert self.calc.current(n1, 20)
        assert self.calc.current(n1, 22)

        nn = NN('nn', 33)
        assert not self.calc.current(nn, 30)
        assert self.calc.current(nn, 33)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(MD5TestCase())
    suite.addTest(TimeStampTestCase())
    suite.addTest(CalcTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
    
