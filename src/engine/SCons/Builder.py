"""SCons.Builder

XXX

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



import os
import os.path
import SCons.Node.FS
from SCons.Util import PathList, scons_str2nodes, scons_subst
import string
import types
from UserList import UserList
from UserDict import UserDict
from Errors import UserError

try:
    from UserString import UserString
except ImportError:
    class UserString:
        pass



if os.name == 'posix':

    def spawn(cmd, args, env):
        pid = os.fork()
        if not pid:
            # Child process.
            os.execvpe(cmd, args, env)
        else:
            # Parent process.
            pid, stat = os.waitpid(pid, 0)
            ret = stat >> 8
	    return ret

elif os.name == 'nt':

    def pathsearch(cmd, env):
	# In order to deal with the fact that 1.5.2 doesn't have
	# os.spawnvpe(), roll our own PATH search.
	if os.path.isabs(cmd):
	    if not os.path.exists(cmd):
	        exts = env['PATHEXT']
		if type(exts) != type([]):
		    exts = string.split(exts, os.pathsep)
		for e in exts:
		    f = cmd + e
		    if os.path.exists(f):
		        return f
	else:
	    path = env['PATH']
	    if type(path) != type([]):
	        path = string.split(path, os.pathsep)
	    exts = env['PATHEXT']
	    if type(exts) != type([]):
	        exts = string.split(exts, os.pathsep)
	    pairs = []
	    for dir in path:
	        for e in [None] + exts:
		    pairs.append(dir, e)
	    for dir, ext in pairs:
		f = os.path.join(dir, cmd)
	        if not ext is None:
		    f = f + ext
		if os.path.exists(f):
		    return f
	return cmd

    def spawn(cmd, args, env):
        try:
	    ret = os.spawnvpe(os.P_WAIT, cmd, args, env)
	except AttributeError:
	    cmd = pathsearch(cmd, env)
	    ret = os.spawnve(os.P_WAIT, cmd, args, env)
        return ret



def Builder(**kw):
    """A factory for builder objects."""
    if kw.has_key('src_builder'):
        return apply(MultiStepBuilder, (), kw)
    elif kw.has_key('action') and (type(kw['action']) is types.DictType or
                                   isinstance(kw['action'], UserDict)):
        action_dict = kw['action']
        builders = []
        for suffix, action in action_dict.items():
            bld_kw = kw.copy()
            bld_kw['action'] = action
            bld_kw['src_suffix'] = suffix
            builders.append(apply(BuilderBase, (), bld_kw))
        del kw['action']
        kw['builders'] = builders
        return apply(CompositeBuilder, (), kw)
    else:
        return apply(BuilderBase, (), kw)



class BuilderBase:
    """Base class for Builders, objects that create output
    nodes (files) from input nodes (files).
    """

    def __init__(self,	name = None,
			action = None,
			prefix = '',
			suffix = '',
			src_suffix = '',
			node_factory = SCons.Node.FS.default_fs.File):
	self.name = name
	self.action = Action(action)

	self.prefix = prefix
	self.suffix = suffix
	self.src_suffix = src_suffix
	self.node_factory = node_factory
        if self.suffix and self.suffix[0] not in '.$':
	    self.suffix = '.' + self.suffix
        if self.src_suffix and self.src_suffix[0] not in '.$':
	    self.src_suffix = '.' + self.src_suffix

    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def __call__(self, env, target = None, source = None):
	def adjustixes(files, pre, suf):
	    ret = []
	    if not type(files) is type([]):
	        files = [files]
	    for f in files:
		if type(f) == type(""):
		    if pre and f[:len(pre)] != pre:
		        f = pre + f
		    if suf:
		        if f[-len(suf):] != suf:
		            f = f + suf
		ret.append(f)
	    return ret

	tlist = scons_str2nodes(adjustixes(target,
                                           env.subst(self.prefix),
                                           env.subst(self.suffix)),
                                self.node_factory)
	slist = scons_str2nodes(adjustixes(source, None,
                                           env.subst(self.src_suffix)),
                                self.node_factory)
	for t in tlist:
	    t.builder_set(self)
	    t.env_set(env)
	    t.add_source(slist)

	if len(tlist) == 1:
	    tlist = tlist[0]
	return tlist

    def execute(self, **kw):
	"""Execute a builder's action to create an output object.
	"""
	return apply(self.action.execute, (), kw)

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
			node_factory = SCons.Node.FS.default_fs.File):
        BuilderBase.__init__(self, name, action, prefix, suffix, src_suffix,
                             node_factory)
        self.src_builder = src_builder

    def __call__(self, env, target = None, source = None):
        slist = scons_str2nodes(source, self.node_factory)
        final_sources = []
        src_suffix = env.subst(self.src_suffix)
        for snode in slist:
            path, ext = os.path.splitext(snode.path)
            if not src_suffix or ext != src_suffix:
                tgt = self.src_builder(env, target = [ path ],
                                     source=snode)
                if not type(tgt) is types.ListType:
                    final_sources.append(tgt)
                else:
                    final_sources.extend(tgt)
            else:
                final_sources.append(snode)
        return BuilderBase.__call__(self, env, target=target,
                                    source=final_sources)

class CompositeBuilder(BuilderBase):
    """This is a convenient Builder subclass that can build different
    files based on their suffixes.  For each target, this builder
    will examine the target's sources.  If they are all the same
    suffix, and that suffix is equal to one of the child builders'
    src_suffix, then that child builder will be used.  Otherwise,
    UserError is thrown.

    Child builders are supplied via the builders arg to the
    constructor.  Each must have its src_suffix set."""
    def __init__(self,  name = None,
                        prefix='',
                        suffix='',
                        builders=[]):
        BuilderBase.__init__(self, name=name, prefix=prefix,
                             suffix=suffix)
        self.builder_dict = {}
        for bld in builders:
            if not bld.src_suffix:
                raise InternalError, "All builders supplied to CompositeBuilder class must have a src_suffix."
            self.builder_dict[bld.src_suffix] = bld

    def __call__(self, env, target = None, source = None):
        ret = BuilderBase.__call__(self, env, target=target, source=source)

        builder_dict = {}
        for suffix, bld in self.builder_dict.items():
            builder_dict[env.subst(bld.src_suffix)] = bld

        if type(ret) is types.ListType:
            tlist = ret
        else:
            tlist = [ ret ]
        for tnode in tlist:
            suflist = map(lambda x: os.path.splitext(x.path)[1],
                          tnode.sources)
            last_suffix=''
            for suffix in suflist:
                if last_suffix and last_suffix != suffix:
                    raise UserError, "The builder for %s is only capable of building source files of identical suffixes." % tnode.path
                last_suffix = suffix
            if last_suffix:
                try:
                    tnode.builder_set(builder_dict[last_suffix])
                except KeyError:
                    raise UserError, "Builder not capable of building files with suffix: %s" % suffix
        return ret

print_actions = 1;
execute_actions = 1;

def Action(act):
    """A factory for action objects."""
    if callable(act):
	return FunctionAction(act)
    elif type(act) == types.StringType or isinstance(act, UserString):
	return CommandAction(act)
    elif type(act) == types.ListType or isinstance(act, UserList):
	return ListAction(act)
    else:
	return None
    
class ActionBase:
    """Base class for actions that create output objects.
    
    We currently expect Actions will only be accessible through
    Builder objects, so they don't yet merit their own module."""
    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def show(self, string):
	print string

