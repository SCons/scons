"""SCons.Node

The Node package for the SCons software construction utility.

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



import string
import types
import copy
import sys

from SCons.Errors import BuildError
import SCons.Util

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
        self.ignore = []	# dependencies to ignore
        self.parents = {}
        self.wkids = None       # Kids yet to walk, when it's an array
        self.builder = None
        self.scanner = None     # explicit scanner from this node's Builder
        self.scanned = {}       # cached scanned values
        self.src_scanners = {}  # scanners for this node's source files
        self.env = None
        self.state = None
        self.bsig = None
        self.csig = None
        self.use_signature = 1
        self.precious = None
        self.found_includes = {}

    def build(self):
        """Actually build the node.   Return the status from the build."""
	if not self.builder:
	    return None
        try:
            # If this Builder instance has already been called,
            # there will already be an associated status.
            stat = self.builder.status
        except AttributeError:
            try:
                dict = copy.copy(self.env.Dictionary())
                if hasattr(self, 'dir'):
                    auto = self.env.autogenerate(dir = self.dir)
                else:
                    auto = self.env.autogenerate()
                dict.update(auto)
                stat = self.builder.execute(env = dict,
                                            target = self,
                                            source = self.sources)
            except:
                raise BuildError(self, "Exception",
                                 sys.exc_type,
                                 sys.exc_value,
                                 sys.exc_traceback)
        if stat:
            raise BuildError(node = self, errstr = "Error %d" % stat)

        self.found_includes = {}

        # If we successfully build a node, then we need to rescan for
        # implicit dependencies, since it might have changed on us.
        self.scanned = {}

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
                dict = self.node.env.Dictionary()
                dict.update(self.node.env.autogenerate())
                try:
                    dir = self.node.getcwd()
                except AttributeError:
                    dir = None
                return self.node.builder.get_contents(env = dict)
        return Adapter(self)

    def scanner_set(self, scanner):
        self.scanner = scanner

    def src_scanner_set(self, key, scanner):
        self.src_scanners[key] = scanner

    def src_scanner_get(self, key):
        return self.src_scanners.get(key, None)

    def scan(self, scanner = None):
        if not scanner:
            scanner = self.scanner
        self.scanned[scanner] = 1

    def scanner_key(self):
        return None

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

    def store_sigs(self):
        """Make the signatures permanent (that is, store them in the
        .sconsign file or equivalent)."""
        pass

    def set_precious(self, precious = 1):
        """Set the Node's precious value."""
        self.precious = precious

    def prepare(self):
        """Prepare for this Node to be created:  no-op by default."""
        pass

    def add_dependency(self, depend):
	"""Adds dependencies. The depend argument must be a list."""
        self._add_child(self.depends, depend)

    def add_ignore(self, depend):
        """Adds dependencies to ignore. The depend argument must be a list."""
        self._add_child(self.ignore, depend)

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
            c.parents[self] = 1

    def add_wkid(self, wkid):
        """Add a node to the list of kids waiting to be evaluated"""
        if self.wkids != None:
            self.wkids.append(wkid)

    def children(self, scanner):
        """Return a list of the node's direct children, minus those
        that are ignored by this node."""
        return filter(lambda x, i=self.ignore: x not in i,
                      self.all_children(scanner))

    def all_children(self, scanner):
        """Return a list of all the node's direct children."""
        #XXX Need to remove duplicates from this
        if not self.implicit.has_key(scanner):
            self.scan(scanner)
        if scanner:
            implicit = self.implicit[scanner]
        else:
            implicit = reduce(lambda x, y: x + y, self.implicit.values(), [])
        return self.sources + self.depends + implicit

    def get_parents(self):
        return self.parents.keys()

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def current(self):
        return None

    def children_are_executed(self, scanner):
        return reduce(lambda x,y: ((y.get_state() == executed
                                   or y.get_state() == up_to_date)
                                   and x),
                      self.children(scanner),
                      1)

def get_children(node, parent): return node.children(None)
def ignore_cycle(node, stack): pass
def do_nothing(node, parent): pass

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
    def __init__(self, node, kids_func=get_children,
                             cycle_func=ignore_cycle,
                             eval_func=do_nothing):
        self.kids_func = kids_func
        self.cycle_func = cycle_func
        self.eval_func = eval_func
        node.wkids = copy.copy(kids_func(node, None))
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
                    node.wkids = copy.copy(self.kids_func(node, self.stack[-1]))
                    self.stack.append(node)
                    self.history[node] = None
            else:
                node = self.stack.pop()
                del self.history[node]
                if node:
                    if self.stack:
                        parent = self.stack[-1]
                    else:
                        parent = None
                    self.eval_func(node, parent)
                return node

    def is_done(self):
        return not self.stack


arg2nodes_lookups = []


def arg2nodes(arg, node_factory=None):
    """This function converts a string or list into a list of Node instances.
    It follows the rules outlined in the SCons design document by accepting
    any of the following inputs:
        - A single string containing names separated by spaces. These will be
          split apart at the spaces.
        - A single Node instance,
        - A list containingg either strings or Node instances. Any strings
          in the list are not split at spaces.
    In all cases, the function returns a list of Node instances."""

    narg = arg
    if SCons.Util.is_String(arg):
        narg = string.split(arg)
    elif not SCons.Util.is_List(arg):
        narg = [arg]

    nodes = []
    for v in narg:
        if SCons.Util.is_String(v):
            n = None
            for l in arg2nodes_lookups:
                n = l(v)
                if not n is None:
                    break
            if not n is None:
                nodes.append(n)
            elif node_factory:
                nodes.append(node_factory(v))
        # Do we enforce the following restriction?  Maybe, but it
        # would also restrict what we can do to allow people to
        # use the engine with alternate Node implementations...
        #elif not issubclass(v.__class__, Node):
        #    raise TypeError
        else:
            nodes.append(v)

    return nodes
