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
import re
import string
import sys
import types
import unittest
import UserList

import SCons.Errors
import SCons.Node



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
        elif type(curr_a) == type([1,2]):
            all.extend(curr_a)
        else:
            raise 'Cannot Combine Actions'
    return MyListAction(all)

class MyActionBase:
    def __add__(self, other):
        return _actionAppend(self, other)

    def __radd__(self, other):
        return _actionAppend(other, self)

class MyAction(MyActionBase):
    def __init__(self):
        self.order = 0

    def __call__(self, target, source, env, errfunc):
        global built_it, built_target, built_source, built_args, built_order
        built_it = 1
        built_target = target
        built_source = source
        built_args = env
        built_order = built_order + 1
        self.order = built_order
        return 0

class MyListAction(MyActionBase):
    def __init__(self, list):
        self.list = list
    def __call__(self, target, source, env, errfunc):
        for A in self.list:
            A(target, source, env, errfunc)
        
class MyNonGlobalAction(MyActionBase):
    def __init__(self):
        self.order = 0
        self.built_it = None
        self.built_target =  None
        self.built_source =  None

    def __call__(self, target, source, env, errfunc):
        # Okay, so not ENTIRELY non-global...
        global built_order
        self.built_it = 1
        self.built_target = target
        self.built_source = source
        self.built_args = env
        built_order = built_order + 1
        self.order = built_order
        return 0

class Environment:
    def __init__(self, **kw):
        self._dict = {}
        self._dict.update(kw)
    def __getitem__(self, key):
        return self._dict[key]
    def Dictionary(self, *args):
        return {}
    def Override(self, overrides):
        d = self._dict.copy()
        d.update(overrides)
        return apply(Environment, (), d)
    def _update(self, dict):
        self._dict.update(dict)

class Builder:
    def __init__(self, is_explicit=1):
        self.env = Environment()
        self.overrides = {}
        self.action = MyAction()
        self.is_explicit = is_explicit
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

class FailBuilder:
    def execute(self, target, source, env):
        return 1

class ExceptBuilder:
    def execute(self, target, source, env):
        raise SCons.Errors.BuildError

class ExceptBuilder2:
    def execute(self, target, source, env):
        raise "foo"

