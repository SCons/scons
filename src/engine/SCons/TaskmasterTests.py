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

import sys
import unittest

import SCons.Taskmaster
import SCons.Errors


built_text = None
cache_text = []
visited_nodes = []
executed = None
scan_called = 0

class Node:
    def __init__(self, name, kids = [], scans = []):
        self.name = name
        self.kids = kids
        self.scans = scans
        self.cached = 0
        self.scanned = 0
        self.scanner = None
        self.builder = Node.build
        self.bsig = None
        self.csig = None
        self.state = None
        self.prepared = None
        self.parents = []
        self.side_effect = 0
        self.side_effects = []
        self.alttargets = []

        for kid in kids:
            kid.parents.append(self)

    def retrieve_from_cache(self):
        global cache_text
        if self.cached:
            cache_text.append(self.name + " retrieved")
        return self.cached

    def build(self):
        global built_text
        built_text = self.name + " built"

    def has_builder(self):
        return not self.builder is None

    def is_derived(self):
        return self.has_builder or self.side_effect

    def alter_targets(self):
        return self.alttargets, None

    def built(self):
        global built_text
        built_text = built_text + " really"

    def visited(self):
        global visited_nodes
        visited_nodes.append(self.name)

    def prepare(self):
        self.prepared = 1

    def children(self):
        if not self.scanned:
            self.scan()
            self.scanned = 1
        return self.kids

    def scan(self):
        global scan_called
        scan_called = scan_called + 1
        self.kids = self.kids + self.scans
        for scan in self.scans:
            scan.parents.append(self)
        self.scans = []

    def scanner_key(self):
        return self.name
  
    def get_parents(self):
        return self.parents

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def set_bsig(self, bsig):
        self.bsig = bsig

    def set_csig(self, csig):
        self.csig = csig

    def store_csig(self):
        pass

    def store_bsig(self):
        pass

    def current(self, calc):
        return calc.current(self, calc.bsig(self))
    
    def depends_on(self, nodes):
        for node in nodes:
            if node in self.kids:
                return 1
        return 0

    def __str__(self):
        return self.name


class OtherError(Exception):
    pass

class MyException(Exception):
    pass


