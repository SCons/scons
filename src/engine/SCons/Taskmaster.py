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



def current(node):
    """Default SCons build engine is-it-current function.

    This returns "always out of date," so every node is always
    built/visited.
    """
    return None



class Taskmaster:
    """A generic Taskmaster for handling a bunch of targets.
    """

    def __init__(self, targets=[], tasker=Task, current=current):
        self.targets = targets
        self.tasker = tasker
        self.current = current
        self.num_iterated = 0
        self.walker = None

    def next_node(self):
        t = None
        if self.walker:
            t = self.walker.next()
        if t == None and self.num_iterated < len(self.targets):
            t = self.targets[self.num_iterated]
            self.num_iterated = self.num_iterated + 1
            t.top_target = 1
            self.walker = SCons.Node.Walker(t)
            t = self.walker.next()
        top = None
        if hasattr(t, "top_target"):
            top = 1
        return t, top

    def next_task(self):
        n, top = self.next_node()
        while n != None:
            if self.current(n):
                self.up_to_date(n)
            else:
                return self.tasker(n)
            n, top = self.next_node()
        return None

    def is_blocked(self):
        return 0

    def up_to_date(self, node):
        pass

    def executed(self, task):
        pass

    def failed(self, task):
        self.walker = None
        self.num_iterated = len(self.targets)
