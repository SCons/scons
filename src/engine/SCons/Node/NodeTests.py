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
import types
import unittest

import SCons.Errors
import SCons.Node



built_it = None
built_target =  None
built_source =  None
cycle_detected = None
built_order = 0

class MyAction:
    def __init__(self):
        self.order = 0
        
    def __call__(self, target, source, env):
        global built_it, built_target, built_source, built_args, built_order
        built_it = 1
        built_target = target
        built_source = source
        built_args = env
        built_order = built_order + 1
        self.order = built_order
        return 0

class MyNonGlobalAction:
    def __init__(self):
        self.order = 0
        self.built_it = None
        self.built_target =  None
        self.built_source =  None

    def __call__(self, target, source, env):
        # Okay, so not ENTIRELY non-global...
        global built_order
        self.built_it = 1
        self.built_target = target
        self.built_source = source
        self.built_args = env
        built_order = built_order + 1
        self.order = built_order
        return 0

class Builder:
    def targets(self, t):
        return [t]
    def get_actions(self):
        return [MyAction()]
    def get_contents(self, target, source, env):
        return 7

class NoneBuilder(Builder):
    def execute(self, target, source, env):
        Builder.execute(self, target, source, env)
        return None

class ListBuilder(Builder):
    def __init__(self, *nodes):
        self.nodes = nodes
    def execute(self, target, source, env):
        if hasattr(self, 'status'):
            return self.status
        for n in self.nodes:
            n.prepare()
        target = self.nodes[0]
        self.status = Builder.execute(self, target, source, env)

class FailBuilder:
    def execute(self, target, source, env):
        return 1

class ExceptBuilder:
    def execute(self, target, source, env):
        raise SCons.Errors.BuildError

class ExceptBuilder2:
    def execute(self, target, source, env):
        raise "foo"

class Environment:
    def Dictionary(self, *args):
        return {}
    def Override(selv, overrides):
        return overrides

class Scanner:
    called = None
    def __call__(self, node):
        self.called = 1
        return node.found_includes

class MyNode(SCons.Node.Node):
    """The base Node class contains a number of do-nothing methods that
    we expect to be overridden by real, functional Node subclasses.  So
    simulate a real, functional Node subclass.
    """
    def __init__(self, name):
        SCons.Node.Node.__init__(self)
        self.name = name
        self.found_includes = []
    def __str__(self):
        return self.name
    def get_found_includes(self, env, scanner, target):
        return scanner(self)