class Scanner:
    called = None
    def __call__(self, node):
        self.called = 1
        return node.found_includes
    def select(self, node):
        return self

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
        node.build(extra_kw_argument = 1)
        assert built_it == None

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
        # [Charles C. 1/7/2002] Uhhh, why are there no asserts here?
        # [SK, 15 May 2003] I dunno, let's add some...
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

    def test_get_executor(self):
        """Test the reset_executor() method"""
        n = SCons.Node.Node()

        try:
            n.get_executor(0)
        except AttributeError:
            pass
        else:
            self.fail("did not catch expected AttributeError")

        class Builder:
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
        """Test the reset_executor() method"""
        n = SCons.Node.Node()
        n.set_executor(1)
        assert n.executor == 1, n.executor

    def test_reset_executor(self):
        """Test the reset_executor() method"""
        n = SCons.Node.Node()
        n.set_executor(1)
        assert n.executor == 1, n.executor
        n.reset_executor()
        assert not hasattr(n, 'executor'), "unexpected executor attribute"

    def test_built(self):
        """Test the built() method"""
        class SubNode(SCons.Node.Node):
            def clear(self):
                self.cleared = 1

        n = SubNode()
        n.built()
        assert n.cleared, n.cleared

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
        n1.builder_set(Builder(is_explicit=1))
        assert n1.has_explicit_builder()
        n1.builder_set(Builder(is_explicit=None))
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
        assert m == None, m

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

    def test_calc_bsig(self):
        """Test generic build signature calculation
        """
        class Calculator:
            def __init__(self, val):
                self.max_drift = 0
                class M:
                    def __init__(self, val):
                        self.val = val
                    def collect(self, args):
                        return reduce(lambda x, y: x+y, args, self.val)
                self.module = M(val)
        node = SCons.Node.Node()
        result = node.calc_bsig(Calculator(222))
        assert result == 222, result
        result = node.calc_bsig(Calculator(333))
        assert result == 222, result

    def test_calc_csig(self):
        """Test generic content signature calculation
        """
        class Calculator:
            def __init__(self, val):
                self.max_drift = 0
                class M:
                    def __init__(self, val):
                        self.val = val
                    def signature(self, args):
                        return self.val
                self.module = M(val)
        node = SCons.Node.Node()
        result = node.calc_csig(Calculator(444))
        assert result == 444, result
        result = node.calc_csig(Calculator(555))
        assert result == 444, result

    def test_gen_binfo(self):
        """Test generating a build information structure
        """
        class Calculator:
            def __init__(self, val):
                self.max_drift = 0
                class M:
                    def __init__(self, val):
                        self.val = val
                    def collect(self, args):
                        return reduce(lambda x, y: x+y, args, self.val)
                self.module = M(val)

        node = SCons.Node.Node()
        binfo = node.gen_binfo(Calculator(666))
        assert isinstance(binfo, SCons.Node.BuildInfo), binfo
        assert hasattr(binfo, 'bsources')
        assert hasattr(binfo, 'bsourcesigs')
        assert hasattr(binfo, 'bdepends')
        assert hasattr(binfo, 'bdependsigs')
        assert hasattr(binfo, 'bimplicit')
        assert hasattr(binfo, 'bimplicitsigs')
        assert binfo.bsig == 666, binfo.bsig

    def test_explain(self):
        """Test explaining why a Node must be rebuilt
        """
        node = SCons.Node.Node()
        node.exists = lambda: None
        node.__str__ = lambda: 'xyzzy'
        result = node.explain()
        assert result == "building `xyzzy' because it doesn't exist\n", result

        node = SCons.Node.Node()
        result = node.explain()
        assert result == None, result

        class Null_BInfo:
            def __init__(self):
                pass

        node.get_stored_info = Null_BInfo
        node.__str__ = lambda: 'null_binfo'
        result = node.explain()
        assert result == "Cannot explain why `null_binfo' is being rebuilt: No previous build information found\n", result

        # XXX additional tests for the guts of the functionality some day

    def test_del_binfo(self):
        """Test deleting the build information from a Node
        """
        node = SCons.Node.Node()
        node.binfo = None
        node.del_binfo()
        assert not hasattr(node, 'binfo'), node

    def test_store_info(self):
        """Test calling the method to store build information
        """
        class Entry:
            pass
        node = SCons.Node.Node()
        node.store_info(Entry())

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

    def test_set_precious(self):
        """Test setting a Node's precious value
        """
        node = SCons.Node.Node()
        node.set_precious()
        assert node.precious
        node.set_precious(7)
        assert node.precious == 7

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
        """
        node = SCons.Node.Node()

        n1 = SCons.Node.Node()
        n1.builder_set(Builder())
        node.implicit = []
        node.implicit_dict = {}
        node._add_child(node.implicit, node.implicit_dict, [n1])

        node.prepare()  # should not throw an exception

        n2 = SCons.Node.Node()
        n2.linked = 1
        node.implicit = []
        node.implicit_dict = {}
        node._add_child(node.implicit, node.implicit_dict, [n2])

        node.prepare()  # should not throw an exception

        n3 = SCons.Node.Node()
        node.implicit = []
        node.implicit_dict = {}
        node._add_child(node.implicit, node.implicit_dict, [n3])

        node.prepare()  # should not throw an exception

        class MyNode(SCons.Node.Node):
            def rexists(self):
                return None
        n4 = MyNode()
        node.implicit = []
        node.implicit_dict = {}
        node._add_child(node.implicit, node.implicit_dict, [n4])
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

        node.add_dependency(zero)
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
            raise "did not catch expected exception"
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

        node.add_source(zero)
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
            raise "did not catch expected exception"
        assert node.sources == [zero, one, two, three, four]

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

        node.add_ignore(zero)
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
            raise "did not catch expected exception"
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

    def test_get_source_scanner(self):
        """Test fetching the source scanner for a Node
        """
        class Builder:
            pass
        target = SCons.Node.Node()
        source = SCons.Node.Node()
        s = target.get_source_scanner(source)
        assert s is None, s

        ts1 = Scanner()
        ts2 = Scanner()
        ts3 = Scanner()

        source.backup_source_scanner = ts1
        s = target.get_source_scanner(source)
        assert s is ts1, s

        target.builder = Builder()
        target.builder.source_scanner = ts2
        s = target.get_source_scanner(source)
        assert s is ts2, s

        target.source_scanner = ts3
        s = target.get_source_scanner(source)
        assert s is ts3, s

    def test_scan(self):
        """Test Scanner functionality
        """
        node = MyNode("nnn")
        node.builder = Builder()
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

        # Check that scanning a node with some stored implicit
        # dependencies resets internal attributes appropriately
        # if the stored dependencies need recalculation.
        class StoredNode(MyNode):
            def get_stored_implicit(self):
                return ['implicit1', 'implicit2']

        class NotCurrent:
            def current(self, node, sig):
                return None
            def bsig(self, node):
                return 0

        import SCons.Sig

        save_default_calc = SCons.Sig.default_calc
        save_implicit_cache = SCons.Node.implicit_cache
        save_implicit_deps_changed = SCons.Node.implicit_deps_changed
        save_implicit_deps_unchanged = SCons.Node.implicit_deps_unchanged
        SCons.Sig.default_calc = NotCurrent()
        SCons.Node.implicit_cache = 1
        SCons.Node.implicit_deps_changed = None
        SCons.Node.implicit_deps_unchanged = None
        try:
            sn = StoredNode("eee")
            sn._children = ['fake']
            sn.target_scanner = s

            sn.scan()

            assert sn.implicit == [], sn.implicit
            assert not hasattr(sn, '_children'), "unexpected _children attribute"
        finally:
            SCons.Sig.default_calc = save_default_calc
            SCons.Node.implicit_cache = save_implicit_cache
            SCons.Node.implicit_deps_changed = save_implicit_deps_changed
            SCons.Node.implicit_deps_unchanged = save_implicit_deps_unchanged

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
        node.implicit_dict = {}
        node._add_child(node.implicit, node.implicit_dict, [n7, n8, n9])
        node._add_child(node.implicit, node.implicit_dict, [n10, n11, n12])
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
        node.implicit_dict = {}
        node._add_child(node.implicit, node.implicit_dict, [n7, n8, n9])
        node._add_child(node.implicit, node.implicit_dict, [n10, n11, n12])
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
        n = nw.next()
        assert n.name ==  "n2", n.name
        n = nw.next()
        assert n.name ==  "n3", n.name
        n = nw.next()
        assert n.name ==  "n1", n.name
        n = nw.next()
        assert n == None, n

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
            node.annotation = self.node_string

        save_Annotate = SCons.Node.Annotate
        SCons.Node.Annotate = my_annotate

        try:
            self.node_string = '#1'
            n = SCons.Node.Node()
            assert n.annotation == '#1', n.annotation

            self.node_string = '#2'
            n = SCons.Node.Node()
            assert n.annotation == '#2', n.annotation
        finally:
            SCons.Node.Annotate = save_Annotate

    def test_clear(self):
        """Test clearing all cached state information."""
        n = SCons.Node.Node()

        n.set_state(3)
        n.binfo = 'xyz'
        n.includes = 'testincludes'
        n.found_include = {'testkey':'testvalue'}
        n.implicit = 'testimplicit'
        n.waiting_parents = ['foo', 'bar']

        n.clear()

        assert n.get_state() is None, n.get_state()
        assert not hasattr(n, 'binfo'), n.bsig
        assert n.includes is None, n.includes
        assert n.found_includes == {}, n.found_includes
        assert n.implicit is None, n.implicit
        assert n.waiting_parents == [], n.waiting_parents

    def test_get_subst_proxy(self):
        """Test the get_subst_proxy method."""
        n = MyNode("test")

        assert n.get_subst_proxy() == n, n.get_subst_proxy()

    def test_new_binfo(self):
        """Test the new_binfo() method"""
        n = SCons.Node.Node()
        result = n.new_binfo()
        assert isinstance(result, SCons.Node.BuildInfo), result

    def test_get_suffix(self):
        """Test the base Node get_suffix() method"""
        n = SCons.Node.Node()
        s = n.get_suffix()
        assert s == '', s

    def test_generate_build_dict(self):
        """Test the base Node generate_build_dict() method"""
        n = SCons.Node.Node()
        dict = n.generate_build_dict()
        assert dict == {}, dict

    def test_postprocess(self):
        """Test calling the base Node postprocess() method"""
        n = SCons.Node.Node()
        n.postprocess()

    def test_add_to_waiting_parents(self):
        """Test the add_to_waiting_parents() method"""
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        assert n1.waiting_parents == [], n1.waiting_parents
        n1.add_to_waiting_parents(n2)
        assert n1.waiting_parents == [n2], n1.waiting_parents

    def test_call_for_all_waiting_parents(self):
        """Test the call_for_all_waiting_parents() method"""
        n1 = SCons.Node.Node()
        n2 = SCons.Node.Node()
        n1.add_to_waiting_parents(n2)
        result = []
        def func(node, result=result):
            result.append(node)
        n1.call_for_all_waiting_parents(func)
        assert result == [n1, n2], result

class NodeListTestCase(unittest.TestCase):
    def test___str__(self):
        """Test"""
        n1 = MyNode("n1")
        n2 = MyNode("n2")
        n3 = MyNode("n3")
        nl = SCons.Node.NodeList([n3, n2, n1])

        l = [1]
        ul = UserList.UserList([2])
        try:
            l.extend(ul)
        except TypeError:
            # An older version of Python (*cough* 1.5.2 *cough*)
            # that doesn't allow UserList objects to extend lists.
            pass
        else:
            s = str(nl)
            assert s == "['n3', 'n2', 'n1']", s

        r = repr(nl)
        r = re.sub('at (0x)?[0-9a-z]+', 'at 0x', repr(nl))
        l = string.join(["<__main__.MyNode instance at 0x>"]*3, ", ")
        assert r == '[%s]' % l, r



if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ NodeTestCase,
                 NodeListTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
