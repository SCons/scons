"""SCons.Node

The Node package for the SCons software construction utility.

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



from SCons.Errors import BuildError
import string
import types
import copy

# Node states
#
# These are in "priority" order, so that the maximum value for any
# child/dependency of a node represents the state of that node if
# it has no builder of its own.  The canonical example is a file
# system directory, which is only up to date if all of its children
# were up to date.
pending = 1
executing = 2
up_to_date = 3
executed = 4
failed = 5

class Node:
    """The base Node class, for entities that we know how to
    build, or use to build other Nodes.
    """

    def __init__(self):
	self.sources = []
	self.depends = []
        self.parents = []
	self.builder = None
	self.env = None
        self.state = None
        self.bsig = None
        self.csig = None
        self.use_signature = 1

    def build(self):
        """Actually build the node.   Return the status from the build."""
	if not self.builder:
	    return None
	sources_str = string.join(map(lambda x: str(x), self.sources))
	stat = self.builder.execute(env = self.env.Dictionary(),
				    target = str(self), source = sources_str)
	if stat != 0:
	    raise BuildError(node = self, stat = stat)
	return stat

    def builder_set(self, builder):
	self.builder = builder

    def env_set(self, env):
	self.env = env

    def get_bsig(self):
        """Get the node's build signature (based on the signatures
        of its dependency files and build information)."""
        return self.bsig

    def set_bsig(self, bsig):
        """Set the node's build signature (based on the signatures
        of its dependency files and build information)."""
        self.bsig = bsig

    def get_csig(self):
        """Get the signature of the node's content."""
        return self.csig

    def set_csig(self, csig):
        """Set the signature of the node's content."""
        self.csig = csig

    def add_dependency(self, depend):
	"""Adds dependencies. The depend argument must be a list."""
        self._add_child(self.depends, depend)

    def add_source(self, source):
	"""Adds sources. The source argument must be a list."""
        self._add_child(self.sources, source)

    def _add_child(self, collection, child):
        """Adds 'child' to 'collection'. The 'child' argument must be a list"""
        if type(child) is not type([]):
            raise TypeError("child must be a list")
	child = filter(lambda x, s=collection: x not in s, child)
	if child:
	    collection.extend(child)

        for c in child:
            c._add_parent(self)

    def _add_parent(self, parent):
        """Adds 'parent' to the list of parents of this node"""

        if parent not in self.parents: self.parents.append(parent)

    def children(self):
	return self.sources + self.depends

    def get_parents(self):
        return self.parents

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def current(self):
        return None

    def children_are_executed(self):
        return reduce(lambda x,y: ((y.get_state() == executed
                                   or y.get_state() == up_to_date)
                                   and x),
                      self.children(),
                      1)

def get_children(node): return node.children()

class Wrapper:
    def __init__(self, node, kids_func):
        self.node = node
        self.kids = copy.copy(kids_func(node))

        # XXX randomize kids here, if requested

class Walker:
    """An iterator for walking a Node tree.

    This is depth-first, children are visited before the parent.
    The Walker object can be initialized with any node, and
    returns the next node on the descent with each next() call.
    'kids_func' is an optional function that will be called to
    get the children of a node instead of calling 'children'.
    """
    def __init__(self, node, kids_func=get_children):
        self.kids_func = kids_func
        self.stack = [Wrapper(node, self.kids_func)]

    def next(self):
	"""Return the next node for this walk of the tree.

	This function is intentionally iterative, not recursive,
	to sidestep any issues of stack size limitations.
	"""

	while self.stack:
	    if self.stack[-1].kids:
	    	self.stack.append(Wrapper(self.stack[-1].kids.pop(0),
                                          self.kids_func))
            else:
                return self.stack.pop().node

    def is_done(self):
        return not self.stack
