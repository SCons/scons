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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import SCons.compat

import collections
import os
import re
import sys
import unittest

import SCons.Errors
import SCons.Node
import SCons.Util



built_it = None
built_target =  None
built_source =  None
cycle_detected = None
built_order = 0

def _actionAppend(a1, a2):
    all = []
    for curr_a in [a1, a2]:
        if isinstance(curr_a, MyAction):
            all.append(curr_a)
        elif isinstance(curr_a, MyListAction):
            all.extend(curr_a.list)
        elif isinstance(curr_a, list):
            all.extend(curr_a)
        else:
            raise Exception('Cannot Combine Actions')
    return MyListAction(all)

class MyActionBase(object):
    def __add__(self, other):
        return _actionAppend(self, other)

    def __radd__(self, other):
        return _actionAppend(other, self)

class MyAction(MyActionBase):
    def __init__(self):
        self.order = 0

    def __call__(self, target, source, env, executor=None):
        global built_it, built_target, built_source, built_args, built_order
        if executor:
            target = executor.get_all_targets()
            source = executor.get_all_sources()
        built_it = 1
        built_target = target
        built_source = source
        built_args = env
        built_order = built_order + 1
        self.order = built_order
        return 0

    def get_implicit_deps(self, target, source, env):
        return []

class MyExecutor(object):
    def __init__(self, env=None, targets=[], sources=[]):
        self.env = env
        self.targets = targets
        self.sources = sources
    def get_build_env(self):
        return self.env
    def get_build_scanner_path(self, scanner):
        return 'executor would call %s' % scanner
    def cleanup(self):
        self.cleaned_up = 1
    def scan_targets(self, scanner):
        if not scanner:
            return
        d = scanner(self.targets)
        for t in self.targets:
            t.implicit.extend(d)
    def scan_sources(self, scanner):
        if not scanner:
            return
        d = scanner(self.sources)
        for t in self.targets:
            t.implicit.extend(d)

class MyListAction(MyActionBase):
    def __init__(self, list):
        self.list = list
    def __call__(self, target, source, env):
        for A in self.list:
            A(target, source, env)

class Environment(object):
    def __init__(self, **kw):
        self._dict = {}
        self._dict.update(kw)
    def __getitem__(self, key):
        return self._dict[key]
    def get(self, key, default = None):
        return self._dict.get(key, default)
    def Dictionary(self, *args):
        return {}
    def Override(self, overrides):
        d = self._dict.copy()
        d.update(overrides)
        return Environment(**d)
    def _update(self, dict):
        self._dict.update(dict)
    def get_factory(self, factory):
        return factory or MyNode
    def get_scanner(self, scanner_key):
        try:
            return self._dict['SCANNERS'][0]
        except:
            pass

        return []

class Builder(object):
    def __init__(self, env=None, is_explicit=1):
        if env is None: env = Environment()
        self.env = env
        self.overrides = {}
        self.action = MyAction()
        self.source_factory = MyNode
        self.is_explicit = is_explicit
        self.target_scanner = None
        self.source_scanner = None
    def targets(self, t):
        return [t]
    def get_actions(self):
        return [self.action]
    def get_contents(self, target, source, env):
        return 7

class NoneBuilder(Builder):
    def execute(self, target, source, env):
        Builder.execute(self, target, source, env)
        return None

class ListBuilder(Builder):
    def __init__(self, *nodes):
        Builder.__init__(self)
        self.nodes = nodes
    def execute(self, target, source, env):
        if hasattr(self, 'status'):
            return self.status
        for n in self.nodes:
            n.prepare()
        target = self.nodes[0]
        self.status = Builder.execute(self, target, source, env)

class FailBuilder(object):
    def execute(self, target, source, env):
        return 1

class ExceptBuilder(object):
    def execute(self, target, source, env):
        raise SCons.Errors.BuildError

class ExceptBuilder2(object):
    def execute(self, target, source, env):
        raise Exception("foo")

class Scanner(object):
    called = None
    def __call__(self, node):
        self.called = 1
        return node.GetTag('found_includes')
    def path(self, env, dir=None, target=None, source=None, kw={}):
        return ()
    def select(self, node):
        return self
    def recurse_nodes(self, nodes):
        return nodes

