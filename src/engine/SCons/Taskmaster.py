"""SCons.Taskmaster

Generic Taskmaster.

"""

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




import SCons.Node
import string
import SCons.Errors
import copy

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
    def __init__(self, tm, targets, top, scanner = None):
        self.tm = tm
        self.targets = targets
        self.top = top
        self.scanner = scanner

    def execute(self):
        if self.targets[0].get_state() != SCons.Node.up_to_date:
            self.targets[0].prepare()
            self.targets[0].build()

    def get_target(self):
        """Fetch the target being built or updated by this task.
        """
        return self.targets[0]

    def set_tstates(self, state):
        """Set all of the target nodes's states."""
        for t in self.targets:
            t.set_state(state)

    def executed(self):
        """Called when the task has been successfully executed.

        This may have been a do-nothing operation (to preserve
        build order), so check the node's state before updating
        things.  Most importantly, this calls back to the
        Taskmaster to put any node tasks waiting on this one
        back on the pending list."""
        if self.targets[0].get_state() == SCons.Node.executing:
            self.set_tstates(SCons.Node.executed)
            for t in self.targets:
                t.store_sigs()
            parents = {}
            for p in reduce(lambda x, y: x + y.get_parents(), self.targets, []):
                parents[p] = 1
            ready = filter(lambda x, s=self.scanner:
                                  (x.get_state() == SCons.Node.pending
                                   and x.children_are_executed(s)),
                           parents.keys())
            tasks = {}
            for t in map(lambda r: r.task, ready):
                tasks[t] = 1
            self.tm.pending_to_ready(tasks.keys())

    def failed(self):
        """Default action when a task fails:  stop the build."""
        self.fail_stop()

    def fail_stop(self):
        """Explicit stop-the-build failure."""
        self.set_tstates(SCons.Node.failed)
        self.tm.stop()

    def fail_continue(self):
        """Explicit continue-the-build failure.

        This sets failure status on the target nodes and all of
        their dependent parent nodes.
        """
        nodes = {}
        for t in self.targets:
            def get_parents(node, parent): return node.get_parents()
            walker = SCons.Node.Walker(t, get_parents)
            while 1:
                n = walker.next()
                if n == None: break
                nodes[n] = 1
        pending = filter(lambda x: x.get_state() == SCons.Node.pending,
                         nodes.keys())
        tasks = {}
        for t in map(lambda r: r.task, pending):
            tasks[t] = 1
        self.tm.pending_remove(tasks.keys())

    def make_ready(self):
        """Make a task ready for execution."""
        state = SCons.Node.up_to_date
        for t in self.targets:
            bsig = self.tm.calc.bsig(t)
            t.set_bsig(bsig)
            if not self.tm.calc.current(t, bsig):
                state = SCons.Node.executing
        self.set_tstates(state)
        self.tm.add_ready(self)



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
        
        def out_of_date(node, parent):
            if node.get_state():
                # The state is set, so someone has already been here
                # (finished or currently executing).  Find another one.
                return []
            # Scan the file before fetching its children().
            if parent:
                scanner = parent.src_scanner_get(node.scanner_key())
            else:
                scanner = None
            return filter(lambda x: x.get_state() != SCons.Node.up_to_date,
                          node.children(scanner))

        def cycle_error(node, stack):
            if node.builder:
                nodes = stack + [node]
                nodes.reverse()
                desc = "Dependency cycle: " + string.join(map(str, nodes), " -> ")
                raise SCons.Errors.UserError, desc

        def eval_node(node, parent, self=self):
            if node.get_state():
                # The state is set, so someone has already been here
                # (finished or currently executing).  Find another one.
                return
            if not node.builder:
                # It's a source file, we don't need to build it,
                # but mark it as "up to date" so targets won't
                # wait for it.
                node.set_state(SCons.Node.up_to_date)
                # set the signature for non-derived files
                # here so they don't get recalculated over
                # and over again:
                node.set_csig(self.calc.csig(node))
                return
            try:
                tlist = node.builder.targets(node)
            except AttributeError:
                tlist = [ node ]
            if parent:
                scanner = parent.src_scanner_get(node.scanner_key())
            else:
                scanner = None
            task = self.tasker(self, tlist, self.walkers[0].is_done(), scanner)
            if not tlist[0].children_are_executed(scanner):
                for t in tlist:
                    t.set_state(SCons.Node.pending)
                    t.task = task
                self.pending = self.pending + 1
                return
            task.make_ready()

        #XXX In Python 2.2 we can get rid of f1, f2 and f3:
        self.walkers = map(lambda x, f1=out_of_date,
                                     f2=cycle_error,
                                     f3=eval_node:
                                  SCons.Node.Walker(x, f1, f2, f3),
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
            if self.ready:
                return
            
    def is_blocked(self):
        return not self.ready and self.pending

    def stop(self):
        """Stop the current build completely."""
        self.walkers = []
        self.pending = 0
        self.ready = []

    def add_ready(self, task):
        """Add a task to the ready queue.
        """
        self.ready.append(task)

    def pending_to_ready(self, tasks):
        """Move the specified tasks from the pending count
        to the 'ready' queue.
        """
        self.pending_remove(tasks)
        for t in tasks:
            t.make_ready()

    def pending_remove(self, tasks):
        """Remove tasks from the pending count.
        
        We assume that the caller has already confirmed that
        the nodes in this task are in pending state.
        """
        self.pending = self.pending - len(tasks)
