#
# Copyright (c) 2001, 2002 Steven Knight
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

import SCons.Errors
import SCons.Node



built_it = None
built_target =  None
built_source =  None
cycle_detected = None

class Builder:
    def execute(self, **kw):
        global built_it, built_target, built_source
	built_it = 1
        built_target = kw['target']
        built_source = kw['source']
        return 0
    def get_contents(self, env):
        return 7

class NoneBuilder(Builder):
    def execute(self, **kw):
        apply(Builder.execute, (self,), kw)
        return None

class ListBuilder(Builder):
    def __init__(self, *nodes):
        self.nodes = nodes
    def execute(self, **kw):
        if hasattr(self, 'status'):
            return self.status
        for n in self.nodes:
            n.prepare()
        kw['target'] = self.nodes[0]
        self.status = apply(Builder.execute, (self,), kw)

class FailBuilder:
    def execute(self, **kw):
        return 1

class ExceptBuilder:
    def execute(self, **kw):
        raise SCons.Errors.BuildError

class ExceptBuilder2:
    def execute(self, **kw):
        raise "foo"

class Environment:
    def Dictionary(self, *args):
	pass



class NodeTestCase(unittest.TestCase):

    def test_BuildException(self):
	"""Test throwing an exception on build failure.
	"""
	node = SCons.Node.Node()
	node.builder_set(FailBuilder())
	node.env_set(Environment())
	try:
	    node.build()
	except SCons.Errors.BuildError:
	    pass
	else:
	    raise TestFailed, "did not catch expected BuildError"

        node = SCons.Node.Node()
        node.builder_set(ExceptBuilder())
        node.env_set(Environment())
        try:
            node.build()
        except SCons.Errors.BuildError:
            pass
        else:
            raise TestFailed, "did not catch expected BuildError"

        node = SCons.Node.Node()
        node.builder_set(ExceptBuilder2())
        node.env_set(Environment())
        try:
            node.build()
        except SCons.Errors.BuildError, e:
            # On a generic (non-BuildError) exception from a Builder,
            # the Node should throw a BuildError exception with
            # the args set to the exception value, type, and traceback.
            assert len(e.args) == 3, `e.args`
            assert e.args[0] == 'foo', e.args[0]
            assert e.args[1] is None
            assert type(e.args[2]) is type(sys.exc_traceback), e.args[2]
        else:
            raise TestFailed, "did not catch expected BuildError"

    def test_build(self):
	"""Test building a node
	"""
        global built_it

        class MyNode(SCons.Node.Node):
            def __init__(self, **kw):
                apply(SCons.Node.Node.__init__, (self,), kw)
                self.prepare_count = 0
            def __str__(self):
                return self.path
            def prepare(self):
                self.prepare_count = self.prepare_count+ 1
	# Make sure it doesn't blow up if no builder is set.
        node = MyNode()
	node.build()
	assert built_it == None

        node = MyNode()
	node.builder_set(Builder())
	node.env_set(Environment())
        node.path = "xxx"
        node.sources = ["yyy", "zzz"]
	node.build()
	assert built_it
        assert type(built_target) == type(MyNode()), type(built_target)
        assert str(built_target) == "xxx", str(built_target)
        assert built_source == ["yyy", "zzz"], built_source

        built_it = None
        node = MyNode()
        node.builder_set(NoneBuilder())
        node.env_set(Environment())
        node.path = "qqq"
        node.sources = ["rrr", "sss"]
        node.build()
        assert built_it
        assert type(built_target) == type(MyNode()), type(built_target)
        assert str(built_target) == "qqq", str(built_target)
        assert built_source == ["rrr", "sss"], built_source

        fff = MyNode()
        ggg = MyNode()
        lb = ListBuilder(fff, ggg)
        e = Environment()
        fff.builder_set(lb)
        fff.env_set(e)
        fff.path = "fff"
        ggg.builder_set(lb)
        ggg.env_set(e)
        ggg.path = "ggg"
        fff.sources = ["hhh", "iii"]
        ggg.sources = ["hhh", "iii"]

        built_it = None
        fff.build()
        assert built_it
        ggg.build()
        assert ggg.prepare_count== 1, ggg.prepare_count
        assert type(built_target) == type(MyNode()), type(built_target)
        assert str(built_target) == "fff", str(built_target)
        assert built_source == ["hhh", "iii"], built_source

        delattr(lb, 'status')
        fff.prepare_count = 0
        ggg.prepare_count = 0

        built_it = None
        ggg.build()
        #assert built_it
        fff.build()
        assert fff.prepare_count== 1, fff.prepare_count
        assert type(built_target) == type(MyNode()), type(built_target)
        assert str(built_target) == "fff", str(built_target)
        assert built_source == ["hhh", "iii"], built_source

    def test_builder_set(self):
	"""Test setting a Node's Builder
	"""
	node = SCons.Node.Node()
	b = Builder()
	node.builder_set(b)
	assert node.builder == b

    def test_builder_sig_adapter(self):
        """Test the node's adapter for builder signatures
        """
        node = SCons.Node.Node()
        node.builder_set(Builder())
        node.env_set(Environment())
        c = node.builder_sig_adapter().get_contents()
        assert c == 7, c

    def test_current(self):
        """Test the default current() method
        """
        node = SCons.Node.Node()
        assert node.current() is None

    def test_env_set(self):
	"""Test setting a Node's Environment
	"""
	node = SCons.Node.Node()
	e = Environment()
	node.env_set(e)
	assert node.env == e

    def test_set_bsig(self):
        """Test setting a Node's signature
        """
        node = SCons.Node.Node()
        node.set_bsig('www')
        assert node.bsig == 'www'

    def test_get_bsig(self):
        """Test fetching a Node's signature
        """
        node = SCons.Node.Node()
        node.set_bsig('xxx')
        assert node.get_bsig() == 'xxx'

    def test_set_csig(self):
        """Test setting a Node's signature
        """
        node = SCons.Node.Node()
        node.set_csig('yyy')
        assert node.csig == 'yyy'

    def test_get_csig(self):
        """Test fetching a Node's signature
        """
        node = SCons.Node.Node()
        node.set_csig('zzz')
        assert node.get_csig() == 'zzz'

    def test_store_sigs(self):
        """Test calling the method to store signatures
        """
        node = SCons.Node.Node()
        node.store_sigs()

    def test_set_precious(self):
        """Test setting a Node's precious value
        """
        node = SCons.Node.Node()
        node.set_precious()
        assert node.precious
        node.set_precious(7)
        assert node.precious == 7

    def test_add_dependency(self):
	"""Test adding dependencies to a Node's list.
	"""
	node = SCons.Node.Node()
	assert node.depends == []

        zero = SCons.Node.Node()
        try:
	    node.add_dependency(zero)
	except TypeError:
	    pass
        else:
            assert 0

        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()

        node.add_dependency([one])
        assert node.depends == [one]
        node.add_dependency([two, three])
        assert node.depends == [one, two, three]
        node.add_dependency([three, four, one])
        assert node.depends == [one, two, three, four]

        assert zero.get_parents() == []
        assert one.get_parents() == [node]
        assert two.get_parents() == [node]
        assert three.get_parents() == [node]
        assert four.get_parents() == [node]


    def test_add_source(self):
	"""Test adding sources to a Node's list.
	"""
	node = SCons.Node.Node()
	assert node.sources == []

        zero = SCons.Node.Node()
	try:
	    node.add_source(zero)
	except TypeError:
	    pass
        else:
            assert 0

        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()

        node.add_source([one])
        assert node.sources == [one]
        node.add_source([two, three])
        assert node.sources == [one, two, three]
        node.add_source([three, four, one])
        assert node.sources == [one, two, three, four]

        assert zero.get_parents() == []
        assert one.get_parents() == [node]
        assert two.get_parents() == [node]
        assert three.get_parents() == [node]
        assert four.get_parents() == [node]

    def test_add_implicit(self):
        """Test adding implicit (scanned) dependencies to a Node's list.
        """
        node = SCons.Node.Node()
        assert node.implicit == {}

        zero = SCons.Node.Node()
        try:
            node.add_source(zero)
        except TypeError:
            pass
        else:
            assert 0

        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()

        node.add_implicit([one], 1)
        assert node.implicit[1] == [one]
        node.add_implicit([two, three], 1)
        assert node.implicit[1] == [one, two, three]
        node.add_implicit([three, four, one], 1)
        assert node.implicit[1] == [one, two, three, four]

        assert zero.get_parents() == []
        assert one.get_parents() == [node]
        assert two.get_parents() == [node]
        assert three.get_parents() == [node]
        assert four.get_parents() == [node]

        node.add_implicit([one], 2)
        node.add_implicit([two, three], 3)
        node.add_implicit([three, four, one], 4)

        assert node.implicit[1] == [one, two, three, four]
        assert node.implicit[2] == [one]
        assert node.implicit[3] == [two, three]
        assert node.implicit[4] == [three, four, one]

    def test_add_ignore(self):
        """Test adding files whose dependencies should be ignored.
        """
        node = SCons.Node.Node()
        assert node.ignore == []

        zero = SCons.Node.Node()
        try:
            node.add_ignore(zero)
        except TypeError:
            pass
        else:
            assert 0

        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()

        node.add_ignore([one])
        assert node.ignore == [one]
        node.add_ignore([two, three])
        assert node.ignore == [one, two, three]
        node.add_ignore([three, four, one])
        assert node.ignore == [one, two, three, four]

        assert zero.get_parents() == []
        assert one.get_parents() == [node]
        assert two.get_parents() == [node]
        assert three.get_parents() == [node]
        assert four.get_parents() == [node]

    def test_scan(self):
        """Test Scanner functionality"""
        class DummyScanner:
            pass
        ds=DummyScanner()
        node = SCons.Node.Node()
        assert node.scanners == [], node.scanners
        node.scanner_set(ds)
        assert node.scanners == [ ds ], node.scanners
        node.scan()
        assert node.scanned[ds] == 1, node.scanned

    def test_children(self):
        """Test fetching the non-ignored "children" of a Node.
        """
	node = SCons.Node.Node()
        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()
        five = SCons.Node.Node()
        six = SCons.Node.Node()

        node.add_source([one, two, three])
        node.add_dependency([four, five, six])
        node.add_ignore([two, five])
        kids = node.children()
        assert len(kids) == 4
        assert one in kids
        assert not two in kids
        assert three in kids
        assert four in kids
        assert not five in kids
        assert six in kids

    def test_all_children(self):
        """Test fetching all the "children" of a Node.
        """
        node = SCons.Node.Node()
        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()
        five = SCons.Node.Node()
        six = SCons.Node.Node()

        node.add_source([one, two, three])
        node.add_dependency([four, five, six])
        node.add_ignore([two, five])
        kids = node.all_children()
        assert len(kids) == 6
        assert one in kids
        assert two in kids
        assert three in kids
        assert four in kids
        assert five in kids
        assert six in kids

    def test_state(self):
	"""Test setting and getting the state of a node
	"""
        node = SCons.Node.Node()
        assert node.get_state() == None
        node.set_state(SCons.Node.executing)
        assert node.get_state() == SCons.Node.executing
        assert SCons.Node.pending < SCons.Node.executing
        assert SCons.Node.executing < SCons.Node.up_to_date
        assert SCons.Node.up_to_date < SCons.Node.executed
        assert SCons.Node.executed < SCons.Node.failed

    def test_walker(self):
	"""Test walking a Node tree.
	"""

	class MyNode(SCons.Node.Node):
	    def __init__(self, name):
		SCons.Node.Node.__init__(self)
		self.name = name

    	n1 = MyNode("n1")

	nw = SCons.Node.Walker(n1)
        assert not nw.is_done()
	assert nw.next().name ==  "n1"
        assert nw.is_done()
	assert nw.next() == None

    	n2 = MyNode("n2")
    	n3 = MyNode("n3")
	n1.add_source([n2, n3])

	nw = SCons.Node.Walker(n1)
	assert nw.next().name ==  "n2"
	assert nw.next().name ==  "n3"
	assert nw.next().name ==  "n1"
	assert nw.next() == None

	n4 = MyNode("n4")
	n5 = MyNode("n5")
	n6 = MyNode("n6")
	n7 = MyNode("n7")
	n2.add_source([n4, n5])
	n3.add_dependency([n6, n7])

	nw = SCons.Node.Walker(n1)
	assert nw.next().name ==  "n4"
	assert nw.next().name ==  "n5"
        assert nw.history.has_key(n2)
	assert nw.next().name ==  "n2"
	assert nw.next().name ==  "n6"
	assert nw.next().name ==  "n7"
        assert nw.history.has_key(n3)
	assert nw.next().name ==  "n3"
        assert nw.history.has_key(n1)
	assert nw.next().name ==  "n1"
	assert nw.next() == None

        n8 = MyNode("n8")
        n8.add_dependency([n3])
        n7.add_dependency([n8])

        def cycle(node, stack):
            global cycle_detected
            cycle_detected = 1

        global cycle_detected

        nw = SCons.Node.Walker(n3, cycle_func = cycle)
        n = nw.next()
        assert n.name == "n6", n.name
        n = nw.next()
        assert n.name == "n8", n.name
        assert cycle_detected
        cycle_detected = None
        n = nw.next()
        assert n.name == "n7", n.name
        n = nw.next()
        assert nw.next() == None

    def test_children_are_executed(self):
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        n3 = SCons.Node.Node()
        n4 = SCons.Node.Node()

        n4.add_source([n3])
        n3.add_source([n1, n2])

        assert not n4.children_are_executed()
        assert not n3.children_are_executed()
        assert n2.children_are_executed()
        assert n1.children_are_executed()

        n1.set_state(SCons.Node.executed)
        assert not n4.children_are_executed()
        assert not n3.children_are_executed()
        assert n2.children_are_executed()
        assert n1.children_are_executed()

        n2.set_state(SCons.Node.executed)
        assert not n4.children_are_executed()
        assert n3.children_are_executed()
        assert n2.children_are_executed()
        assert n1.children_are_executed()

        n3.set_state(SCons.Node.executed)
        assert n4.children_are_executed()
        assert n3.children_are_executed()
        assert n2.children_are_executed()
        assert n1.children_are_executed()

    def test_rescan(self):
        """Test that built nodes are rescanned."""
        class DummyScanner:
            pass
        
        class TestNode(SCons.Node.Node):
            def scan(self):
                for scn in self.scanners:
                    if not self.scanned.has_key(scn):
                        n=SCons.Node.Node()
                        n.scanner_set(scn)
                        self.add_implicit([ n ], scn)
                    self.scanned[scn] = 1
        tn=TestNode()
        tn.builder_set(Builder())
        tn.env_set(Environment())
        ds = DummyScanner()
        tn.scanner_set(ds)
        tn.scan()
        map(lambda x: x.scan(), tn.depends)
        assert tn.scanned[ds]
        assert len(tn.implicit[ds]) == 1, tn.implicit
        tn.build()
        assert len(tn.implicit[ds]) == 2, tn.implicit
        for dep in tn.implicit[ds]:
            assert dep.scanned[ds] == 1

if __name__ == "__main__":
    suite = unittest.makeSuite(NodeTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