class NodeTestCase(unittest.TestCase):

    def test_build(self):
        """Test building a node
        """
        global built_it, built_order

        # Make sure it doesn't blow up if no builder is set.
        node = MyNode("www")
        node.build()
        assert built_it == None

        node = MyNode("xxx")
        node.builder_set(Builder())
        node.env_set(Environment())
        node.path = "xxx"
        node.sources = ["yyy", "zzz"]
        node.build()
        assert built_it
        assert built_target[0] == node, built_target[0]
        assert built_source == ["yyy", "zzz"], built_source

        built_it = None
        node = MyNode("qqq")
        node.builder_set(NoneBuilder())
        node.env_set(Environment())
        node.path = "qqq"
        node.sources = ["rrr", "sss"]
        node.overrides = { "foo" : 1, "bar" : 2 }
        node.build()
        assert built_it
        assert built_target[0] == node, build_target[0]
        assert built_source == ["rrr", "sss"], built_source
        assert built_args["foo"] == 1, built_args
        assert built_args["bar"] == 2, built_args

        fff = MyNode("fff")
        ggg = MyNode("ggg")
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
        # [Charles C. 1/7/2002] Uhhh, why are there no asserts here?

        built_it = None
        built_order = 0
        node = MyNode("xxx")
        node.builder_set(Builder())
        node.env_set(Environment())
        node.sources = ["yyy", "zzz"]
        pre1 = MyNonGlobalAction()
        pre2 = MyNonGlobalAction()
        post1 = MyNonGlobalAction()
        post2 = MyNonGlobalAction()
        node.add_pre_action(pre1)
        node.add_pre_action(pre2)
        node.add_post_action(post1)
        node.add_post_action(post2)
        node.build()
        assert built_it
        assert pre1.built_it
        assert pre2.built_it
        assert post1.built_it
        assert post2.built_it
        assert pre1.order == 1, pre1.order
        assert pre2.order == 2, pre1.order
        # The action of the builder itself is order 3...
        assert post1.order == 4, pre1.order
        assert post2.order == 5, pre1.order

        for act in [ pre1, pre2, post1, post2 ]:
            assert type(act.built_target[0]) == type(MyNode("bar")), type(act.built_target[0])
            assert str(act.built_target[0]) == "xxx", str(act.built_target[0])
            assert act.built_source == ["yyy", "zzz"], act.built_source

    def test_visited(self):
        """Test the base visited() method

        Just make sure it's there and we can call it.
        """
        n = SCons.Node.Node()
        n.visited()
            
    def test_depends_on(self):
        """Test the depends_on() method
        """
        parent = SCons.Node.Node()
        child = SCons.Node.Node()
        parent.add_dependency([child])
        assert parent.depends_on([child])
        
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

    def test_get_actions(self):
        """Test fetching a Node's action list
        """
        node = SCons.Node.Node()
        node.builder_set(Builder())
        a = node.builder.get_actions()
        assert isinstance(a[0], MyAction), a[0]

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

    def test_store_bsig(self):
        """Test calling the method to store a build signature
        """
        node = SCons.Node.Node()
        node.store_bsig()

    def test_store_csig(self):
        """Test calling the method to store a content signature
        """
        node = SCons.Node.Node()
        node.store_csig()

    def test_get_timestamp(self):
        """Test calling the method to fetch a Node's timestamp
        """
        node = SCons.Node.Node()
        assert node.get_timestamp() == 0

    def test_store_timestamp(self):
        """Test calling the method to store a timestamp
        """
        node = SCons.Node.Node()
        node.store_timestamp()

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

    def test_get_found_includes(self):
        """Test the default get_found_includes() method
        """
        node = SCons.Node.Node()
        target = SCons.Node.Node()
        e = Environment()
        deps = node.get_found_includes(e, None, target)
        assert deps == [], deps

    def test_get_implicit_deps(self):
        """Test get_implicit_deps()
        """
        node = MyNode("nnn")
        target = MyNode("ttt")
        env = Environment()

        # No scanner at all returns []
        deps = node.get_implicit_deps(env, None, target)
        assert deps == [], deps

        s = Scanner()
        d = MyNode("ddd")
        node.found_includes = [d]

        # Simple return of the found includes
        deps = node.get_implicit_deps(env, s, target)
        assert deps == [d], deps

        # No "recursive" attribute on scanner doesn't recurse
        e = MyNode("eee")
        d.found_includes = [e]
        deps = node.get_implicit_deps(env, s, target)
        assert deps == [d], map(str, deps)

        # Explicit "recursive" attribute on scanner doesn't recurse
        s.recursive = None
        deps = node.get_implicit_deps(env, s, target)
        assert deps == [d], map(str, deps)

        # Explicit "recursive" attribute on scanner which does recurse
        s.recursive = 1
        deps = node.get_implicit_deps(env, s, target)
        assert deps == [d, e], map(str, deps)

        # Recursive scanning eliminates duplicates
        f = MyNode("fff")
        d.found_includes = [e, f]
        e.found_includes = [f]
        deps = node.get_implicit_deps(env, s, target)
        assert deps == [d, e, f], map(str, deps)

    def test_scan(self):
        """Test Scanner functionality
        """
        node = MyNode("nnn")
        node.builder = 1
        node.env_set(Environment())
        s = Scanner()

        d = MyNode("ddd")
        node.found_includes = [d]

        assert node.target_scanner == None, node.target_scanner
        node.target_scanner = s
        assert node.implicit is None

        node.scan()
        assert s.called
        assert node.implicit == [d], node.implicit

    def test_scanner_key(self):
        """Test that a scanner_key() method exists"""
        assert SCons.Node.Node().scanner_key() == None

    def test_children(self):
        """Test fetching the non-ignored "children" of a Node.
        """
        node = SCons.Node.Node()
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        n3 = SCons.Node.Node()
        n4 = SCons.Node.Node()
        n5 = SCons.Node.Node()
        n6 = SCons.Node.Node()
        n7 = SCons.Node.Node()
        n8 = SCons.Node.Node()
        n9 = SCons.Node.Node()
        n10 = SCons.Node.Node()
        n11 = SCons.Node.Node()
        n12 = SCons.Node.Node()

        node.add_source([n1, n2, n3])
        node.add_dependency([n4, n5, n6])
        node.implicit = []
        node._add_child(node.implicit, [n7, n8, n9])
        node._add_child(node.implicit, [n10, n11, n12])
        node.add_ignore([n2, n5, n8, n11])

        kids = node.children()
        for kid in [n1, n3, n4, n6, n7, n9, n10, n12]:
            assert kid in kids, kid
        for kid in [n2, n5, n8, n11]:
            assert not kid in kids, kid

    def test_all_children(self):
        """Test fetching all the "children" of a Node.
        """
        node = SCons.Node.Node()
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        n3 = SCons.Node.Node()
        n4 = SCons.Node.Node()
        n5 = SCons.Node.Node()
        n6 = SCons.Node.Node()
        n7 = SCons.Node.Node()
        n8 = SCons.Node.Node()
        n9 = SCons.Node.Node()
        n10 = SCons.Node.Node()
        n11 = SCons.Node.Node()
        n12 = SCons.Node.Node()

        node.add_source([n1, n2, n3])
        node.add_dependency([n4, n5, n6])
        node.implicit = []
        node._add_child(node.implicit, [n7, n8, n9])
        node._add_child(node.implicit, [n10, n11, n12])
        node.add_ignore([n2, n5, n8, n11])

        kids = node.all_children()
        for kid in [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12]:
            assert kid in kids, kid

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

    def test_rstr(self):
        """Test the rstr() method."""
        n1 = MyNode("n1")
        assert n1.rstr() == 'n1', n1.rstr()

    def test_arg2nodes(self):
        """Test the arg2nodes function."""
        dict = {}
        class X(SCons.Node.Node):
            pass
        def Factory(name, directory = None, create = 1, dict=dict, X=X):
            if not dict.has_key(name):
                dict[name] = X()
                dict[name].name = name
            return dict[name]

        nodes = SCons.Node.arg2nodes("Util.py UtilTests.py", Factory)
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], X)
        assert nodes[0].name == "Util.py UtilTests.py"

        if hasattr(types, 'UnicodeType'):
            code = """if 1:
                nodes = SCons.Node.arg2nodes(u"Util.py UtilTests.py", Factory)
                assert len(nodes) == 1, nodes
                assert isinstance(nodes[0], X)
                assert nodes[0].name == u"Util.py UtilTests.py"
                \n"""
            exec code in globals(), locals()

        nodes = SCons.Node.arg2nodes(["Util.py", "UtilTests.py"], Factory)
        assert len(nodes) == 2, nodes
        assert isinstance(nodes[0], X)
        assert isinstance(nodes[1], X)
        assert nodes[0].name == "Util.py"
        assert nodes[1].name == "UtilTests.py"

        n1 = Factory("Util.py")
        nodes = SCons.Node.arg2nodes([n1, "UtilTests.py"], Factory)
        assert len(nodes) == 2, nodes
        assert isinstance(nodes[0], X)
        assert isinstance(nodes[1], X)
        assert nodes[0].name == "Util.py"
        assert nodes[1].name == "UtilTests.py"

        class SConsNode(SCons.Node.Node):
            pass
        nodes = SCons.Node.arg2nodes(SConsNode())
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], SConsNode), node

        class OtherNode:
            pass
        nodes = SCons.Node.arg2nodes(OtherNode())
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], OtherNode), node

        def lookup_a(str, F=Factory):
            if str[0] == 'a':
                n = F(str)
                n.a = 1
                return n
            else:
                return None

        def lookup_b(str, F=Factory):
            if str[0] == 'b':
                n = F(str)
                n.b = 1
                return n
            else:
                return None

        SCons.Node.arg2nodes_lookups.append(lookup_a)
        SCons.Node.arg2nodes_lookups.append(lookup_b)

        nodes = SCons.Node.arg2nodes(['aaa', 'bbb', 'ccc'], Factory)
        assert len(nodes) == 3, nodes

        assert nodes[0].name == 'aaa', nodes[0]
        assert nodes[0].a == 1, nodes[0]
        assert not hasattr(nodes[0], 'b'), nodes[0]

        assert nodes[1].name == 'bbb'
        assert not hasattr(nodes[1], 'a'), nodes[1]
        assert nodes[1].b == 1, nodes[1]

        assert nodes[2].name == 'ccc'
        assert not hasattr(nodes[2], 'a'), nodes[1]
        assert not hasattr(nodes[2], 'b'), nodes[1]

        def lookup_bbbb(str, F=Factory):
            if str == 'bbbb':
                n = F(str)
                n.bbbb = 1
                return n
            else:
                return None

        def lookup_c(str, F=Factory):
            if str[0] == 'c':
                n = F(str)
                n.c = 1
                return n
            else:
                return None

        nodes = SCons.Node.arg2nodes(['bbbb', 'ccc'], Factory,
                                     [lookup_c, lookup_bbbb, lookup_b])
        assert len(nodes) == 2, nodes

        assert nodes[0].name == 'bbbb'
        assert not hasattr(nodes[0], 'a'), nodes[1]
        assert not hasattr(nodes[0], 'b'), nodes[1]
        assert nodes[0].bbbb == 1, nodes[1]
        assert not hasattr(nodes[0], 'c'), nodes[0]

        assert nodes[1].name == 'ccc'
        assert not hasattr(nodes[1], 'a'), nodes[1]
        assert not hasattr(nodes[1], 'b'), nodes[1]
        assert not hasattr(nodes[1], 'bbbb'), nodes[0]
        assert nodes[1].c == 1, nodes[1]
        
    def test_literal(self):
        """Test the is_literal() function."""
        n=SCons.Node.Node()
        assert n.is_literal()


if __name__ == "__main__":
    suite = unittest.makeSuite(NodeTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
