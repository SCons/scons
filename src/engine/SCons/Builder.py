"""SCons.Builder

Builder object subsystem.

A Builder object is a callable that encapsulates information about how
to execute actions to create a Node (file) from other Nodes (files), and
how to create those dependencies for tracking.

The main entry point here is the Builder() factory method.  This
provides a procedural interface that creates the right underlying
Builder object based on the keyword arguments supplied and the types of
the arguments.

The goal is for this external interface to be simple enough that the
vast majority of users can create new Builders as necessary to support
building new types of files in their configurations, without having to
dive any deeper into this subsystem.

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



import os.path
from SCons.Errors import InternalError, UserError

import SCons.Action
import SCons.Node
import SCons.Node.FS
import SCons.Util
import SCons.Warnings

class _Null:
    pass

_null = _Null

class DictCmdGenerator:
    """This is a callable class that can be used as a
    command generator function.  It holds on to a dictionary
    mapping file suffixes to Actions.  It uses that dictionary
    to return the proper action based on the file suffix of
    the source file."""
    
    def __init__(self, action_dict):
        self.action_dict = action_dict

    def src_suffixes(self):
        return self.action_dict.keys()

    def add_action(self, suffix, action):
        """Add a suffix-action pair to the mapping.
        """
        self.action_dict[suffix] = action

    def __call__(self, target, source, env, for_signature):
        ext = None
        for src in map(str, source):
            my_ext = SCons.Util.splitext(src)[1]
            if ext and my_ext != ext:
                raise UserError("Cannot build multiple sources with different extensions: %s, %s" % (ext, my_ext))
            ext = my_ext

        if ext is None:
            raise UserError("Cannot deduce file extension from source files: %s" % repr(map(str, source)))
        try:
            # XXX Do we need to perform Environment substitution
            # on the keys of action_dict before looking it up?
            return self.action_dict[ext]
        except KeyError:
            raise UserError("Don't know how to build a file with suffix %s." % ext)
    def __cmp__(self, other):
        return cmp(self.action_dict, other.action_dict)

def Builder(**kw):
    """A factory for builder objects."""
    composite = None
    if kw.has_key('generator'):
        if kw.has_key('action'):
            raise UserError, "You must not specify both an action and a generator."
        kw['action'] = SCons.Action.CommandGenerator(kw['generator'])
        del kw['generator']
    elif kw.has_key('action') and SCons.Util.is_Dict(kw['action']):
        composite = DictCmdGenerator(kw['action'])
        kw['action'] = SCons.Action.CommandGenerator(composite)
        kw['src_suffix'] = composite.src_suffixes()

    if kw.has_key('emitter') and \
       SCons.Util.is_String(kw['emitter']):
        # This allows users to pass in an Environment
        # variable reference (like "$FOO") as an emitter.
        # We will look in that Environment variable for
        # a callable to use as the actual emitter.
        var = SCons.Util.get_environment_var(kw['emitter'])
        if not var:
            raise UserError, "Supplied emitter '%s' does not appear to refer to an Environment variable" % kw['emitter']
        kw['emitter'] = EmitterProxy(var)

    if kw.has_key('src_builder'):
        ret = apply(MultiStepBuilder, (), kw)
    else:
        ret = apply(BuilderBase, (), kw)

    if composite:
        ret = CompositeBuilder(ret, composite)

    return ret

def _init_nodes(builder, env, overrides, tlist, slist):
    """Initialize lists of target and source nodes with all of
    the proper Builder information.
    """

    for s in slist:
        src_key = s.scanner_key()        # the file suffix
        scanner = env.get_scanner(src_key)
        if scanner:
            s.source_scanner = scanner

    for t in tlist:
        if t.side_effect:
            raise UserError, "Multiple ways to build the same target were specified for: %s" % str(t)
        if t.has_builder():
            if t.env != env:
                raise UserError, "Two different environments were specified for the same target: %s"%str(t)
            elif t.overrides != overrides:
                raise UserError, "Two different sets of overrides were specified for the same target: %s"%str(t)
            elif builder.scanner and builder.scanner != t.target_scanner:
                raise UserError, "Two different scanners were specified for the same target: %s"%str(t)

            if builder.multi:
                if t.builder != builder:
                    if isinstance(t.builder, ListBuilder) and isinstance(builder, ListBuilder) and t.builder.builder == builder.builder:
                        raise UserError, "Two different target sets have a target in common: %s"%str(t)
                    else:
                        raise UserError, "Two different builders (%s and %s) were specified for the same target: %s"%(t.builder.get_name(env), builder.get_name(env), str(t))
            elif t.sources != slist:
                raise UserError, "Multiple ways to build the same target were specified for: %s" % str(t)

        t.overrides = overrides
        t.cwd = SCons.Node.FS.default_fs.getcwd()
        t.builder_set(builder)
        t.env_set(env)
        t.add_source(slist)
        if builder.scanner:
            t.target_scanner = builder.scanner

def _adjust_suffix(suff):
    if suff and not suff[0] in [ '.', '$' ]:
        return '.' + suff
    return suff

class EmitterProxy:
    """This is a callable class that can act as a
    Builder emitter.  It holds on to a string that
    is a key into an Environment dictionary, and will
    look there at actual build time to see if it holds
    a callable.  If so, we will call that as the actual
    emitter."""
    def __init__(self, var):
        self.var = SCons.Util.to_String(var)

    def __call__(self, target, source, env):
        emitter = self.var

        # Recursively substitute the variable.
        # We can't use env.subst() because it deals only
        # in strings.  Maybe we should change that?
        while SCons.Util.is_String(emitter) and \
              env.has_key(emitter):
            emitter = env[emitter]
        if not callable(emitter):
            return (target, source)

        return emitter(target, source, env)

    def __cmp__(self, other):
        return cmp(self.var, other.var)

class BuilderBase:
    """Base class for Builders, objects that create output
    nodes (files) from input nodes (files).
    """

    def __init__(self,  action = None,
                        prefix = '',
                        suffix = '',
                        src_suffix = '',
                        node_factory = SCons.Node.FS.default_fs.File,
                        target_factory = None,
                        source_factory = None,
                        scanner = None,
                        emitter = None,
                        multi = 0,
                        env = None,
                        overrides = {}):
        self.action = SCons.Action.Action(action)
        self.multi = multi
        self.prefix = prefix
        self.suffix = suffix
        self.env = env
        self.overrides = overrides

        self.set_src_suffix(src_suffix)

        self.target_factory = target_factory or node_factory
        self.source_factory = source_factory or node_factory
        self.scanner = scanner

        self.emitter = emitter

    def __nonzero__(self):
        raise InternalError, "Do not test for the Node.builder attribute directly; use Node.has_builder() instead"

    def get_name(self, env):
        """Attempts to get the name of the Builder.

        Look at the BUILDERS variable of env, expecting it to be a
        dictionary containing this Builder, and return the key of the
        dictionary."""

        try:
            index = env['BUILDERS'].values().index(self)
            return env['BUILDERS'].keys()[index]
        except (AttributeError, KeyError, ValueError):
            return str(self.__class__)

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def _create_nodes(self, env, overrides, target = None, source = None):
        """Create and return lists of target and source nodes.
        """
        def adjustixes(files, pre, suf):
            if not files:
                return []
            ret = []
            if not SCons.Util.is_List(files):
                files = [files]

            for f in files:
                if SCons.Util.is_String(f):
                    if pre and f[:len(pre)] != pre:
                        path, fn = os.path.split(os.path.normpath(f))
                        f = os.path.join(path, pre + fn)
                    # Only append a suffix if the file does not have one.
                    if suf and not SCons.Util.splitext(f)[1]:
                        if f[-len(suf):] != suf:
                            f = f + suf
                ret.append(f)
            return ret

        env = env.Override(overrides)

        pre = self.get_prefix(env)
        suf = self.get_suffix(env)
        src_suf = self.get_src_suffix(env)

        source = adjustixes(source, None, src_suf)
        if target is None:
            s = source[0]
            if isinstance(s, SCons.Node.Node):
                s = os.path.split(str(s))[1]
            target = [ pre + os.path.splitext(s)[0] + suf ]
        else:
            target = adjustixes(target, pre, suf)

        slist = SCons.Node.arg2nodes(source, self.source_factory)
        tlist = SCons.Node.arg2nodes(target, self.target_factory)

        if self.emitter:
            # The emitter is going to do str(node), but because we're
            # being called *from* a builder invocation, the new targets
            # don't yet have a builder set on them and will look like
            # source files.  Fool the emitter's str() calls by setting
            # up a temporary builder on the new targets.
            new_targets = []
            for t in tlist:
                if not t.is_derived():
                    t.builder = self
                    new_targets.append(t)
        
            target, source = self.emitter(target=tlist, source=slist, env=env)

            # Now delete the temporary builders that we attached to any
            # new targets, so that _init_nodes() doesn't do weird stuff
            # to them because it thinks they already have builders.
            for t in new_targets:
                if t.builder is self:
                    # Only delete the temporary builder if the emitter
                    # didn't change it on us.
                    t.builder = None

            # Have to call arg2nodes yet again, since it is legal for
            # emitters to spit out strings as well as Node instances.
            slist = SCons.Node.arg2nodes(source, self.source_factory)
            tlist = SCons.Node.arg2nodes(target, self.target_factory)

        return tlist, slist

    def __call__(self, env, target = None, source = _null, **overrides):
        if source is _null:
            source = target
            target = None
        tlist, slist = self._create_nodes(env, overrides, target, source)

        if len(tlist) == 1:
            _init_nodes(self, env, overrides, tlist, slist)
            tlist = tlist[0]
        else:
            _init_nodes(ListBuilder(self, env, tlist), env, overrides, tlist, slist)

        return tlist

    def get_actions(self):
        return self.action.get_actions()

    def get_raw_contents(self, target, source, env):
        """Fetch the "contents" of the builder's action.
        """
        return self.action.get_raw_contents(target, source, env)

    def get_contents(self, target, source, env):
        """Fetch the "contents" of the builder's action
        (for signature calculation).
        """
        return self.action.get_contents(target, source, env)

    def src_suffixes(self, env):
        return map(lambda x, e=env: e.subst(_adjust_suffix(x)),
                   self.src_suffix)

    def set_src_suffix(self, src_suffix):
        if not src_suffix:
            src_suffix = []
        elif not SCons.Util.is_List(src_suffix):
            src_suffix = [ src_suffix ]
        self.src_suffix = src_suffix

    def get_src_suffix(self, env):
        """Get the first src_suffix in the list of src_suffixes."""
        ret = self.src_suffixes(env)
        if not ret:
            return ''
        return ret[0]

    def get_suffix(self, env):
        return env.subst(_adjust_suffix(self.suffix))

    def get_prefix(self, env):
        return env.subst(self.prefix)

    def targets(self, node):
        """Return the list of targets for this builder instance.

        For most normal builders, this is just the supplied node.
        """
        return [ node ]

class ListBuilder(SCons.Util.Proxy):
    """A Proxy to support building an array of targets (for example,
    foo.o and foo.h from foo.y) from a single Action execution.
    """

    def __init__(self, builder, env, tlist):
        SCons.Util.Proxy.__init__(self, builder)
        self.builder = builder
        self.scanner = builder.scanner
        self.env = env
        self.tlist = tlist
        self.multi = builder.multi

    def targets(self, node):
        """Return the list of targets for this builder instance.
        """
        return self.tlist

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def get_name(self, env):
        """Attempts to get the name of the Builder."""

        return "ListBuilder(%s)" % self.builder.get_name(env)

class MultiStepBuilder(BuilderBase):
    """This is a builder subclass that can build targets in
    multiple steps.  The src_builder parameter to the constructor
    accepts a builder that is called to build sources supplied to
    this builder.  The targets of that first build then become
    the sources of this builder.

    If this builder has a src_suffix supplied, then the src_builder
    builder is NOT invoked if the suffix of a source file matches
    src_suffix.
    """
    def __init__(self,  src_builder,
                        action = None,
                        prefix = '',
                        suffix = '',
                        src_suffix = '',
                        node_factory = SCons.Node.FS.default_fs.File,
                        target_factory = None,
                        source_factory = None,
                        scanner=None,
                        emitter=None):
        BuilderBase.__init__(self, action, prefix, suffix, src_suffix,
                             node_factory, target_factory, source_factory,
                             scanner, emitter)
        if not SCons.Util.is_List(src_builder):
            src_builder = [ src_builder ]
        self.src_builder = src_builder
        self.sdict = {}
        self.cached_src_suffixes = {} # source suffixes keyed on id(env)

    def __call__(self, env, target = None, source = _null, **kw):
        if source is _null:
            source = target
            target = None

        slist = SCons.Node.arg2nodes(source, self.source_factory)
        final_sources = []

        try:
            sdict = self.sdict[id(env)]
        except KeyError:
            sdict = {}
            self.sdict[id(env)] = sdict
            for bld in self.src_builder:
                if SCons.Util.is_String(bld):
                    try:
                        bld = env['BUILDERS'][bld]
                    except KeyError:
                        continue
                for suf in bld.src_suffixes(env):
                    sdict[suf] = bld

        src_suffixes = self.src_suffixes(env)

        for snode in slist:
            path, ext = SCons.Util.splitext(snode.get_abspath())
            if sdict.has_key(ext):
                src_bld = sdict[ext]
                tgt = apply(src_bld, (env, path, snode), kw)
                # Only supply the builder with sources it is capable
                # of building.
                if SCons.Util.is_List(tgt):
                    tgt = filter(lambda x, suf=src_suffixes:
                                 SCons.Util.splitext(SCons.Util.to_String(x))[1] in suf,
                                 tgt)
                if not SCons.Util.is_List(tgt):
                    final_sources.append(tgt)
                else:
                    final_sources.extend(tgt)
            else:
                final_sources.append(snode)

        return apply(BuilderBase.__call__,
                     (self, env, target, final_sources), kw)

    def get_src_builders(self, env):
        """Return all the src_builders for this Builder.

        This is essentially a recursive descent of the src_builder "tree."
        """
        ret = []
        for bld in self.src_builder:
            if SCons.Util.is_String(bld):
                # All Environments should have a BUILDERS
                # variable, so no need to check for it.
                try:
                    bld = env['BUILDERS'][bld]
                except KeyError:
                    continue
            ret.append(bld)
        return ret

    def src_suffixes(self, env):
        """Return a list of the src_suffix attributes for all
        src_builders of this Builder.
        """
        try:
            return self.cached_src_suffixes[id(env)]
        except KeyError:
            suffixes = BuilderBase.src_suffixes(self, env)
            for builder in self.get_src_builders(env):
                suffixes.extend(builder.src_suffixes(env))
            self.cached_src_suffixes[id(env)] = suffixes
            return suffixes

class CompositeBuilder(SCons.Util.Proxy):
    """A Builder Proxy whose main purpose is to always have
    a DictCmdGenerator as its action, and to provide access
    to the DictCmdGenerator's add_action() method.
    """

    def __init__(self, builder, cmdgen):
        SCons.Util.Proxy.__init__(self, builder)

        # cmdgen should always be an instance of DictCmdGenerator.
        self.cmdgen = cmdgen
        self.builder = builder

    def add_action(self, suffix, action):
        self.cmdgen.add_action(suffix, action)
        self.set_src_suffix(self.cmdgen.src_suffixes())
        
    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)
