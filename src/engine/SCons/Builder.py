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
from Errors import UserError

import SCons.Action
import SCons.Node.FS
import SCons.Util



def Builder(**kw):
    """A factory for builder objects."""
    
    if kw.has_key('generator'):
        if kw.has_key('action'):
            raise UserError, "You must not specify both an action and a generator."
        kw['action'] = SCons.Action.CommandGenerator(kw['generator'])
        del kw['generator']

    if kw.has_key('action') and SCons.Util.is_Dict(kw['action']):
        return apply(CompositeBuilder, (), kw)
    elif kw.has_key('src_builder'):
        return apply(MultiStepBuilder, (), kw)
    else:
        return apply(BuilderBase, (), kw)



def _init_nodes(builder, env, tlist, slist):
    """Initialize lists of target and source nodes with all of
    the proper Builder information.
    """
    for t in tlist:
        t.cwd = SCons.Node.FS.default_fs.getcwd()	# XXX
        t.builder_set(builder)
        t.env_set(env)
        t.add_source(slist)
        if builder.scanner:
            t.scanner_set(builder.scanner.instance(env))

    for s in slist:
        s.env_set(env, 1)
        scanner = env.get_scanner(os.path.splitext(s.name)[1])
        if scanner:
            s.scanner_set(scanner.instance(env))



class BuilderBase:
    """Base class for Builders, objects that create output
    nodes (files) from input nodes (files).
    """

    def __init__(self,	name = None,
			action = None,
			prefix = '',
			suffix = '',
			src_suffix = '',
                        node_factory = SCons.Node.FS.default_fs.File,
                        scanner = None):
        if name is None:
            raise UserError, "You must specify a name for the builder."
	self.name = name
	self.action = SCons.Action.Action(action)

	self.prefix = prefix
	self.suffix = suffix
	self.src_suffix = src_suffix
	self.node_factory = node_factory
        self.scanner = scanner
        if self.suffix and self.suffix[0] not in '.$':
	    self.suffix = '.' + self.suffix
        if self.src_suffix and self.src_suffix[0] not in '.$':
	    self.src_suffix = '.' + self.src_suffix

    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def _create_nodes(self, env, target = None, source = None):
        """Create and return lists of target and source nodes.
        """
	def adjustixes(files, pre, suf):
	    ret = []
            if SCons.Util.is_String(files):
                files = string.split(files)
            if not SCons.Util.is_List(files):
	        files = [files]
	    for f in files:
                if SCons.Util.is_String(f):
		    if pre and f[:len(pre)] != pre:
                        path, fn = os.path.split(os.path.normpath(f))
                        f = os.path.join(path, pre + fn)
		    if suf:
		        if f[-len(suf):] != suf:
		            f = f + suf
		ret.append(f)
	    return ret

        tlist = SCons.Util.scons_str2nodes(adjustixes(target,
                                                      env.subst(self.prefix),
                                                      env.subst(self.suffix)),
                                           self.node_factory)

        slist = SCons.Util.scons_str2nodes(adjustixes(source,
                                                      None,
                                                      env.subst(self.src_suffix)),
                                           self.node_factory)
        return tlist, slist

    def __call__(self, env, target = None, source = None):
        tlist, slist = self._create_nodes(env, target, source)

        if len(tlist) == 1:
            _init_nodes(self, env, tlist, slist)
            tlist = tlist[0]
        else:
            _init_nodes(ListBuilder(self, env, tlist), env, tlist, slist)

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

    def src_suffixes(self, env):
        if self.src_suffix != '':
            return [env.subst(self.src_suffix)]
        return []

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
        self.scanner = builder.scanner
        self.env = env
        self.tlist = tlist

    def execute(self, **kw):
        if hasattr(self, 'status'):
            return self.status
        for t in self.tlist:
            # unlink all targets and make all directories
            # before building anything
            t.prepare()
        kw['target'] = self.tlist[0]
        self.status = apply(self.builder.execute, (), kw)
        for t in self.tlist:
            if not t is kw['target']:
                t.build()
        return self.status

    def get_raw_contents(self, **kw):
        return apply(self.builder.get_raw_contents, (), kw)

    def get_contents(self, **kw):
        return apply(self.builder.get_contents, (), kw)

    def src_suffixes(self, env):
        return self.builder.src_suffixes(env)

    def targets(self, node):
        """Return the list of targets for this builder instance.
        """
        return self.tlist

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
                        scanner=None):
        BuilderBase.__init__(self, name, action, prefix, suffix, src_suffix,
                             node_factory, scanner)
        self.src_builder = src_builder

    def __call__(self, env, target = None, source = None):
        slist = SCons.Util.scons_str2nodes(source, self.node_factory)
        final_sources = []
        src_suffix = env.subst(self.src_suffix)
        sdict = {}
        for suff in self.src_builder.src_suffixes(env):
            sdict[suff] = None
        for snode in slist:
            path, ext = os.path.splitext(snode.abspath)
            if sdict.has_key(ext):
                tgt = self.src_builder(env, target = [ path ], source = snode)
                if not SCons.Util.is_List(tgt):
                    final_sources.append(tgt)
                else:
                    final_sources.extend(tgt)
            else:
                final_sources.append(snode)
        return BuilderBase.__call__(self, env, target=target,
                                    source=final_sources)

    def src_suffixes(self, env):
        return BuilderBase.src_suffixes(self, env) + \
               self.src_builder.src_suffixes(env)

