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
    def __init__(self, path, contents, timestamp, derived):
        self.path = path
        self.contents = contents
        self.timestamp = timestamp
        self.derived = derived

    def modify(self, contents, timestamp):
        self.contents = contents
        self.timestamp = timestamp

class DummyNode:
    """A node workalike for testing purposes"""

    def __init__(self, file):
        self.file = file
        self.path = file.path
        self.derived = file.derived
	self.depends = []
        
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
        
    def has_signature(self):
        return hasattr(self, "sig")

    def set_signature(self, sig):
        self.sig = sig

    def get_signature(self):
        return self.sig


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
            self.failUnless(not calc.current(node), "none of the nodes should be current")

        # simulate a build:
        self.files[1].modify('built', 222)
        self.files[7].modify('built', 222)
        self.files[9].modify('built', 222)
        self.files[10].modify('built', 222)
        
        calc.write(nodes)

    def test_built(self):

        nodes = create_nodes(self.files)

        calc = SCons.Sig.Calculator(self.module)
        
        for node in nodes:
            self.failUnless(calc.current(node), "all of the nodes should be current")

        calc.write(nodes)

    def test_modify(self):

        nodes = create_nodes(self.files)

        #simulate a modification of some files
        self.files[0].modify('blah blah blah', 333)
        self.files[3].modify('blah blah blah', 333)
        self.files[6].modify('blah blah blah', 333)
        self.files[8].modify('blah blah blah', 333)

        calc = SCons.Sig.Calculator(self.module)

        self.failUnless(not calc.current(nodes[0]), "modified directly")
        self.failUnless(not calc.current(nodes[1]), "direct source modified")
        self.failUnless(calc.current(nodes[2]))
        self.failUnless(not calc.current(nodes[3]), "modified directly")
        self.failUnless(calc.current(nodes[4]))
        self.failUnless(calc.current(nodes[5]))
        self.failUnless(not calc.current(nodes[6]), "modified directly")
        self.failUnless(not calc.current(nodes[7]), "indirect source modified")
        self.failUnless(not calc.current(nodes[8]), "modified directory")
        self.failUnless(not calc.current(nodes[9]), "direct source modified")
        self.failUnless(not calc.current(nodes[10]), "indirect source modified")

        calc.write(nodes)

    def test_delete(self):
        
        nodes = create_nodes(self.files)

        #simulate the deletion of some files
        self.files[1].modify(None, 0)
        self.files[7].modify(None, 0)
        self.files[9].modify(None, 0)
        
        calc = SCons.Sig.Calculator(self.module)

        self.failUnless(calc.current(nodes[0]))
        self.failUnless(not calc.current(nodes[1]), "deleted")
        self.failUnless(calc.current(nodes[2]))
        self.failUnless(calc.current(nodes[3]))
        self.failUnless(calc.current(nodes[4]))
        self.failUnless(calc.current(nodes[5]))
        self.failUnless(calc.current(nodes[6]))
        self.failUnless(not calc.current(nodes[7]), "deleted")
        self.failUnless(calc.current(nodes[8]))
        self.failUnless(not calc.current(nodes[9]), "deleted")
        self.failUnless(calc.current(nodes[10]),
                        "current even though it's source was deleted") 

        calc.write(nodes)

class MD5TestCase(unittest.TestCase, SigTestBase):
    """Test MD5 signatures"""

    module = SCons.Sig.MD5

class TimeStampTestCase(unittest.TestCase, SigTestBase):
    """Test timestamp signatures"""

    module = SCons.Sig.TimeStamp

def suite():
    suite = unittest.TestSuite()
    suite.addTest(MD5TestCase())
    suite.addTest(TimeStampTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
    
