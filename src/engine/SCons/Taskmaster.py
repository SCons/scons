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
    """Default SCons build engine task."""
    def __init__(self, tm, target, top):
        self.tm = tm
        self.target = target
        self.sig = None
        self.top = top

    def execute(self):
        if not self.target.get_state() == SCons.Node.up_to_date:
            self.target.build()

    def get_target(self):
        return self.target

    def set_sig(self, sig):
        self.sig = sig

    def set_state(self, state):
        self.target.set_state(state)

    def executed(self):
        if self.target.get_state() == SCons.Node.executing:
            self.set_state(SCons.Node.executed)
            self.tm.add_pending(self.target)
            self.target.set_signature(self.sig)

    def failed(self):
        self.fail_stop()

    def fail_stop(self):
        self.set_state(SCons.Node.failed)
        self.tm.stop()

    def fail_continue(self):
        def get_parents(node): return node.get_parents()
        walker = SCons.Node.Walker(self.target, get_parents)
        while 1:
            node = walker.next()
            if node == None: break
            self.tm.remove_pending(node)
            node.set_state(SCons.Node.failed)
        


class Calc:
    def get_signature(self, node):
        """
        """
        return None

    def set_signature(self, node):
        """
        """
        pass

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
        self.walkers = map(SCons.Node.Walker, targets)
        self.tasker = tasker
        self.calc = calc
        self.ready = []
        self.pending = 0
        
        self._find_next_ready_node()

    def next_task(self):
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
                n.set_signature(self.calc.get_signature(n))
                continue
            task = self.tasker(self, n, self.walkers[0].is_done())
            if not n.children_are_executed():
                n.set_state(SCons.Node.pending)
                n.task = task
                self.pending = self.pending + 1
                continue
            sig = self.calc.get_signature(n)
            task.set_sig(sig)
            if self.calc.current(n, sig):
                task.set_state(SCons.Node.up_to_date)
            else:
                task.set_state(SCons.Node.executing)

            self.ready.append(task)
            return
            
    def is_blocked(self):
        return not self.ready and self.pending

    def stop(self):
        self.walkers = []
        self.pending = 0
        self.ready = []

    def add_pending(self, node):
        # add all the pending parents that are now executable to the 'ready'
        # queue:
        ready = filter(lambda x: (x.get_state() == SCons.Node.pending
                                  and x.children_are_executed()),
                       node.get_parents())
        for n in ready:
            task = n.task
            delattr(n, "task")
            sig = self.calc.get_signature(n)
            task.set_sig(sig)
            if self.calc.current(n, sig):
                task.set_state(SCons.Node.up_to_date)
            else:
                task.set_state(SCons.Node.executing)
            self.ready.append(task)
        self.pending = self.pending - len(ready)

    def remove_pending(self, node):
        if node.get_state() == SCons.Node.pending:
            self.pending = self.pending - 1
