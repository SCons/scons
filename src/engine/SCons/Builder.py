"""SCons.Builder

XXX

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



import os.path
import string
import copy
from SCons.Errors import UserError

import SCons.Action
import SCons.Node
import SCons.Node.FS
import SCons.Util
import SCons.Warnings

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

    def __call__(self, source, target, env, **kw):
        ext = None
        for src in map(str, source):
            my_ext = os.path.splitext(src)[1]
            if ext and my_ext != ext:
                raise UserError("Cannot build multiple sources with different extensions.")
            ext = my_ext

        if ext is None:
            raise UserError("Cannot deduce file extension from source files: %s" % repr(map(str, source)))
        try:
            # XXX Do we need to perform Environment substitution
            # on the keys of action_dict before looking it up?
            return self.action_dict[ext]
        except KeyError:
            raise UserError("Don't know how to build a file with suffix %s." % ext)

def Builder(**kw):
    """A factory for builder objects."""
    if kw.has_key('name'):
        SCons.Warnings.warn(SCons.Warnings.DeprecatedWarning,
                            "The use of the 'name' parameter to Builder() is deprecated.")
    if kw.has_key('generator'):
        if kw.has_key('action'):
            raise UserError, "You must not specify both an action and a generator."
        kw['action'] = SCons.Action.CommandGenerator(kw['generator'])
        del kw['generator']
    elif kw.has_key('action') and SCons.Util.is_Dict(kw['action']):
        action_dict = kw['action']
        kw['action'] = SCons.Action.CommandGenerator(DictCmdGenerator(action_dict))
        kw['src_suffix'] = action_dict.keys()

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
        return apply(MultiStepBuilder, (), kw)
    else:
        return apply(BuilderBase, (), kw)

def _init_nodes(builder, env, args, tlist, slist):
    """Initialize lists of target and source nodes with all of
    the proper Builder information.
    """

    for s in slist:
        src_key = s.scanner_key()        # the file suffix
        scanner = env.get_scanner(src_key)
        if scanner:
            s.source_scanner = scanner

    for t in tlist:
        if t.builder is not None:
            if t.env != env: 
                raise UserError, "Two different environments were specified for the same target: %s"%str(t)
            elif t.build_args != args:
                raise UserError, "Two different sets of build arguments were specified for the same target: %s"%str(t)
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

        t.build_args = args
        t.cwd = SCons.Node.FS.default_fs.getcwd()
        t.builder_set(builder)
        t.env_set(env)
        t.add_source(slist)
        if builder.scanner:
            t.target_scanner = builder.scanner
        
class _callable_adaptor:
    """When crteating a Builder, you can pass a string OR
    a callable in for prefix, suffix, or src_suffix.
    src_suffix even takes a list!

    If a string or list is passed, we use this class to
    adapt it to a callable."""
    def __init__(self, static):
        self.static = static

    def __call__(self, **kw):
        return self.static

    def __cmp__(self, other):
        if isinstance(other, _callable_adaptor):
            return cmp(self.static, other.static)
        return -1

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

    def __call__(self, target, source, env, **kw):
        emitter = self.var

        # Recursively substitue the variable.
        # We can't use env.subst() because it deals only
        # in strings.  Maybe we should change that?
        while SCons.Util.is_String(emitter) and \
              env.has_key(emitter):
            emitter = env[emitter]
        if not callable(emitter):
            return (target, source)
        args = { 'target':target,
                 'source':source,
                 'env':env }
        args.update(kw)
        return apply(emitter, (), args)

class BuilderBase:
    """Base class for Builders, objects that create output
    nodes (files) from input nodes (files).
    """

    def __init__(self,  name = None,
                        action = None,
                        prefix = '',
                        suffix = '',
                        src_suffix = '',
                        node_factory = SCons.Node.FS.default_fs.File,
                        target_factory = None,
                        source_factory = None,
                        scanner = None,
                        emitter = None,
                        multi = 0):
        self.name = name
        self.action = SCons.Action.Action(action)
        self.multi = multi

        if callable(prefix):
            self.prefix = prefix
        else:
            self.prefix = _callable_adaptor(str(prefix))

        if callable(suffix):
            self.suffix = suffix
        else:
            self.suffix = _callable_adaptor(str(suffix))

        if callable(src_suffix):
            self.src_suffix = src_suffix
        elif SCons.Util.is_String(src_suffix):
            self.src_suffix = _callable_adaptor([ str(src_suffix) ])
        else:
            self.src_suffix = _callable_adaptor(src_suffix)
            
        self.target_factory = target_factory or node_factory
        self.source_factory = source_factory or node_factory
        self.scanner = scanner

        self.emitter = emitter

    def get_name(self, env):
        """Attempts to get the name of the Builder.

        If the Builder's name attribute is None, then we will look at
        the BUILDERS variable of env, expecting it to be a dictionary
        containing this Builder, and we will return the key of the
        dictionary."""

        if self.name:
            return self.name
        try:
            index = env['BUILDERS'].values().index(self)
            return env['BUILDERS'].keys()[index]
        except (AttributeError, KeyError, ValueError):
            return str(self.__class__)

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def _create_nodes(self, env, args, target = None, source = None):
        """Create and return lists of target and source nodes.
        """
        def adjustixes(files, pre, suf):
            ret = []
            # FOR RELEASE 0.08:
            #if not SCons.Util.is_List(files):
            #    files = [files]
            files = SCons.Util.argmunge(files)

            for f in files:
                if SCons.Util.is_String(f):
                    if pre and f[:len(pre)] != pre:
                        path, fn = os.path.split(os.path.normpath(f))
                        f = os.path.join(path, pre + fn)
                    # Only append a suffix if the file does not have one.
		    if suf and not os.path.splitext(f)[1]:
		        if f[-len(suf):] != suf:
		            f = f + suf
		ret.append(f)
	    return ret

        pre = self.get_prefix(env, args)
        suf = self.get_suffix(env, args)
        src_suf = self.get_src_suffix(env, args)
        if self.emitter:
            # pass the targets and sources to the emitter as strings
            # rather than nodes since str(node) doesn't work 
            # properly from any directory other than the top directory,
            # and emitters are called "in" the SConscript directory:
            tlist = adjustixes(target, pre, suf)
            slist = adjustixes(source, None, src_suf)

            emit_args = { 'target' : tlist,
                          'source' : slist,
                          'env' : env }
            emit_args.update(args)
            target, source = apply(self.emitter, (), emit_args)

        tlist = SCons.Node.arg2nodes(adjustixes(target, pre, suf),
                                     self.target_factory)
        slist = SCons.Node.arg2nodes(adjustixes(source, None, src_suf),
                                     self.source_factory)

        return tlist, slist

    def __call__(self, env, target = None, source = None, **kw):
        tlist, slist = self._create_nodes(env, kw, target, source)

        if len(tlist) == 1:
            _init_nodes(self, env, kw, tlist, slist)
            tlist = tlist[0]
        else:
            _init_nodes(ListBuilder(self, env, tlist), env, kw, tlist, slist)

        return tlist


    def execute(self, **kw):
        """Execute a builder's action to create an output object.
        """
        return apply(self.action.execute, (), kw)

    def get_raw_contents(self, **kw):
        """Fetch the "contents" of the builder's action.
        """
        return apply(self.action.get_raw_contents, (), kw)

    def get_contents(self, **kw):
        """Fetch the "contents" of the builder's action
        (for signature calculation).
        """
        return apply(self.action.get_contents, (), kw)

    def src_suffixes(self, env, args):
        return map(lambda x, e=env: e.subst(_adjust_suffix(x)),
                   apply(self.src_suffix, (), args))

    def get_src_suffix(self, env, args):
        """Get the first src_suffix in the list of src_suffixes."""
        ret = self.src_suffixes(env, args)
        if not ret:
            return ''
        else:
            return ret[0]

    def get_suffix(self, env, args):
        return env.subst(_adjust_suffix(apply(self.suffix, (), args)))

    def get_prefix(self, env, args):
        return env.subst(apply(self.prefix, (), args))

    def targets(self, node):
        """Return the list of targets for this builder instance.

        For most normal builders, this is just the supplied node.
        """
        return [ node ]

class ListBuilder:
    """This is technically not a Builder object, but a wrapper
    around another Builder object.  This is designed to look
    like a Builder object, though, for purposes of building an
    array of targets from a single Action execution.
    """

    def __init__(self, builder, env, tlist):
        self.builder = builder
        self.tlist = tlist
        self.name = "ListBuilder(%s)"%builder.get_name(env)

    def get_name(self, env):
        return self.name

    def execute(self, **kw):
        if hasattr(self, 'status'):
            return self.status
        for t in self.tlist:
            # unlink all targets and make all directories
            # before building anything
            t.prepare()
        kw['target'] = self.tlist
        self.status = apply(self.builder.execute, (), kw)
        for t in self.tlist:
            if not t is kw['target']:
                t.build()
        return self.status

    def targets(self, node):
        """Return the list of targets for this builder instance.
        """
        return self.tlist

    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def __getattr__(self, name):
	return getattr(self.builder, name)

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
                        name = None,
                        action = None,
                        prefix = '',
                        suffix = '',
                        src_suffix = '',
                        node_factory = SCons.Node.FS.default_fs.File,
                        target_factory = None,
                        source_factory = None,
                        scanner=None,
                        emitter=None):
        BuilderBase.__init__(self, name, action, prefix, suffix, src_suffix,
                             node_factory, target_factory, source_factory,
                             scanner, emitter)
        if not SCons.Util.is_List(src_builder):
            src_builder = [ src_builder ]
        self.src_builder = src_builder
        self.sdict = {}

    def __call__(self, env, target = None, source = None, **kw):
        slist = SCons.Node.arg2nodes(source, self.source_factory)
        final_sources = []

        r=repr(env)
        try:
            sdict = self.sdict[r]
        except KeyError:
            sdict = {}
            self.sdict[r] = sdict
            for bld in self.src_builder:
                for suf in bld.src_suffixes(env, kw):
                    sdict[suf] = bld
                    
        for snode in slist:
            path, ext = os.path.splitext(snode.abspath)
            if sdict.has_key(ext):
                src_bld = sdict[ext]

                dictArgs = copy.copy(kw)
                dictArgs['target'] = [path]
                dictArgs['source'] = snode
                dictArgs['env'] = env
                tgt = apply(src_bld, (), dictArgs)
                if not SCons.Util.is_List(tgt):
                    tgt = [ tgt ]

                # Only supply the builder with sources it is capable
                # of building.
                tgt = filter(lambda x,
                             suf=self.src_suffixes(env, kw):
                             os.path.splitext(SCons.Util.to_String(x))[1] in \
                             suf, tgt)
                final_sources.extend(tgt)
            else:
                final_sources.append(snode)
        dictKwArgs = kw
        dictKwArgs['target'] = target
        dictKwArgs['source'] = final_sources
        return apply(BuilderBase.__call__,
                     (self, env), dictKwArgs)

    def src_suffixes(self, env, args):
        return BuilderBase.src_suffixes(self, env, args) + \
               reduce(lambda x, y: x + y,
                      map(lambda b, e=env, args=args: b.src_suffixes(e, args),
                          self.src_builder),
                      [])