class CommandAction(ActionBase):
    """Class for command-execution actions."""
    def __init__(self, string):
	self.command = string

    def execute(self, **kw):
	loc = {}
	if kw.has_key('target'):
	    t = kw['target']
	    if type(t) is type(""):
	        t = [t]
	    loc['targets'] = PathList(map(os.path.normpath, t))
	    loc['target'] = loc['targets'][0]
	if kw.has_key('source'):
	    s = kw['source']
	    if type(s) is type(""):
	        s = [s]
            loc['sources'] = PathList(map(os.path.normpath, s))

	glob = {}
	if kw.has_key('env'):
	    glob = kw['env']

	cmd_str = scons_subst(self.command, loc, glob)
        for cmd in string.split(cmd_str, '\n'):
            if print_actions:
                self.show(cmd)
            if execute_actions:
                args = string.split(cmd)
                try:
                    ENV = glob['ENV']
                except:
                    import SCons.Defaults
                    ENV = SCons.Defaults.ConstructionEnvironment['ENV']
                ret = spawn(args[0], args, ENV)
                if ret:
                    #XXX This doesn't account for ignoring errors (-i)
                    return ret
        return 0



class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
	self.function = function

    def execute(self, **kw):
	# if print_actions:
	# XXX:  WHAT SHOULD WE PRINT HERE?
	if execute_actions:
	    return self.function(kw)

class ListAction(ActionBase):
    """Class for lists of other actions."""
    def __init__(self, list):
	self.list = map(lambda x: Action(x), list)

    def execute(self, **kw):
	for l in self.list:
	    r = apply(l.execute, (), kw)
	    if r != 0:
		return r
	return 0