class TaskmasterTestCase(unittest.TestCase):

    def test_next_task(self):
        """Test fetching the next task
        """
        global built_text
        
        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1, n1])
        t = tm.next_task()
        t.prepare()
        t.execute()
        t = tm.next_task()
        assert t == None

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        
        tm = SCons.Taskmaster.Taskmaster([n3])

        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n1 built", built_text
        t.executed()

        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n2 built", built_text
        t.executed()

        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n3 built", built_text
        t.executed()

        assert tm.next_task() == None

        built_text = "up to date: "
        top_node = n3

        class MyCalc(SCons.Taskmaster.Calc):
            def current(self, node, sig):
                return 1

        class MyTask(SCons.Taskmaster.Task):
            def execute(self):
                global built_text
                if self.targets[0].get_state() == SCons.Node.up_to_date:
                    if self.top:
                        built_text = self.targets[0].name + " up-to-date top"
                    else:
                        built_text = self.targets[0].name + " up-to-date"
                else:
                    self.targets[0].build()

        n1.set_state(None)
        n2.set_state(None)
        n3.set_state(None)
        tm = SCons.Taskmaster.Taskmaster(targets = [n3],
                                         tasker = MyTask, calc = MyCalc())

        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n1 up-to-date", built_text
        t.executed()

        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n2 up-to-date", built_text
        t.executed()

        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n3 up-to-date top", built_text
        t.executed()

        assert tm.next_task() == None


        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        n4 = Node("n4")
        n5 = Node("n5", [n3, n4])
        tm = SCons.Taskmaster.Taskmaster([n5])

        assert not tm.is_blocked()
        
        t1 = tm.next_task()
        assert t1.get_target() == n1
        assert not tm.is_blocked()
        
        t2 = tm.next_task()
        assert t2.get_target() == n2
        assert not tm.is_blocked()

        t4 = tm.next_task()
        assert t4.get_target() == n4
        assert tm.is_blocked()
        t4.executed()
        assert tm.is_blocked()
        
        t1.executed()
        assert tm.is_blocked()
        t2.executed()
        assert not tm.is_blocked()
        t3 = tm.next_task()
        assert t3.get_target() == n3
        assert tm.is_blocked()

        t3.executed()
        assert not tm.is_blocked()
        t5 = tm.next_task()
        assert t5.get_target() == n5, t5.get_target()
        assert tm.is_blocked()  # still executing t5
        t5.executed()
        assert not tm.is_blocked()

        assert tm.next_task() == None

        
        n4 = Node("n4")
        n4.set_state(SCons.Node.executed)
        tm = SCons.Taskmaster.Taskmaster([n4])
        assert tm.next_task() == None

        n1 = Node("n1")
        n2 = Node("n2", [n1])
        tm = SCons.Taskmaster.Taskmaster([n2,n2])
        t = tm.next_task()
        assert tm.is_blocked()
        t.executed()
        assert not tm.is_blocked()
        t = tm.next_task()
        assert tm.next_task() == None


        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1], [n2])
        tm = SCons.Taskmaster.Taskmaster([n3])
        t = tm.next_task()
        target = t.get_target()
        assert target == n1, target
        t.executed()
        t = tm.next_task()
        target = t.get_target()
        assert target == n2, target
        t.executed()
        t = tm.next_task()
        target = t.get_target()
        assert target == n3, target
        t.executed()
        assert tm.next_task() == None

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        n4 = Node("n4", [n3])
        n5 = Node("n5", [n3])
        global scan_called
        scan_called = 0
        tm = SCons.Taskmaster.Taskmaster([n4])
        t = tm.next_task()
        assert t.get_target() == n1
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n2
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n3
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n4
        t.executed()
        assert tm.next_task() == None
        assert scan_called == 4, scan_called

        tm = SCons.Taskmaster.Taskmaster([n5])
        t = tm.next_task()
        assert t.get_target() == n5, t.get_target()
        t.executed()
        assert tm.next_task() == None
        assert scan_called == 5, scan_called

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3")
        n4 = Node("n4", [n1,n2,n3])
        n5 = Node("n5", [n4])
        n3.side_effect = 1
        n1.side_effects = n2.side_effects = n3.side_effects = [n4]
        tm = SCons.Taskmaster.Taskmaster([n1,n2,n3,n4,n5])
        t = tm.next_task()
        assert t.get_target() == n1
        assert n4.state == SCons.Node.executing
        assert tm.is_blocked()
        t.executed()
        assert not tm.is_blocked()
        t = tm.next_task()
        assert t.get_target() == n2
        assert tm.is_blocked()
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n3
        assert tm.is_blocked()
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n4
        assert tm.is_blocked()
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n5
        assert tm.is_blocked()  # still executing n5
        assert not tm.next_task()
        t.executed()
        assert not tm.is_blocked()

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3")
        n4 = Node("n4", [n1,n2,n3])
        def reverse(dependencies):
            dependencies.reverse()
            return dependencies
        tm = SCons.Taskmaster.Taskmaster([n4], order=reverse)
        t = tm.next_task()
        assert t.get_target() == n3, t.get_target()
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n2, t.get_target()
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n1, t.get_target()
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n4, t.get_target()
        t.executed()

        n5 = Node("n5")
        n6 = Node("n6")
        n7 = Node("n7")
        n6.alttargets = [n7]
        tm = SCons.Taskmaster.Taskmaster([n5])
        t = tm.next_task()
        assert t.get_target() == n5
        t.executed()
        tm = SCons.Taskmaster.Taskmaster([n6])
        t = tm.next_task()
        assert t.get_target() == n7
        t.executed()


    def test_make_ready_exception(self):
        """Test handling exceptions from Task.make_ready()
        """
        class MyTask(SCons.Taskmaster.Task):
            def make_ready(self):
                raise MyException, "from make_ready()"

        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster(targets = [n1], tasker = MyTask)
        t = tm.next_task()
        assert isinstance(tm.exc_type, SCons.Errors.TaskmasterException), repr(tm.exc_type)
        assert tm.exc_value is None, tm.exc_value
        e = tm.exc_type
        assert e.type == MyException, e.type
        assert str(e.value) == "from make_ready()", str(e.value)


    def test_children_errors(self):
        """Test errors when fetching the children of a node.
        """
        class StopNode(Node):
            def children(self):
                raise SCons.Errors.StopError, "stop!"
        class ExitNode(Node):
            def children(self):
                sys.exit(77)

        n1 = StopNode("n1")
        tm = SCons.Taskmaster.Taskmaster([n1])
        t = tm.next_task()
        assert isinstance(tm.exc_type, SCons.Errors.TaskmasterException), repr(tm.exc_type)
        assert tm.exc_value is None, tm.exc_value
        e = tm.exc_type
        assert e.type == SCons.Errors.StopError, e.type
        assert str(e.value) == "stop!", "Unexpected exc_value `%s'" % e.value

        n2 = ExitNode("n2")
        tm = SCons.Taskmaster.Taskmaster([n2])
        t = tm.next_task()
        assert tm.exc_type == SCons.Errors.ExplicitExit, "Did not record ExplicitExit on node"
        assert tm.exc_value.node == n2, tm.exc_value.node
        assert tm.exc_value.status == 77, tm.exc_value.status

    def test_cycle_detection(self):
        """Test detecting dependency cycles

        """
        n1 = Node("n1")
        n2 = Node("n2", [n1])
        n3 = Node("n3", [n2])
        n1.kids = [n3]
        n3.parents.append(n1)

        try:
            tm = SCons.Taskmaster.Taskmaster([n3])
            t = tm.next_task()
        except SCons.Errors.UserError, e:
            assert str(e) == "Dependency cycle: n3 -> n1 -> n2 -> n3", str(e)
        else:
            assert 0
        
    def test_is_blocked(self):
        """Test whether a task is blocked

        Both default and overridden in a subclass.
        """
        tm = SCons.Taskmaster.Taskmaster()
        assert not tm.is_blocked()

        class MyTM(SCons.Taskmaster.Taskmaster):
            def _find_next_ready_node(self):
                self.ready = 1
        tm = MyTM()
        assert not tm.is_blocked()

        class MyTM(SCons.Taskmaster.Taskmaster):
            def _find_next_ready_node(self):
                self.ready = None
                self.pending = []
                self.executing = []
        tm = MyTM()
        assert not tm.is_blocked()

        class MyTM(SCons.Taskmaster.Taskmaster):
            def _find_next_ready_node(self):
                self.ready = None
                self.pending = [1]
        tm = MyTM()
        assert tm.is_blocked()

        class MyTM(SCons.Taskmaster.Taskmaster):
            def _find_next_ready_node(self):
                self.ready = None
                self.executing = [1]
        tm = MyTM()
        assert tm.is_blocked()

    def test_stop(self):
        """Test the stop() method

        Both default and overridden in a subclass.
        """
        global built_text

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        
        tm = SCons.Taskmaster.Taskmaster([n3])
        t = tm.next_task()
        t.prepare()
        t.execute()
        assert built_text == "n1 built", built_text
        t.executed()
        assert built_text == "n1 built really", built_text

        tm.stop()
        assert tm.next_task() is None

        class MyTM(SCons.Taskmaster.Taskmaster):
            def stop(self):
                global built_text
                built_text = "MyTM.stop()"
                SCons.Taskmaster.Taskmaster.stop(self)

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])

        built_text = None
        tm = MyTM([n3])
        tm.next_task().execute()
        assert built_text == "n1 built"

        tm.stop()
        assert built_text == "MyTM.stop()"
        assert tm.next_task() is None

    def test_failed(self):
        """Test when a task has failed
        """
        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1])
        t = tm.next_task()
        assert tm.executing == [n1], tm.executing
        tm.failed(n1)
        assert tm.executing == [], tm.executing

    def test_executed(self):
        """Test when a task has been executed
        """
        global built_text
        global visited_nodes

        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1])
        t = tm.next_task()
        built_text = "xxx"
        visited_nodes = []
        n1.set_state(SCons.Node.executing)
        t.executed()
        s = n1.get_state()
        assert s == SCons.Node.executed, s
        assert built_text == "xxx really", built_text
        assert visited_nodes == [], visited_nodes

        n2 = Node("n2")
        tm = SCons.Taskmaster.Taskmaster([n2])
        t = tm.next_task()
        built_text = "should_not_change"
        visited_nodes = []
        n2.set_state(None)
        t.executed()
        s = n1.get_state()
        assert s == SCons.Node.executed, s
        assert built_text == "should_not_change", built_text
        assert visited_nodes == ["n2"], visited_nodes

    def test_prepare(self):
        """Test preparation of multiple Nodes for a task

        """
        n1 = Node("n1")
        n2 = Node("n2")
        tm = SCons.Taskmaster.Taskmaster([n1, n2])
        t = tm.next_task()
        # This next line is moderately bogus.  We're just reaching
        # in and setting the targets for this task to an array.  The
        # "right" way to do this would be to have the next_task() call
        # set it up by having something that approximates a real Builder
        # return this list--but that's more work than is probably
        # warranted right now.
        t.targets = [n1, n2]
        t.prepare()
        assert n1.prepared
        assert n2.prepared

        n3 = Node("n3")
        n4 = Node("n4")
        tm = SCons.Taskmaster.Taskmaster([n3, n4])
        t = tm.next_task()
        # More bogus reaching in and setting the targets.
        n3.set_state(SCons.Node.up_to_date)
        t.targets = [n3, n4]
        t.prepare()
        assert n3.prepared
        assert n4.prepared

        # If the Node has had an exception recorded while it was getting
        # prepared, then prepare() should raise that exception.
        class MyException(Exception):
            pass

        built_text = None
        n5 = Node("n5")
        tm = SCons.Taskmaster.Taskmaster([n5])
        tm.exc_type = MyException
        tm.exc_value = "exception value"
        t = tm.next_task()
        exc_caught = None
        try:
            t.prepare()
        except MyException, e:
            exc_caught = 1
        except:
            pass
        assert exc_caught, "did not catch expected MyException"
        assert str(e) == "exception value", e
        assert built_text is None, built_text

        # Regression test, make sure we prepare not only
        # all targets, but their side effects as well.
        n6 = Node("n6")
        n7 = Node("n7")
        n8 = Node("n8")
        n9 = Node("n9")
        n10 = Node("n10")

        n6.side_effects = [ n8 ]
        n7.side_effects = [ n9, n10 ]
        
        tm = SCons.Taskmaster.Taskmaster([n6, n7])
        t = tm.next_task()
        # More bogus reaching in and setting the targets.
        t.targets = [n6, n7]
        t.prepare()
        assert n6.prepared
        assert n7.prepared
        assert n8.prepared
        assert n9.prepared
        assert n10.prepared

    def test_execute(self):
        """Test executing a task

        """
        global built_text
        global cache_text

        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1])
        t = tm.next_task()
        t.execute()
        assert built_text == "n1 built", built_text

        def raise_UserError():
            raise SCons.Errors.UserError
        n2 = Node("n2")
        n2.build = raise_UserError
        tm = SCons.Taskmaster.Taskmaster([n2])
        t = tm.next_task()
        try:
            t.execute()
        except SCons.Errors.UserError:
            pass
        else:
            raise TestFailed, "did not catch expected UserError"

        def raise_BuildError():
            raise SCons.Errors.BuildError
        n3 = Node("n3")
        n3.build = raise_BuildError
        tm = SCons.Taskmaster.Taskmaster([n3])
        t = tm.next_task()
        try:
            t.execute()
        except SCons.Errors.BuildError:
            pass
        else:
            raise TestFailed, "did not catch expected BuildError"

        # On a generic (non-BuildError) exception from a Builder,
        # the target should throw a BuildError exception with the
        # args set to the exception value, instance, and traceback.
        def raise_OtherError():
            raise OtherError
        n4 = Node("n4")
        n4.build = raise_OtherError
        tm = SCons.Taskmaster.Taskmaster([n4])
        t = tm.next_task()
        try:
            t.execute()
        except SCons.Errors.BuildError, e:
            assert e.node == n4, e.node
            assert e.errstr == "Exception", e.errstr
            assert len(e.args) == 3, `e.args`
            assert e.args[0] == OtherError, e.args[0]
            assert isinstance(e.args[1], OtherError), type(e.args[1])
            assert type(e.args[2]) == type(sys.exc_traceback), e.args[2]
        else:
            raise TestFailed, "did not catch expected BuildError"

        built_text = None
        cache_text = []
        n5 = Node("n5")
        n6 = Node("n6")
        n6.cached = 1
        tm = SCons.Taskmaster.Taskmaster([n5])
        t = tm.next_task()
        # This next line is moderately bogus.  We're just reaching
        # in and setting the targets for this task to an array.  The
        # "right" way to do this would be to have the next_task() call
        # set it up by having something that approximates a real Builder
        # return this list--but that's more work than is probably
        # warranted right now.
        t.targets = [n5, n6]
        t.execute()
        assert built_text == "n5 built", built_text
        assert cache_text == [], cache_text

        built_text = None
        cache_text = []
        n7 = Node("n7")
        n8 = Node("n8")
        n7.cached = 1
        n8.cached = 1
        tm = SCons.Taskmaster.Taskmaster([n7])
        t = tm.next_task()
        # This next line is moderately bogus.  We're just reaching
        # in and setting the targets for this task to an array.  The
        # "right" way to do this would be to have the next_task() call
        # set it up by having something that approximates a real Builder
        # return this list--but that's more work than is probably
        # warranted right now.
        t.targets = [n7, n8]
        t.execute()
        assert built_text is None, built_text
        assert cache_text == ["n7 retrieved", "n8 retrieved"], cache_text

    def test_exception(self):
        """Test generic Taskmaster exception handling

        """
        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1])

        tm.exception_set(1, 2)
        assert tm.exc_type == 1, tm.exc_type
        assert tm.exc_value == 2, tm.exc_value

        tm.exception_set(3)
        assert tm.exc_type == 3, tm.exc_type
        assert tm.exc_value is None, tm.exc_value

        tm.exception_set(None, None)
        assert tm.exc_type is None, tm.exc_type
        assert tm.exc_value is None, tm.exc_value

        tm.exception_set("exception 1", None)
        try:
            tm.exception_raise()
        except:
            assert sys.exc_type == "exception 1", sys.exc_type
            assert sys.exc_value is None, sys.exc_value
        else:
            assert 0, "did not catch expected exception"

        tm.exception_set("exception 2", "xyzzy")
        try:
            tm.exception_raise()
        except:
            assert sys.exc_type == "exception 2", sys.exc_type
            assert sys.exc_value == "xyzzy", sys.exc_value
        else:
            assert 0, "did not catch expected exception"



if __name__ == "__main__":
    suite = unittest.makeSuite(TaskmasterTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
