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
        self.sources = []       # source files used to build node
        self.depends = []       # explicit dependencies (from Depends)
        self.implicit = {}	# implicit (scanned) dependencies
        self.parents = []
        self.wkids = None       # Kids yet to walk, when it's an array
	self.builder = None
        self.scanners = []
        self.scanned = {}
	self.env = None
        self.state = None
        self.bsig = None
        self.csig = None
        self.use_signature = 1

    def build(self):
        """Actually build the node.   Return the status from the build."""
	if not self.builder:
	    return None
        try:
            stat = self.builder.execute(env = self.env.Dictionary(),
                                        target = self, source = self.sources)
        except:
            raise BuildError(node = self, errstr = "Exception")
        if stat:
            raise BuildError(node = self, errstr = "Error %d" % stat)

        # If we succesfully build a node, then we need to rescan for
        # implicit dependencies, since it might have changed on us.

        # XXX Modify this so we only rescan using the scanner(s) relevant
        # to this build.
        for scn in self.scanners:
            try:
                del self.scanned[scn]
            except KeyError:
                pass
        
        self.scan()

        for scn in self.scanners:
            try:
                for dep in self.implicit[scn]:
                    w=Walker(dep)
                    while not w.is_done():
                        w.next().scan()
            except KeyError:
                pass
	return stat

    def builder_set(self, builder):
	self.builder = builder

    def builder_sig_adapter(self):
        """Create an adapter for calculating a builder's signature.

        The underlying signature class will call get_contents()
        to fetch the signature of a builder, but the actual
        content of that signature depends on the node and the
        environment (for construction variable substitution),
        so this adapter provides the right glue between the two.
        """
        class Adapter:
            def __init__(self, node):
                self.node = node
            def get_contents(self):
                env = self.node.env.Dictionary()
                try:
                    dir = self.node.getcwd()
                except AttributeError:
                    dir = None
                return self.node.builder.get_contents(env = env, dir = dir)
        return Adapter(self)

    def scanner_set(self, scanner):
        if not scanner in self.scanners:
            self.scanners.append(scanner)

    def scan(self):
        for scn in self.scanners:
            self.scanned[scn] = 1

    def env_set(self, env, safe=0):
        if safe and self.env:
            return
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

    def add_implicit(self, implicit, key):
        """Adds implicit (scanned) dependencies. The implicit
        argument must be a list."""
        if not self.implicit.has_key(key):
             self.implicit[key] = []
        self._add_child(self.implicit[key], implicit)

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

    def add_wkid(self, wkid):
        """Add a node to the list of kids waiting to be evaluated"""
        if self.wkids != None:
            self.wkids.append(wkid)

    def children(self):
        #XXX Need to remove duplicates from this
        return self.sources \
               + self.depends \
               + reduce(lambda x, y: x + y, self.implicit.values(), [])

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
def ignore_cycle(node, stack): pass

class Walker:
    """An iterator for walking a Node tree.

    This is depth-first, children are visited before the parent.
    The Walker object can be initialized with any node, and
    returns the next node on the descent with each next() call.
    'kids_func' is an optional function that will be called to
    get the children of a node instead of calling 'children'. 
    'cycle_func' is an optional function that will be called
    when a cycle is detected.
    
    This class does not get caught in node cycles caused, for example,
    by C header file include loops.
    """
    def __init__(self, node, kids_func=get_children, cycle_func=ignore_cycle):
        self.kids_func = kids_func
        self.cycle_func = cycle_func
        node.wkids = copy.copy(kids_func(node))
        self.stack = [node]
        self.history = {} # used to efficiently detect and avoid cycles
        self.history[node] = None

    def next(self):
	"""Return the next node for this walk of the tree.

	This function is intentionally iterative, not recursive,
	to sidestep any issues of stack size limitations.
	"""

	while self.stack:
            if self.stack[-1].wkids:
                node = self.stack[-1].wkids.pop(0)
                if not self.stack[-1].wkids:
                    self.stack[-1].wkids = None
                if self.history.has_key(node):
                    self.cycle_func(node, self.stack)
                else:
                    node.wkids = copy.copy(self.kids_func(node))
                    self.stack.append(node)
                    self.history[node] = None
            else:
                node = self.stack.pop()
                del self.history[node]
                return node

    def is_done(self):
        return not self.stack
