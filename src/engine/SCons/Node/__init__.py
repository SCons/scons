"""SCons.Node

The Node package for the SCons software construction utility.

This is, in many ways, the heart of SCons.

A Node is where we encapsulate all of the dependency information about
any thing that SCons can build, or about any thing which SCons can use
to build some other thing.  The canonical "thing," of course, is a file,
but a Node can also represent something remote (like a web page) or
something completely abstract (like an Alias).

Each specific type of "thing" is specifically represented by a subclass
of the Node base class:  Node.FS.File for files, Node.Alias for aliases,
etc.  Dependency information is kept here in the base class, and
information specific to files/aliases/etc. is in the subclass.  The
goal, if we've done this correctly, is that any type of "thing" should
be able to depend on any other type of "thing."

"""

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



import copy

import SCons.Sig
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

# A variable that can be set to an interface-specific function be called
# to annotate a Node with information about its creation.
def do_nothing(node): pass

Annotate = do_nothing

class Node:
    """The base Node class, for entities that we know how to
    build, or use to build other Nodes.
    """

    class Attrs:
        pass

    def __init__(self):
        # Note that we no longer explicitly initialize a self.builder
        # attribute to None here.  That's because the self.builder
        # attribute may be created on-the-fly later by a subclass (the
        # canonical example being a builder to fetch a file from a
        # source code system like CVS or Subversion).

        self.sources = []       # source files used to build node
        self.depends = []       # explicit dependencies (from Depends)
        self.implicit = None    # implicit (scanned) dependencies (None means not scanned yet)
        self.ignore = []        # dependencies to ignore
        self.parents = {}
        self.wkids = None       # Kids yet to walk, when it's an array
        self.source_scanner = None      # implicit scanner from scanner map
        self.target_scanner = None      # explicit scanner from this node's Builder

        self.env = None
        self.state = None
        self.precious = None
        self.found_includes = {}
        self.includes = None
        self.overrides = {}     # construction variable overrides for building this node
        self.attributes = self.Attrs() # Generic place to stick information about the Node.
        self.side_effect = 0 # true iff this node is a side effect
        self.side_effects = [] # the side effects of building this target
        self.pre_actions = []
        self.post_actions = []
        self.linked = 0 # is this node linked to the build directory? 

        # Let the interface in which the build engine is embedded
        # annotate this Node with its own info (like a description of
        # what line in what file created the node, for example).
        Annotate(self)

    def generate_build_env(self):
        """Generate the appropriate Environment to build this node."""
        if self.env is None:
            # The node itself doesn't have an associated Environment
            # (which kind of implies it's a source code file, but who
            # knows...).  Regardless of why, use the environment (if
            # any) associated with the Builder itself.
            env = self.builder.env
            overrides = self.builder.overrides
        else:
            # The normal case: use the Environment used to specify how
            # this Node is to be built.
            env = self.env
            overrides = self.overrides
        return env.Override(overrides)

    def _for_each_action(self, func):
        """Call a function for each action required to build a node.

        The purpose here is to have one place for the logic that
        collects and executes all of the actions for a node's builder,
        even though multiple sections of code elsewhere need this logic
        to do different things."""
        if not self.has_builder():
            return
        action_list = self.pre_actions + \
                      self.builder.get_actions() + \
                      self.post_actions
        if not action_list:
            return
        targets = self.builder.targets(self)
        env = self.generate_build_env()
        for action in action_list:
            func(action, targets, self.sources, env)

    def build(self):
        """Actually build the node.

        This method is called from multiple threads in a parallel build,
        so only do thread safe stuff here. Do thread unsafe stuff in
        built().
        """
        def do_action(action, targets, sources, env, self=self):
            stat = action(targets, sources, env)
            if stat:
                raise SCons.Errors.BuildError(node = self,
                                              errstr = "Error %d" % stat)
        self._for_each_action(do_action)

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
                node.del_bsig()
            w = Walker(self, get_parents, ignore_cycle, clear_cache)
            while w.next(): pass

        # clear out the content signature, since the contents of this
        # node were presumably just changed:
        self.del_csig()

    def clear(self):
        """Completely clear a Node of all its cached state (so that it
        can be re-evaluated by interfaces that do continuous integration
        builds).
        """
        self.set_state(None)
        self.del_bsig()
        self.del_csig()
        self.includes = None
        self.found_includes = {}
        self.implicit = None

    def visited(self):
        """Called just after this node has been visited
        without requiring a build.."""
        pass

    def depends_on(self, nodes):
        """Does this node depend on any of 'nodes'?"""
        for node in nodes:
            if node in self.children():
                return 1

        return 0

    def builder_set(self, builder):
        self.builder = builder

    def has_builder(self):
        """Return whether this Node has a builder or not.

        In Boolean tests, this turns out to be a *lot* more efficient
        than simply examining the builder attribute directly ("if
        node.builder: ..."). When the builder attribute is examined
        directly, it ends up calling __getattr__ for both the __len__
        and __nonzero__ attributes on instances of our Builder Proxy
        class(es), generating a bazillion extra calls and slowing
        things down immensely.
        """
        try:
            b = self.builder
        except AttributeError:
            # There was no explicit builder for this Node, so initialize
            # the self.builder attribute to None now.
            self.builder = None
            b = self.builder
        return not b is None

    def is_derived(self):
        return self.has_builder() or self.side_effect

    def alter_targets(self):
        """Return a list of alternate targets for this Node.
        """
        return [], None

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
                return self.node.builder.get_contents(self.node.builder.targets(self.node), self.node.sources, self.node.generate_build_env())
            def get_timestamp(self):
                return None
        return Adapter(self)

    def get_found_includes(self, env, scanner, target):
        """Return the scanned include lines (implicit dependencies)
        found in this node.

        The default is no implicit dependencies.  We expect this method
        to be overridden by any subclass that can be scanned for
        implicit dependencies.
        """
        return []

    def get_implicit_deps(self, env, scanner, target):
        """Return a list of implicit dependencies for this node.

        This method exists to handle recursive invocation of the scanner
        on the implicit dependencies returned by the scanner, if the
        scanner's recursive flag says that we should.
        """
        if not scanner:
            return []

        try:
            recurse = scanner.recursive
        except AttributeError:
            recurse = None

        nodes = [self]
        seen = {}
        seen[self] = 1
        deps = []
        while nodes:
           n = nodes.pop(0)
           d = filter(lambda x, seen=seen: not seen.has_key(x),
                      n.get_found_includes(env, scanner, target))
           if d:
               deps.extend(d)
               for n in d:
                   seen[n] = 1
               if recurse:
                   nodes.extend(d)

        return deps

    # cache used to make implicit_factory fast.
    implicit_factory_cache = {}
    
    def implicit_factory(self, path):
        """
        Turn a cache implicit dependency path into a node.
        This is called so many times that doing caching
        here is a significant perforamnce boost.
        """
        try:
            return self.implicit_factory_cache[path]
        except KeyError:
            n = self.builder.source_factory(path)
            self.implicit_factory_cache[path] = n
            return n

    def scan(self):
        """Scan this node's dependents for implicit dependencies."""
        # Don't bother scanning non-derived files, because we don't
        # care what their dependencies are.
        # Don't scan again, if we already have scanned.
        if not self.implicit is None:
            return
        self.implicit = []
        if not self.has_builder():
            return

        if implicit_cache and not implicit_deps_changed:
            implicit = self.get_stored_implicit()
            if implicit is not None:
                implicit = map(self.implicit_factory, implicit)
                self._add_child(self.implicit, implicit)
                calc = SCons.Sig.default_calc
                if implicit_deps_unchanged or calc.current(self, calc.bsig(self)):
                    return
                else:
                    # one of this node's sources has changed, so
                    # we need to recalculate the implicit deps,
                    # and the bsig:
                    self.implicit = []
                    self.del_bsig()

        build_env = self.generate_build_env()

        for child in self.children(scan=0):
            self._add_child(self.implicit,
                            child.get_implicit_deps(build_env,
                                                    child.source_scanner,
                                                    self))

        # scan this node itself for implicit dependencies
        self._add_child(self.implicit,
                        self.get_implicit_deps(build_env,
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

    def calc_signature(self, calc, cache=None):
        """
        Select and calculate the appropriate build signature for a node.

        self - the node
        calc - the signature calculation module
        cache - alternate node to use for the signature cache
        returns - the signature
        """

        if self.has_builder():
            if SCons.Sig.build_signature:
                return calc.bsig(self, cache)
            else:
                return calc.csig(self, cache)
        elif not self.exists():
            return None
        else:
            return calc.csig(self, cache)

    def get_bsig(self):
        """Get the node's build signature (based on the signatures
        of its dependency files and build information)."""
        if not hasattr(self, 'bsig'):
            return None
        return self.bsig

    def set_bsig(self, bsig):
        """Set the node's build signature (based on the signatures
        of its dependency files and build information)."""
        self.bsig = bsig

    def store_bsig(self):
        """Make the build signature permanent (that is, store it in the
        .sconsign file or equivalent)."""
        pass

    def del_bsig(self):
        """Delete the bsig from this node."""
        if hasattr(self, 'bsig'):
            delattr(self, 'bsig')

    def get_csig(self):
        """Get the signature of the node's content."""
        if not hasattr(self, 'csig'):
            return None
        return self.csig

    def set_csig(self, csig):
        """Set the signature of the node's content."""
        self.csig = csig

    def store_csig(self):
        """Make the content signature permanent (that is, store it in the
        .sconsign file or equivalent)."""
        pass

    def del_csig(self):
        """Delete the csig from this node."""
        if hasattr(self, 'csig'):
            delattr(self, 'csig')

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

    def exists(self):
        """Does this node exists?"""
        # All node exist by default:
        return 1
    
    def rexists(self):
        """Does this node exist locally or in a repositiory?"""
        # There are no repositories by default:
        return self.exists()
    
    def prepare(self):
        """Prepare for this Node to be created.
        The default implemenation checks that all children either exist
        or are derived.
        """
        def missing(node):
            return not node.is_derived() and not node.linked and not node.rexists()
        missing_sources = filter(missing, self.children())
        if missing_sources:
            desc = "No Builder for target `%s', needed by `%s'." % (missing_sources[0], self)
            raise SCons.Errors.StopError, desc

    def remove(self):
        """Remove this Node:  no-op by default."""
        return None

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
        # The return list may contain duplicate Nodes, especially in
        # source trees where there are a lot of repeated #includes
        # of a tangle of .h files.  Profiling shows, however, that
        # eliminating the duplicates with a brute-force approach that
        # preserves the order (that is, something like:
        #
        #       u = []
        #       for n in list:
        #           if n not in u:
        #               u.append(n)"
        #
        # takes more cycles than just letting the underlying methods
        # hand back cached values if a Node's information is requested
        # multiple times.  (Other methods of removing duplicates, like
        # using dictionary keys, lose the order, and the only ordered
        # dictionary patterns I found all ended up using "not in"
        # internally anyway...)
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

    def current(self, calc=None):
        return None

    def rfile(self):
        return self

    def rstr(self):
        return str(self)

    def is_literal(self):
        """Always pass the string representation of a Node to
        the command interpreter literally."""
        return 1

    def add_pre_action(self, act):
        """Adds an Action performed on this Node only before
        building it."""
        self.pre_actions.append(act)

    def add_post_action(self, act):
        """Adds and Action performed on this Node only after
        building it."""
        self.post_actions.append(act)

    def render_include_tree(self):
        """
        Return a text representation, suitable for displaying to the
        user, of the include tree for the sources of this node.
        """
        if self.has_builder() and self.env:
            env = self.generate_build_env()
            for s in self.sources:
                def f(node, env=env, scanner=s.source_scanner, target=self):
                    return node.get_found_includes(env, scanner, target)
                return SCons.Util.render_tree(s, f, 1)
        else:
            return None

    def get_abspath(self):
        """
        Return an absolute path to the Node.  This will return simply
        str(Node) by default, but for Node types that have a concept of
        relative path, this might return something different.
        """
        return str(self)

    def for_signature(self):
        """
        Return a string representation of the Node that will always
        be the same for this particular Node, no matter what.  This
        is by contrast to the __str__() method, which might, for
        instance, return a relative path for a file Node.  The purpose
        of this method is to generate a value to be used in signature
        calculation for the command line used to build a target, and
        we use this method instead of str() to avoid unnecessary
        rebuilds.  This method does not need to return something that
        would actually work in a command line; it can return any kind of
        nonsense, so long as it does not change.
        """
        return str(self)

    def get_string(self, for_signature):
        """This is a convenience function designed primarily to be
        used in command generators (i.e., CommandGeneratorActions or
        Environment variables that are callable), which are called
        with a for_signature argument that is nonzero if the command
        generator is being called to generate a signature for the
        command line, which determines if we should rebuild or not.

        Such command generators shoud use this method in preference
        to str(Node) when converting a Node to a string, passing
        in the for_signature parameter, such that we will call
        Node.for_signature() or str(Node) properly, depending on whether
        we are calculating a signature or actually constructing a
        command line."""
        if for_signature:
            return self.for_signature()
        return str(self)

    def get_subst_proxy(self):
        """
        This method is expected to return an object that will function
        exactly like this Node, except that it implements any additional
        special features that we would like to be in effect for
        Environment variable substitution.  The principle use is that
        some Nodes would like to implement a __getattr__() method,
        but putting that in the Node type itself has a tendency to kill
        performance.  We instead put it in a proxy and return it from
        this method.  It is legal for this method to return self
        if no new functionality is needed for Environment substitution.
        """
        return self
        

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

def arg2nodes(args, node_factory=None, lookup_list=arg2nodes_lookups):
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
            for l in lookup_list:
                n = l(v)
                if not n is None:
                    break
            if not n is None:
                if SCons.Util.is_String(n) and node_factory:
                    n = node_factory(n)
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
