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
executed = None
scan_called = 0

class Node:
    def __init__(self, name, kids = [], scans = []):
        self.name = name
        self.kids = kids
        self.scans = scans
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

        for kid in kids:
            kid.parents.append(self)

    def build(self):
        global built_text
        built_text = self.name + " built"

    def has_builder(self):
        return not self.builder is None

    def built(self):
        global built_text
        built_text = built_text + " really"

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
        assert not tm.is_blocked()
        assert not tm.next_task()
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
        assert n1.exc_type == MyException, n1.exc_type
        assert str(n1.exc_value) == "from make_ready()", n1.exc_value


    def test_children_errors(self):
        """Test errors when fetching the children of a node.
        """
        class MyNode(Node):
            def children(self):
                raise SCons.Errors.StopError, "stop!"
        n1 = MyNode("n1")
        tm = SCons.Taskmaster.Taskmaster([n1])
        t = tm.next_task()
        assert n1.exc_type == SCons.Errors.StopError, "Did not record StopError on node"
        assert str(n1.exc_value) == "stop!", "Unexpected exc_value `%s'" % n1.exc_value

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
            def is_blocked(self):
                return 1
        tm = MyTM()
        assert tm.is_blocked() == 1

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

    def test_executed(self):
        """Test when a task has been executed
        """
        pass

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

    def test_execute(self):
        """Test executing a task

        """
        global built_text

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

        # If the Node has had an exception recorded (during
        # preparation), then execute() should raise that exception,
        # not build the Node.
        class MyException(Exception):
            pass

        built_text = None
        n5 = Node("n5")
        n5.exc_type = MyException
        n5.exc_value = "exception value"
        tm = SCons.Taskmaster.Taskmaster([n5])
        t = tm.next_task()
        exc_caught = None
        try:
            t.execute()
        except MyException, v:
            assert str(v) == "exception value", v
            exc_caught = 1
        assert exc_caught, "did not catch expected MyException"
        assert built_text is None, built_text



if __name__ == "__main__":
    suite = unittest.makeSuite(TaskmasterTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