class MyNode(SCons.Node.Node):
    """The base Node class contains a number of do-nothing methods that
    we expect to be overridden by real, functional Node subclasses.  So
    simulate a real, functional Node subclass.
    """
    def __init__(self, name):
        SCons.Node.Node.__init__(self)
        self.name = name
        self.Tag('found_includes', [])
    def __str__(self):
        return self.name
    def get_found_includes(self, env, scanner, target):
        return scanner(self)

class Calculator(object):
    def __init__(self, val):
        self.max_drift = 0
        class M(object):
            def __init__(self, val):
                self.val = val
            def signature(self, args):
                return self.val
            def collect(self, args):
                result = self.val
                for a in args:
                    result += a
                return result
        self.module = M(val)



class NodeInfoBaseTestCase(unittest.TestCase):
    # The abstract class NodeInfoBase has not enough default slots to perform
    # the merge and format test (arbitrary attributes do not work). Do it with a
    # derived class that does provide the slots.

    def test_merge(self):
        """Test merging NodeInfoBase attributes"""

        class TestNodeInfo(SCons.Node.NodeInfoBase):
            __slots__ = ('a1', 'a2', 'a3')

        ni1 = TestNodeInfo()
        ni2 = TestNodeInfo()

        ni1.a1 = 1
        ni1.a2 = 2

        ni2.a2 = 222
        ni2.a3 = 333

        ni1.merge(ni2)
        assert ni1.a1 == 1, ni1.a1
        assert ni1.a2 == 222, ni1.a2
        assert ni1.a3 == 333, ni1.a3

    def test_update(self):
        """Test the update() method"""
        ni = SCons.Node.NodeInfoBase()
        ni.update(SCons.Node.Node())

    def test_format(self):
        """Test the NodeInfoBase.format() method"""

        class TestNodeInfo(SCons.Node.NodeInfoBase):
            __slots__ = ('xxx', 'yyy', 'zzz')

        ni1 = TestNodeInfo()
        ni1.xxx = 'x'
        ni1.yyy = 'y'
        ni1.zzz = 'z'

        f = ni1.format()
        assert f == ['x', 'y', 'z'], f
 
        field_list = ['xxx', 'zzz', 'aaa']

        f = ni1.format(field_list)
        assert f == ['x', 'z', 'None'], f



class BuildInfoBaseTestCase(unittest.TestCase):

    def test___init__(self):
        """Test BuildInfoBase initialization"""
        n = SCons.Node.Node()
        bi = SCons.Node.BuildInfoBase()
        assert bi

    def test_merge(self):
        """Test merging BuildInfoBase attributes"""
        n1 = SCons.Node.Node()
        bi1 = SCons.Node.BuildInfoBase()
        n2 = SCons.Node.Node()
        bi2 = SCons.Node.BuildInfoBase()

        bi1.bsources = 1
        bi1.bdepends = 2

        bi2.bdepends = 222
        bi2.bact = 333

        bi1.merge(bi2)
        assert bi1.bsources == 1, bi1.bsources
        assert bi1.bdepends == 222, bi1.bdepends
        assert bi1.bact == 333, bi1.bact