class CompositeBuilder(BuilderBase):
    """This is a convenient Builder subclass that can build different
    files based on their suffixes.  For each target, this builder
    will examine the target's sources.  If they are all the same
    suffix, and that suffix is equal to one of the child builders'
    src_suffix, then that child builder will be used.  Otherwise,
    UserError is thrown."""
    def __init__(self,  name = None,
                        prefix='',
                        suffix='',
                        action = {},
                        src_builder = []):
        BuilderBase.__init__(self, name=name, prefix=prefix,
                             suffix=suffix)
        if src_builder and not SCons.Util.is_List(src_builder):
            src_builder = [src_builder]
        self.src_builder = src_builder
        self.action_dict = action
        self.sdict = {}
        self.sbuild = {}

    def __call__(self, env, target = None, source = None):
        tlist, slist = BuilderBase._create_nodes(self, env,
                                                 target=target, source=source)

        r = repr(env)
        if not self.sdict.has_key(r):
            self.sdict[r] = {}
            self.sbuild[r] = []
            for suff in self.src_suffixes(env):
                suff = env.subst(suff)
                self.sdict[r][suff] = suff
                self.sbuild[r].extend(filter(lambda x, e=env, s=suff:
                                                    e.subst(x.suffix) == s,
                                             self.src_builder))
            for sb in self.sbuild[r]:
                suff = env.subst(sb.suffix)
                for s in sb.src_suffixes(env):
                     self.sdict[r][env.subst(s)] = suff

        sufflist = map(lambda x, s=self.sdict[r]:
                              s[os.path.splitext(x.path)[1]],
                       slist)
        last_suffix = ''
        for suff in sufflist:
            if last_suffix and last_suffix != suff:
                raise UserError, "The builder for %s can only build source files of identical suffixes:  %s." % \
                      (tlist[0].path,
                       str(map(lambda t: str(t.path), tlist[0].sources)))
            last_suffix = suff

        if last_suffix:
            kw = {
                'name' : self.name,
                'action' : self.action_dict[last_suffix],
                'src_suffix' : last_suffix,
            }
            if self.sbuild[r]:
                sb = filter(lambda x, e=env, s=last_suffix:
                                   e.subst(x.suffix) == s,
                            self.sbuild[r])
                if sb:
                    kw['src_builder'] = sb[0]
            # XXX We should be able to cache this
            bld = apply(Builder, (), kw)
            for tnode in tlist:
                bld.__call__(env, target = tnode, source = slist)

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def src_suffixes(self, env):
        suffixes = map(lambda k, e=env: e.subst(k), self.action_dict.keys()) + \
                   reduce(lambda x, y: x + y,
                          map(lambda b, e=env: b.src_suffixes(e),
                              self.src_builder),
                          [])
        return suffixes
