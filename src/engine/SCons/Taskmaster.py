"""SCons.Taskmaster

Generic Taskmaster.

"""

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




import SCons.Node



class Task:
    """Default SCons build engine task.
    
    This controls the interaction of the actual building of node
    and the rest of the engine.

    This is expected to handle all of the normally-customizable
    aspects of controlling a build, so any given application
    *should* be able to do what it wants by sub-classing this
    class and overriding methods as appropriate.  If an application
    needs to customze something by sub-classing Taskmaster (or
    some other build engine class), we should first try to migrate
    that functionality into this class.
    
    Note that it's generally a good idea for sub-classes to call
    these methods explicitly to update state, etc., rather than
    roll their own interaction with Taskmaster from scratch."""
    def __init__(self, tm, target, top):
        self.tm = tm
        self.target = target
        self.top = top

    def execute(self):
        if not self.target.get_state() == SCons.Node.up_to_date:
            self.target.build()

    def get_target(self):
        """Fetch the target being built or updated by this task.
        """
        return self.target

    def set_bsig(self, bsig):
        """Set the task's (*not* the target's)  build signature.

        This will be used later to update the target's build
        signature if the build succeeds."""
        self.bsig = bsig

    def set_tstate(self, state):
        """Set the target node's state."""
        self.target.set_state(state)

    def executed(self):
        """Called when the task has been successfully executed.

        This may have been a do-nothing operation (to preserve
        build order), so check the node's state before updating
        things.  Most importantly, this calls back to the
        Taskmaster to put any node tasks waiting on this one
        back on the pending list."""
        if self.target.get_state() == SCons.Node.executing:
            self.set_tstate(SCons.Node.executed)
            self.target.set_bsig(self.bsig)
            self.tm.add_pending(self.target)

    def failed(self):
        """Default action when a task fails:  stop the build."""
        self.fail_stop()

    def fail_stop(self):
        """Explicit stop-the-build failure."""
        self.set_tstate(SCons.Node.failed)
        self.tm.stop()

    def fail_continue(self):
        """Explicit continue-the-build failure.

        This sets failure status on the target node and all of
        its dependent parent nodes.
        """
        def get_parents(node): return node.get_parents()
        walker = SCons.Node.Walker(self.target, get_parents)
        while 1:
            node = walker.next()
            if node == None: break
            self.tm.remove_pending(node)
            node.set_state(SCons.Node.failed)
        


class Calc:
    def bsig(self, node):
        """
        """
        return None

    def current(self, node, sig):
        """Default SCons build engine is-it-current function.
    
        This returns "always out of date," so every node is always
        built/visited.
        """
        return 0



class Taskmaster:
    """A generic Taskmaster for handling a bunch of targets.

    Classes that override methods of this class should call
    the base class method, so this class can do its thing.    
    """

    def __init__(self, targets=[], tasker=Task, calc=Calc()):
        def out_of_date(node):
            return filter(lambda x: x.get_state() != SCons.Node.up_to_date,
                          node.children())
        self.walkers = map(lambda x, f=out_of_date: SCons.Node.Walker(x, f),
                           targets)
        self.tasker = tasker
        self.calc = calc
        self.ready = []
        self.pending = 0
        
        self._find_next_ready_node()

    def next_task(self):
        """Return the next task to be executed."""
        if self.ready:
            task = self.ready.pop()
            if not self.ready:
                self._find_next_ready_node()
            return task
        else:
            return None

    def _find_next_ready_node(self):
        """Find the next node that is ready to be built"""
        while self.walkers:
            n = self.walkers[0].next()
            if n == None:
                self.walkers.pop(0)
                continue
            if n.get_state():
                # The state is set, so someone has already been here
                # (finished or currently executing).  Find another one.
                continue
            if not n.builder:
                # It's a source file, we don't need to build it,
                # but mark it as "up to date" so targets won't
                # wait for it.
                n.set_state(SCons.Node.up_to_date)
                # set the signature for non-derived files
                # here so they don't get recalculated over
                # and over again:
                n.set_csig(self.calc.csig(n))
                continue
            task = self.tasker(self, n, self.walkers[0].is_done())
            if not n.children_are_executed():
                n.set_state(SCons.Node.pending)
                n.task = task
                self.pending = self.pending + 1
                continue
            self.make_ready(task, n)
            return
            
    def is_blocked(self):
        return not self.ready and self.pending

    def stop(self):
        """Stop the current build completely."""
        self.walkers = []
        self.pending = 0
        self.ready = []

    def add_pending(self, node):
        """Add all the pending parents that are now executable
        to the 'ready' queue."""
        ready = filter(lambda x: (x.get_state() == SCons.Node.pending
                                  and x.children_are_executed()),
                       node.get_parents())
        for n in ready:
            task = n.task
            delattr(n, "task")
            self.make_ready(task, n) 
        self.pending = self.pending - len(ready)

    def remove_pending(self, node):
        """Remove a node from the 'ready' queue."""
        if node.get_state() == SCons.Node.pending:
            self.pending = self.pending - 1

    def make_ready(self, task, node):
        """Common routine that takes a single task+node and makes
        them available on the 'ready' queue."""
        bsig = self.calc.bsig(node)
        task.set_bsig(bsig)
        if self.calc.current(node, bsig):
            task.set_tstate(SCons.Node.up_to_date)
        else:
            task.set_tstate(SCons.Node.executing)
        self.ready.append(task)
