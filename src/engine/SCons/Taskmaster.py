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
    def __init__(self,target):
        self.target = target

    def execute(self):
        self.target.build()

    def set_state(self, state):
        return self.target.set_state(state)

    def get_target(self):
        return self.target
        
def current(node):
    """Default SCons build engine is-it-current function.

    This returns "always out of date," so every node is always
    built/visited.
    """
    return None



class Taskmaster:
    """A generic Taskmaster for handling a bunch of targets.

    Classes that override methods of this class should call
    the base class method, so this class can do it's thing.    
    """

    def __init__(self,
                 targets=[],
                 tasker=Task,
                 current=current,
                 ignore_errors=0,
                 keep_going_on_error=0):
        self.walkers = map(SCons.Node.Walker, targets)
        self.tasker = tasker
        self.current = current
        self.targets = targets
        self.ready = []
        self.pending = 0
        self.ignore_errors = ignore_errors
        self.keep_going_on_error = keep_going_on_error

        self._find_next_ready_node()
        
    def next_task(self):
        if self.ready:
            n = self.ready.pop()
            n.set_state(SCons.Node.executing)
            if not self.ready:
                self._find_next_ready_node()

            return self.tasker(n)
        else:
            return None
        
    def _find_next_ready_node(self):
        """Find the next node that is ready to be built"""
        while self.walkers:
            n = self.walkers[0].next()
            if n == None:
                self.walkers.pop(0)
            elif n.get_state() == SCons.Node.up_to_date:
                self.up_to_date(n, self.walkers[0].is_done())
            elif n.get_state() == None:
                if not n.children_are_executed():
                    n.set_state(SCons.Node.pending)
                    self.pending = self.pending + 1
                elif self.current(n):
                    n.set_state(SCons.Node.up_to_date)
                    self.up_to_date(n, self.walkers[0].is_done())
                else:
                    self.ready.append(n)
                    return
        
    def is_blocked(self):
        return not self.ready and self.pending

    def up_to_date(self, node):
        pass

    def executed(self, task):
        task.set_state(SCons.Node.executed)

        # add all the pending parents that are now executable to the 'ready'
        # queue:
        n = task.get_target()
        ready = filter(lambda x: (x.get_state() == SCons.Node.pending
                                  and x.children_are_executed()),
                       n.get_parents())
        self.ready.extend(ready)
        self.pending = self.pending - len(ready)
        
    def failed(self, task):
        if self.ignore_errors:
            self.executed(task)
        else:
            if self.keep_going_on_error:
                # mark all the depants of this node as failed:
                def get_parents(node): return node.get_parents()
                walker = SCons.Node.Walker(task.get_target(), get_parents)
                while 1:
                    node = walker.next()
                    if node == None: break
                    if node.get_state() == SCons.Node.pending:
                        self.pending = self.pending - 1
                    node.set_state(SCons.Node.failed)
            else:
                # terminate the build:
                self.walkers = []
                self.pending = 0
                self.ready = []

            task.set_state(SCons.Node.failed)