class NodeTestCase(unittest.TestCase):

    def test_build(self):
        """Test building a node
        """
        global built_it, built_order

        # Make sure it doesn't blow up if no builder is set.
        node = MyNode("www")
        node.build()
        assert built_it is None
        node.build(extra_kw_argument = 1)
        assert built_it is None

        node = MyNode("xxx")
        node.builder_set(Builder())
        node.env_set(Environment())
        node.path = "xxx"
        node.sources = ["yyy", "zzz"]
        node.build()
        assert built_it
        assert built_target == [node], built_target
        assert built_source == ["yyy", "zzz"], built_source

        built_it = None
        node = MyNode("qqq")
        node.builder_set(NoneBuilder())
        node.env_set(Environment())
        node.path = "qqq"
        node.sources = ["rrr", "sss"]
        node.builder.overrides = { "foo" : 1, "bar" : 2 }
        node.build()
        assert built_it
        assert built_target == [node], built_target
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
        built_it = None
        fff.build()
        assert built_it
        assert built_target == [fff], built_target
        assert built_source == ["hhh", "iii"], built_source
        built_it = None
        ggg.build()
        assert built_it
        assert built_target == [ggg], built_target
        assert built_source == ["hhh", "iii"], built_source

        built_it = None
        jjj = MyNode("jjj")
        b = Builder()
        jjj.builder_set(b)
        # NOTE:  No env_set()!  We should pull the environment from the builder.
        b.env = Environment()
        b.overrides = { "on" : 3, "off" : 4 }
        e.builder = b
        jjj.build()
        assert built_it
        assert built_target[0] == jjj, built_target[0]
        assert built_source == [], built_source
        assert built_args["on"] == 3, built_args
        assert built_args["off"] == 4, built_args

    def test_get_build_scanner_path(self):
        """Test the get_build_scanner_path() method"""
        n = SCons.Node.Node()
        x = MyExecutor()
        n.set_executor(x)
        p = n.get_build_scanner_path('fake_scanner')
        assert p == "executor would call fake_scanner", p

    def test_get_executor(self):
        """Test the get_executor() method"""
        n = SCons.Node.Node()

        try:
            n.get_executor(0)
        except AttributeError:
            pass
        else:
            self.fail("did not catch expected AttributeError")

        class Builder(object):
            action = 'act'
            env = 'env1'
            overrides = {}

        n = SCons.Node.Node()
        n.builder_set(Builder())
        x = n.get_executor()
        assert x.env == 'env1', x.env

        n = SCons.Node.Node()
        n.builder_set(Builder())
        n.env_set('env2')
        x = n.get_executor()
        assert x.env == 'env2', x.env

    def test_set_executor(self):
        """Test the set_executor() method"""
        n = SCons.Node.Node()
        n.set_executor(1)
        assert n.executor == 1, n.executor

    def test_executor_cleanup(self):
        """Test letting the executor cleanup its cache"""
        n = SCons.Node.Node()
        x = MyExecutor()
        n.set_executor(x)
        n.executor_cleanup()
        assert x.cleaned_up

    def test_reset_executor(self):
        """Test the reset_executor() method"""
        n = SCons.Node.Node()
        n.set_executor(1)
        assert n.executor == 1, n.executor
        n.reset_executor()
        assert not hasattr(n, 'executor'), "unexpected executor attribute"

    def test_built(self):
        """Test the built() method"""
        class SubNodeInfo(SCons.Node.NodeInfoBase):
            __slots__ = ('updated',)
            def update(self, node):
                self.updated = 1
        class SubNode(SCons.Node.Node):
            def clear(self):
                self.cleared = 1

        n = SubNode()
        n.ninfo = SubNodeInfo()
        n.built()
        assert n.cleared, n.cleared
        assert n.ninfo.updated, n.ninfo.cleared

    def test_push_to_cache(self):
        """Test the base push_to_cache() method"""
        n = SCons.Node.Node()
        r = n.push_to_cache()
        assert r is None, r

    def test_retrieve_from_cache(self):
        """Test the base retrieve_from_cache() method"""
        n = SCons.Node.Node()
        r = n.retrieve_from_cache()
        assert r == 0, r

    def test_visited(self):
        """Test the base visited() method

        Just make sure it's there and we can call it.
        """
        n = SCons.Node.Node()
        n.visited()

    def test_builder_set(self):
        """Test setting a Node's Builder
        """
        node = SCons.Node.Node()
        b = Builder()
        node.builder_set(b)
        assert node.builder == b

    def test_has_builder(self):
        """Test the has_builder() method
        """
        n1 = SCons.Node.Node()
        assert n1.has_builder() == 0
        n1.builder_set(Builder())
        assert n1.has_builder() == 1

    def test_has_explicit_builder(self):
        """Test the has_explicit_builder() method
        """
        n1 = SCons.Node.Node()
        assert not n1.has_explicit_builder()
        n1.set_explicit(1)
        assert n1.has_explicit_builder()
        n1.set_explicit(None)
        assert not n1.has_explicit_builder()

    def test_get_builder(self):
        """Test the get_builder() method"""
        n1 = SCons.Node.Node()
        b = n1.get_builder()
        assert b is None, b
        b = n1.get_builder(777)
        assert b == 777, b
        n1.builder_set(888)
        b = n1.get_builder()
        assert b == 888, b
        b = n1.get_builder(999)
        assert b == 888, b

    def test_multiple_side_effect_has_builder(self):
        """Test the multiple_side_effect_has_builder() method
        """
        n1 = SCons.Node.Node()
        assert n1.multiple_side_effect_has_builder() == 0
        n1.builder_set(Builder())
        assert n1.multiple_side_effect_has_builder() == 1

    def test_is_derived(self):
        """Test the is_derived() method
        """
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        n3 = SCons.Node.Node()

        n2.builder_set(Builder())
        n3.side_effect = 1

        assert n1.is_derived() == 0
        assert n2.is_derived() == 1
        assert n3.is_derived() == 1

    def test_alter_targets(self):
        """Test the alter_targets() method
        """
        n = SCons.Node.Node()
        t, m = n.alter_targets()
        assert t == [], t
        assert m is None, m

    def test_is_up_to_date(self):
        """Test the default is_up_to_date() method
        """
        node = SCons.Node.Node()
        assert node.is_up_to_date() is None

    def test_children_are_up_to_date(self):
        """Test the children_are_up_to_date() method used by subclasses
        """
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()

        n1.add_source([n2])
        assert n1.children_are_up_to_date(), "expected up to date"
        n2.set_state(SCons.Node.executed)
        assert not n1.children_are_up_to_date(), "expected not up to date"
        n2.set_state(SCons.Node.up_to_date)
        assert n1.children_are_up_to_date(), "expected up to date"
        n1.always_build = 1
        assert not n1.children_are_up_to_date(), "expected not up to date"

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

    def test_get_csig(self):
        """Test generic content signature calculation
        """
        
        class TestNodeInfo(SCons.Node.NodeInfoBase):
            __slots__ = ('csig',)
        try:
            SCons.Node.Node.NodeInfo = TestNodeInfo
            def my_contents(obj):
                return 444
            SCons.Node._get_contents_map[4] = my_contents
            node = SCons.Node.Node()
            node._func_get_contents = 4
            result = node.get_csig()
            assert result == '550a141f12de6341fba65b0ad0433500', result
        finally:
            SCons.Node.Node.NodeInfo = SCons.Node.NodeInfoBase

    def test_get_cachedir_csig(self):
        """Test content signature calculation for CacheDir
        """
        class TestNodeInfo(SCons.Node.NodeInfoBase):
            __slots__ = ('csig',)
        try:
            SCons.Node.Node.NodeInfo = TestNodeInfo
            def my_contents(obj):
                return 555
            SCons.Node._get_contents_map[4] = my_contents
            node = SCons.Node.Node()
            node._func_get_contents = 4
            result = node.get_cachedir_csig()
            assert result == '15de21c670ae7c3f6f3f1f37029303c9', result
        finally:
            SCons.Node.Node.NodeInfo = SCons.Node.NodeInfoBase

    def test_get_binfo(self):
        """Test fetching/creating a build information structure
        """
        class TestNodeInfo(SCons.Node.NodeInfoBase):
            __slots__ = ('csig',)
        SCons.Node.Node.NodeInfo = TestNodeInfo
        node = SCons.Node.Node()
 
        binfo = node.get_binfo()
        assert isinstance(binfo, SCons.Node.BuildInfoBase), binfo

        node = SCons.Node.Node()
        d = SCons.Node.Node()
        ninfo = d.get_ninfo()
        assert isinstance(ninfo, SCons.Node.NodeInfoBase), ninfo
        i = SCons.Node.Node()
        ninfo = i.get_ninfo()
        assert isinstance(ninfo, SCons.Node.NodeInfoBase), ninfo
        node.depends = [d]
        node.implicit = [i]

        binfo = node.get_binfo()
        assert isinstance(binfo, SCons.Node.BuildInfoBase), binfo
        assert hasattr(binfo, 'bsources')
        assert hasattr(binfo, 'bsourcesigs')
        assert binfo.bdepends == [d]
        assert hasattr(binfo, 'bdependsigs')
        assert binfo.bimplicit == [i]
        assert hasattr(binfo, 'bimplicitsigs')

    def test_explain(self):
        """Test explaining why a Node must be rebuilt
        """
        class testNode(SCons.Node.Node):
            def __str__(self): return 'xyzzy'
        node = testNode()
        node.exists = lambda: None
        # Can't do this with new-style classes (python bug #1066490)
        #node.__str__ = lambda: 'xyzzy'
        result = node.explain()
        assert result == "building `xyzzy' because it doesn't exist\n", result

        class testNode2(SCons.Node.Node):
            def __str__(self): return 'null_binfo'
        class FS(object):
            pass
        node = testNode2()
        node.fs = FS()
        node.fs.Top = SCons.Node.Node()
        result = node.explain()
        assert result is None, result

        def get_null_info():
            class Null_SConsignEntry(object):
                class Null_BuildInfo(object):
                    def prepare_dependencies(self):
                        pass
                binfo = Null_BuildInfo()
            return Null_SConsignEntry()

        node.get_stored_info = get_null_info
        #see above: node.__str__ = lambda: 'null_binfo'
        result = node.explain()
        assert result == "Cannot explain why `null_binfo' is being rebuilt: No previous build information found\n", result

        # XXX additional tests for the guts of the functionality some day

    #def test_del_binfo(self):
    #    """Test deleting the build information from a Node
    #    """
    #    node = SCons.Node.Node()
    #    node.binfo = None
    #    node.del_binfo()
    #    assert not hasattr(node, 'binfo'), node

    def test_store_info(self):
        """Test calling the method to store build information
        """
        node = SCons.Node.Node()
        SCons.Node.store_info_map[node.store_info](node)

    def test_get_stored_info(self):
        """Test calling the method to fetch stored build information
        """
        node = SCons.Node.Node()
        result = node.get_stored_info()
        assert result is None, result

    def test_set_always_build(self):
        """Test setting a Node's always_build value
        """
        node = SCons.Node.Node()
        node.set_always_build()
        assert node.always_build
        node.set_always_build(3)
        assert node.always_build == 3

    def test_set_noclean(self):
        """Test setting a Node's noclean value
        """
        node = SCons.Node.Node()
        node.set_noclean()
        assert node.noclean == 1, node.noclean
        node.set_noclean(7)
        assert node.noclean == 1, node.noclean
        node.set_noclean(0)
        assert node.noclean == 0, node.noclean
        node.set_noclean(None)
        assert node.noclean == 0, node.noclean

    def test_set_precious(self):
        """Test setting a Node's precious value
        """
        node = SCons.Node.Node()
        node.set_precious()
        assert node.precious
        node.set_precious(7)
        assert node.precious == 7

    def test_set_pseudo(self):
        """Test setting a Node's pseudo value
        """
        node = SCons.Node.Node()
        node.set_pseudo()
        assert node.pseudo
        node.set_pseudo(False)
        assert not node.pseudo

    def test_exists(self):
        """Test evaluating whether a Node exists.
        """
        node = SCons.Node.Node()
        e = node.exists()
        assert e == 1, e

    def test_exists(self):
        """Test evaluating whether a Node exists locally or in a repository.
        """
        node = SCons.Node.Node()
        e = node.rexists()
        assert e == 1, e

        class MyNode(SCons.Node.Node):
            def exists(self):
                return 'xyz'

        node = MyNode()
        e = node.rexists()
        assert e == 'xyz', e

    def test_prepare(self):
        """Test preparing a node to be built

        By extension, this also tests the missing() method.
        """
        node = SCons.Node.Node()

        n1 = SCons.Node.Node()
        n1.builder_set(Builder())
        node.implicit = []
        node.implicit_set = set()
        node._add_child(node.implicit, node.implicit_set, [n1])

        node.prepare()  # should not throw an exception

        n2 = SCons.Node.Node()
        n2.linked = 1
        node.implicit = []
        node.implicit_set = set()
        node._add_child(node.implicit, node.implicit_set, [n2])

        node.prepare()  # should not throw an exception

        n3 = SCons.Node.Node()
        node.implicit = []
        node.implicit_set = set()
        node._add_child(node.implicit, node.implicit_set, [n3])

        node.prepare()  # should not throw an exception

        class MyNode(SCons.Node.Node):
            def rexists(self):
                return None
        n4 = MyNode()
        node.implicit = []
        node.implicit_set = set()
        node._add_child(node.implicit, node.implicit_set, [n4])
        exc_caught = 0
        try:
            node.prepare()
        except SCons.Errors.StopError:
            exc_caught = 1
        assert exc_caught, "did not catch expected StopError"

    def test_add_dependency(self):
        """Test adding dependencies to a Node's list.
        """
        node = SCons.Node.Node()
        assert node.depends == []

        zero = SCons.Node.Node()

        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()
        five = SCons.Node.Node()
        six = SCons.Node.Node()

        node.add_dependency([zero])
        assert node.depends == [zero]
        node.add_dependency([one])
        assert node.depends == [zero, one]
        node.add_dependency([two, three])
        assert node.depends == [zero, one, two, three]
        node.add_dependency([three, four, one])
        assert node.depends == [zero, one, two, three, four]

        try:
            node.add_depends([[five, six]])
        except:
            pass
        else:
            raise Exception("did not catch expected exception")
        assert node.depends == [zero, one, two, three, four]


    def test_add_source(self):
        """Test adding sources to a Node's list.
        """
        node = SCons.Node.Node()
        assert node.sources == []

        zero = SCons.Node.Node()
        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()
        five = SCons.Node.Node()
        six = SCons.Node.Node()

        node.add_source([zero])
        assert node.sources == [zero]
        node.add_source([one])
        assert node.sources == [zero, one]
        node.add_source([two, three])
        assert node.sources == [zero, one, two, three]
        node.add_source([three, four, one])
        assert node.sources == [zero, one, two, three, four]

        try:
            node.add_source([[five, six]])
        except:
            pass
        else:
            raise Exception("did not catch expected exception")
        assert node.sources == [zero, one, two, three, four], node.sources

    def test_add_ignore(self):
        """Test adding files whose dependencies should be ignored.
        """
        node = SCons.Node.Node()
        assert node.ignore == []

        zero = SCons.Node.Node()
        one = SCons.Node.Node()
        two = SCons.Node.Node()
        three = SCons.Node.Node()
        four = SCons.Node.Node()
        five = SCons.Node.Node()
        six = SCons.Node.Node()

        node.add_ignore([zero])
        assert node.ignore == [zero]
        node.add_ignore([one])
        assert node.ignore == [zero, one]
        node.add_ignore([two, three])
        assert node.ignore == [zero, one, two, three]
        node.add_ignore([three, four, one])
        assert node.ignore == [zero, one, two, three, four]

        try:
            node.add_ignore([[five, six]])
        except:
            pass
        else:
            raise Exception("did not catch expected exception")
        assert node.ignore == [zero, one, two, three, four]

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
        d1 = MyNode("d1")
        d2 = MyNode("d2")
        node.Tag('found_includes', [d1, d2])

        # Simple return of the found includes
        deps = node.get_implicit_deps(env, s, s.path)
        assert deps == [d1, d2], deps

        # By default, our fake scanner recurses
        e = MyNode("eee")
        f = MyNode("fff")
        g = MyNode("ggg")
        d1.Tag('found_includes', [e, f])
        d2.Tag('found_includes', [e, f])
        f.Tag('found_includes', [g])
        deps = node.get_implicit_deps(env, s, s.path)
        assert deps == [d1, d2, e, f, g], list(map(str, deps))

        # Recursive scanning eliminates duplicates
        e.Tag('found_includes', [f])
        deps = node.get_implicit_deps(env, s, s.path)
        assert deps == [d1, d2, e, f, g], list(map(str, deps))

        # Scanner method can select specific nodes to recurse
        def no_fff(nodes):
            return [n for n in nodes if str(n)[0] != 'f']
        s.recurse_nodes = no_fff
        deps = node.get_implicit_deps(env, s, s.path)
        assert deps == [d1, d2, e, f], list(map(str, deps))

        # Scanner method can short-circuit recursing entirely
        s.recurse_nodes = lambda nodes: []
        deps = node.get_implicit_deps(env, s, s.path)
        assert deps == [d1, d2], list(map(str, deps))

    def test_get_env_scanner(self):
        """Test fetching the environment scanner for a Node
        """
        node = SCons.Node.Node()
        scanner = Scanner()
        env = Environment(SCANNERS = [scanner])
        s = node.get_env_scanner(env)
        assert s == scanner, s
        s = node.get_env_scanner(env, {'X':1})
        assert s == scanner, s

    def test_get_target_scanner(self):
        """Test fetching the target scanner for a Node
        """
        s = Scanner()
        b = Builder()
        b.target_scanner = s
        n = SCons.Node.Node()
        n.builder = b
        x = n.get_target_scanner()
        assert x is s, x

    def test_get_source_scanner(self):
        """Test fetching the source scanner for a Node
        """
        target = SCons.Node.Node()
        source = SCons.Node.Node()
        s = target.get_source_scanner(source)
        assert isinstance(s, SCons.Util.Null), s

        ts1 = Scanner()
        ts2 = Scanner()
        ts3 = Scanner()

        class Builder1(Builder):
            def __call__(self, source):
                r = SCons.Node.Node()
                r.builder = self
                return [r]
        class Builder2(Builder1):
            def __init__(self, scanner):
                self.source_scanner = scanner

        builder = Builder2(ts1)

        targets = builder([source])
        s = targets[0].get_source_scanner(source)
        assert s is ts1, s

        target.builder_set(Builder2(ts1))
        target.builder.source_scanner = ts2
        s = target.get_source_scanner(source)
        assert s is ts2, s

        builder = Builder1(env=Environment(SCANNERS = [ts3]))

        targets = builder([source])

        s = targets[0].get_source_scanner(source)
        assert s is ts3, s


    def test_scan(self):
        """Test Scanner functionality
        """
        env = Environment()
        node = MyNode("nnn")
        node.builder = Builder()
        node.env_set(env)
        x = MyExecutor(env, [node])

        s = Scanner()
        d = MyNode("ddd")
        node.Tag('found_includes', [d])

        node.builder.target_scanner = s
        assert node.implicit is None

        node.scan()
        assert s.called
        assert node.implicit == [d], node.implicit

        # Check that scanning a node with some stored implicit
        # dependencies resets internal attributes appropriately
        # if the stored dependencies need recalculation.
        class StoredNode(MyNode):
            def get_stored_implicit(self):
                return [MyNode('implicit1'), MyNode('implicit2')]

        save_implicit_cache = SCons.Node.implicit_cache
        save_implicit_deps_changed = SCons.Node.implicit_deps_changed
        save_implicit_deps_unchanged = SCons.Node.implicit_deps_unchanged
        SCons.Node.implicit_cache = 1
        SCons.Node.implicit_deps_changed = None
        SCons.Node.implicit_deps_unchanged = None
        try:
            sn = StoredNode("eee")
            sn.builder_set(Builder())
            sn.builder.target_scanner = s

            sn.scan()

            assert sn.implicit == [], sn.implicit
            assert sn.children() == [], sn.children()

        finally:
            SCons.Node.implicit_cache = save_implicit_cache
            SCons.Node.implicit_deps_changed = save_implicit_deps_changed
            SCons.Node.implicit_deps_unchanged = save_implicit_deps_unchanged

    def test_scanner_key(self):
        """Test that a scanner_key() method exists"""
        assert SCons.Node.Node().scanner_key() is None

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
        node.implicit_set = set()
        node._add_child(node.implicit, node.implicit_set, [n7, n8, n9])
        node._add_child(node.implicit, node.implicit_set, [n10, n11, n12])
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
        node.implicit_set = set()
        node._add_child(node.implicit, node.implicit_set, [n7, n8, n9])
        node._add_child(node.implicit, node.implicit_set, [n10, n11, n12])
        node.add_ignore([n2, n5, n8, n11])

        kids = node.all_children()
        for kid in [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12]:
            assert kid in kids, kid

    def test_state(self):
        """Test setting and getting the state of a node
        """
        node = SCons.Node.Node()
        assert node.get_state() == SCons.Node.no_state
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
        assert nw.get_next().name ==  "n1"
        assert nw.is_done()
        assert nw.get_next() is None

        n2 = MyNode("n2")
        n3 = MyNode("n3")
        n1.add_source([n2, n3])

        nw = SCons.Node.Walker(n1)
        n = nw.get_next()
        assert n.name ==  "n2", n.name
        n = nw.get_next()
        assert n.name ==  "n3", n.name
        n = nw.get_next()
        assert n.name ==  "n1", n.name
        n = nw.get_next()
        assert n is None, n

        n4 = MyNode("n4")
        n5 = MyNode("n5")
        n6 = MyNode("n6")
        n7 = MyNode("n7")
        n2.add_source([n4, n5])
        n3.add_dependency([n6, n7])

        nw = SCons.Node.Walker(n1)
        assert nw.get_next().name ==  "n4"
        assert nw.get_next().name ==  "n5"
        assert n2 in nw.history
        assert nw.get_next().name ==  "n2"
        assert nw.get_next().name ==  "n6"
        assert nw.get_next().name ==  "n7"
        assert n3 in nw.history
        assert nw.get_next().name ==  "n3"
        assert n1 in nw.history
        assert nw.get_next().name ==  "n1"
        assert nw.get_next() is None

        n8 = MyNode("n8")
        n8.add_dependency([n3])
        n7.add_dependency([n8])

        def cycle(node, stack):
            global cycle_detected
            cycle_detected = 1

        global cycle_detected

        nw = SCons.Node.Walker(n3, cycle_func = cycle)
        n = nw.get_next()
        assert n.name == "n6", n.name
        n = nw.get_next()
        assert n.name == "n8", n.name
        assert cycle_detected
        cycle_detected = None
        n = nw.get_next()
        assert n.name == "n7", n.name
        n = nw.get_next()
        assert nw.get_next() is None

    def test_abspath(self):
        """Test the get_abspath() method."""
        n = MyNode("foo")
        assert n.get_abspath() == str(n), n.get_abspath()

    def test_for_signature(self):
        """Test the for_signature() method."""
        n = MyNode("foo")
        assert n.for_signature() == str(n), n.get_abspath()

    def test_get_string(self):
        """Test the get_string() method."""
        class TestNode(MyNode):
            def __init__(self, name, sig):
                MyNode.__init__(self, name)
                self.sig = sig

            def for_signature(self):
                return self.sig

        n = TestNode("foo", "bar")
        assert n.get_string(0) == "foo", n.get_string(0)
        assert n.get_string(1) == "bar", n.get_string(1)

    def test_literal(self):
        """Test the is_literal() function."""
        n=SCons.Node.Node()
        assert n.is_literal()

    def test_Annotate(self):
        """Test using an interface-specific Annotate function."""
        def my_annotate(node, self=self):
            node.Tag('annotation', self.node_string)

        save_Annotate = SCons.Node.Annotate
        SCons.Node.Annotate = my_annotate

        try:
            self.node_string = '#1'
            n = SCons.Node.Node()
            a = n.GetTag('annotation')
            assert a == '#1', a

            self.node_string = '#2'
            n = SCons.Node.Node()
            a = n.GetTag('annotation')
            assert a == '#2', a
        finally:
            SCons.Node.Annotate = save_Annotate

    def test_clear(self):
        """Test clearing all cached state information."""
        n = SCons.Node.Node()

        n.set_state(3)
        n.binfo = 'xyz'
        n.includes = 'testincludes'
        n.Tag('found_includes', {'testkey':'testvalue'})
        n.implicit = 'testimplicit'

        x = MyExecutor()
        n.set_executor(x)

        n.clear()

        assert n.includes is None, n.includes
        assert x.cleaned_up

    def test_get_subst_proxy(self):
        """Test the get_subst_proxy method."""
        n = MyNode("test")

        assert n.get_subst_proxy() == n, n.get_subst_proxy()

    def test_new_binfo(self):
        """Test the new_binfo() method"""
        n = SCons.Node.Node()
        result = n.new_binfo()
        assert isinstance(result, SCons.Node.BuildInfoBase), result

    def test_get_suffix(self):
        """Test the base Node get_suffix() method"""
        n = SCons.Node.Node()
        s = n.get_suffix()
        assert s == '', s

    def test_postprocess(self):
        """Test calling the base Node postprocess() method"""
        n = SCons.Node.Node()
        n.waiting_parents = set( ['foo','bar'] )

        n.postprocess()
        assert n.waiting_parents == set(), n.waiting_parents

    def test_add_to_waiting_parents(self):
        """Test the add_to_waiting_parents() method"""
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        assert n1.waiting_parents == set(), n1.waiting_parents
        r = n1.add_to_waiting_parents(n2)
        assert r == 1, r
        assert n1.waiting_parents == set((n2,)), n1.waiting_parents
        r = n1.add_to_waiting_parents(n2)
        assert r == 0, r


class NodeListTestCase(unittest.TestCase):
    def test___str__(self):
        """Test"""
        n1 = MyNode("n1")
        n2 = MyNode("n2")
        n3 = MyNode("n3")
        nl = SCons.Node.NodeList([n3, n2, n1])

        l = [1]
        ul = collections.UserList([2])
        s = str(nl)
        assert s == "['n3', 'n2', 'n1']", s

        r = repr(nl)
        r = re.sub('at (0[xX])?[0-9a-fA-F]+', 'at 0x', r)
        # Don't care about ancestry: just leaf value of MyNode
        r = re.sub('<.*?\.MyNode', '<MyNode', r)
        # New-style classes report as "object"; classic classes report
        # as "instance"...
        r = re.sub("object", "instance", r)
        l = ", ".join(["<MyNode instance at 0x>"]*3)
        assert r == '[%s]' % l, r



if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
