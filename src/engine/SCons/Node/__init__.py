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
import SCons.Sig

from SCons.Errors import BuildError, UserError
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
stack = 6 # nodes that are in the current Taskmaster execution stack

# controls whether implicit depedencies are cached:
implicit_cache = 0

# controls whether implicit dep changes are ignored:
implicit_deps_unchanged = 0

# controls whether the cached implicit deps are ignored:
implicit_deps_changed = 0


class Node:
    """The base Node class, for entities that we know how to
    build, or use to build other Nodes.
    """

    class Attrs:
        pass

    def __init__(self):
        self.sources = []       # source files used to build node
        self.depends = []       # explicit dependencies (from Depends)
        self.implicit = None    # implicit (scanned) dependencies (None means not scanned yet)
        self.ignore = []        # dependencies to ignore
        self.parents = {}
        self.wkids = None       # Kids yet to walk, when it's an array
        self.builder = None
        self.source_scanner = None      # implicit scanner from scanner map
        self.target_scanner = None      # explicit scanner from this node's Builder
        self.env = None
        self.state = None
        self.bsig = None
        self.csig = None
        self.use_signature = 1
        self.precious = None
        self.found_includes = {}
        self.includes = None
        self.build_args = {}
        self.attributes = self.Attrs() # Generic place to stick information about the Node.
        self.side_effect = 0 # true iff this node is a side effect
        self.side_effects = [] # the side effects of building this target

    def generate_build_args(self):
        dict = copy.copy(self.env.Dictionary())
        if hasattr(self, 'cwd'):
            auto = self.env.autogenerate(dir = self.cwd)
        else:
            auto = self.env.autogenerate()
        dict.update(auto)

        dictArgs = { 'env' : dict,
                     'target' : self,
                     'source' : self.sources }
        dictArgs.update(self.build_args)
        return dictArgs

    def build(self):
        """Actually build the node.   Return the status from the build."""
        # This method is called from multiple threads in a parallel build,
        # so only do thread safe stuff here. Do thread unsafe stuff in built().
        if not self.builder:
            return None
        try:
            # If this Builder instance has already been called,
            # there will already be an associated status.
            stat = self.builder.status
        except AttributeError:
            try:
                stat = apply(self.builder.execute, (),
                             self.generate_build_args())
            except KeyboardInterrupt:
                raise
            except UserError:
                raise
            except:
                raise BuildError(self, "Exception",
                                 sys.exc_type,
                                 sys.exc_value,
                                 sys.exc_traceback)
        if stat:
            raise BuildError(node = self, errstr = "Error %d" % stat)

        return stat

    def built(self):
        """Called just after this node is sucessfully built."""
        self.store_bsig()

        # Clear out the implicit dependency caches:
        # XXX this really should somehow be made more general and put
        #     under the control of the scanners.
        if self.source_scanner:
            self.found_includes = {}
            self.includes = None

            def get_parents(node, parent): return node.get_parents()
            def clear_cache(node, parent):
                node.implicit = None
                node.bsig = None
            w = Walker(self, get_parents, ignore_cycle, clear_cache)
            while w.next(): pass

        # clear out the content signature, since the contents of this
        # node were presumably just changed:
        self.csig = None

    def depends_on(self, nodes):
        """Does this node depend on any of 'nodes'?"""
        for node in nodes:
            if node in self.children():
                return 1

        return 0

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
                return apply(self.node.builder.get_contents, (),
                             self.node.generate_build_args())
            def get_timestamp(self):
                return None
        return Adapter(self)

    def get_implicit_deps(self, env, scanner, target):
        """Return a list of implicit dependencies for this node"""
        return []

    def scan(self):
        """Scan this node's dependents for implicit dependencies."""
        # Don't bother scanning non-derived files, because we don't
        # care what their dependencies are.
        # Don't scan again, if we already have scanned.
        if not self.implicit is None:
            return
        self.implicit = []
        if not self.builder:
            return

        if implicit_cache and not implicit_deps_changed:
            implicit = self.get_stored_implicit()
            if implicit is not None:
                implicit = map(self.builder.source_factory, implicit)
                self._add_child(self.implicit, implicit)
                calc = SCons.Sig.default_calc
                if implicit_deps_unchanged or calc.current(self, calc.bsig(self)):
                    return
                else:
                    # one of this node's sources has changed, so 
                    # we need to recalculate the implicit deps,
                    # and the bsig:
                    self.implicit = []
                    self.bsig = None

        for child in self.children(scan=0):
            self._add_child(self.implicit,
                            child.get_implicit_deps(self.env,
                                                    child.source_scanner,
                                                    self))

        # scan this node itself for implicit dependencies
        self._add_child(self.implicit,
                        self.get_implicit_deps(self.env,
                                               self.target_scanner,
                                               self))

        if implicit_cache:
            self.store_implicit()

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

    def store_bsig(self):
        """Make the build signature permanent (that is, store it in the
        .sconsign file or equivalent)."""
        pass

    def get_csig(self):
        """Get the signature of the node's content."""
        return self.csig

    def set_csig(self, csig):
        """Set the signature of the node's content."""
        self.csig = csig

    def store_csig(self):
        """Make the content signature permanent (that is, store it in the
        .sconsign file or equivalent)."""
        pass

    def get_prevsiginfo(self):
        """Fetch the previous signature information from the
        .sconsign entry."""
        return None

    def get_timestamp(self):
        return 0

    def store_timestamp(self):
        """Make the timestamp permanent (that is, store it in the
        .sconsign file or equivalent)."""
        pass

    def store_implicit(self):
        """Make the implicit deps permanent (that is, store them in the
        .sconsign file or equivalent)."""
        pass

    def get_stored_implicit(self):
        """Fetch the stored implicit dependencies"""
        return None

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

    def children(self, scan=1):
        """Return a list of the node's direct children, minus those
        that are ignored by this node."""
        return filter(lambda x, i=self.ignore: x not in i,
                      self.all_children(scan))

    def all_children(self, scan=1):
        """Return a list of all the node's direct children."""
        #XXX Need to remove duplicates from this
        if scan:
            self.scan()
        if self.implicit is None:
            return self.sources + self.depends
        else:
            return self.sources + self.depends + self.implicit

    def get_parents(self):
        return self.parents.keys()

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def current(self):
        return None

def get_children(node, parent): return node.children()
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

def arg2nodes(args, node_factory=None):
    """This function converts a string or list into a list of Node
    instances.  It accepts the following inputs:
        - A single string,
        - A single Node instance,
        - A list containing either strings or Node instances.
    In all cases, strings are converted to Node instances, and the
    function returns a list of Node instances."""

    if not args:
        return []
    if not SCons.Util.is_List(args):
        args = [args]

    nodes = []
    for v in args:
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
