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
import string
import sys
import types
from Errors import UserError

import SCons.Node.FS
import SCons.Util

exitvalmap = {
    2 : 127,
    13 : 126,
}

if os.name == 'posix':

    def spawn(cmd, args, env):
        pid = os.fork()
        if not pid:
            # Child process.
            exitval = 127
            try:
                os.execvpe(cmd, args, env)
            except OSError, e:
                exitval = exitvalmap[e[0]]
                sys.stderr.write("scons: %s: %s\n" % (cmd, e[1]))
            os._exit(exitval)
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
		if not SCons.Util.is_List(exts):
		    exts = string.split(exts, os.pathsep)
		for e in exts:
		    f = cmd + e
		    if os.path.exists(f):
		        return f
	else:
	    path = env['PATH']
	    if not SCons.Util.is_List(path):
	        path = string.split(path, os.pathsep)
	    exts = env['PATHEXT']
	    if not SCons.Util.is_List(exts):
	        exts = string.split(exts, os.pathsep)
	    pairs = []
	    for dir in path:
	        for e in exts:
		    pairs.append((dir, e))
	    for dir, ext in pairs:
		f = os.path.join(dir, cmd)
	        if not ext is None:
		    f = f + ext
		if os.path.exists(f):
		    return f
	return cmd

    def spawn(cmd, args, env):
        try:
            try:
                ret = os.spawnvpe(os.P_WAIT, cmd, args, env)
            except AttributeError:
                cmd = pathsearch(cmd, env)
                ret = os.spawnve(os.P_WAIT, cmd, args, env)
        except OSError, e:
            ret = exitvalmap[e[0]]
            sys.stderr.write("scons: %s: %s\n" % (cmd, e[1]))
        return ret



def Builder(**kw):
    """A factory for builder objects."""
    if kw.has_key('action') and SCons.Util.is_Dict(kw['action']):
        return apply(CompositeBuilder, (), kw)
    elif kw.has_key('src_builder'):
        return apply(MultiStepBuilder, (), kw)
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
                        node_factory = SCons.Node.FS.default_fs.File,
                        scanner = None):
	self.name = name
	self.action = Action(action)

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

    def _init_nodes(self, env, tlist, slist):
        """Initialize lists of target and source nodes with all of
        the proper Builder information.
        """
	for t in tlist:
            t.cwd = SCons.Node.FS.default_fs.getcwd()	# XXX
	    t.builder_set(self)
	    t.env_set(env)
	    t.add_source(slist)
            if self.scanner:
                t.scanner_set(self.scanner.instance(env))

	for s in slist:
	    s.env_set(env, 1)
            scanner = env.get_scanner(os.path.splitext(s.name)[1])
            if scanner:
                s.scanner_set(scanner.instance(env))

	if len(tlist) == 1:
	    tlist = tlist[0]
	return tlist

    def __call__(self, env, target = None, source = None):
        tlist, slist = self._create_nodes(env, target, source)

        return self._init_nodes(env, tlist, slist)

    def execute(self, **kw):
	"""Execute a builder's action to create an output object.
	"""
	return apply(self.action.execute, (), kw)

    def get_contents(self, **kw):
        """Fetch the "contents" of the builder's action
        (for signature calculation).
        """
        return apply(self.action.get_contents, (), kw)

    def src_suffixes(self):
        if self.src_suffix != '':
            return [self.src_suffix]
        return []

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
        for snode in slist:
            path, ext = os.path.splitext(snode.abspath)
            if not src_suffix or ext != src_suffix:
                tgt = self.src_builder(env, target = [ path ],
                                     source=snode)
                if not SCons.Util.is_List(tgt):
                    final_sources.append(tgt)
                else:
                    final_sources.extend(tgt)
            else:
                final_sources.append(snode)
        return BuilderBase.__call__(self, env, target=target,
                                    source=final_sources)

    def src_suffixes(self):
        return BuilderBase.src_suffixes(self) + self.src_builder.src_suffixes()

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
        self.builder_dict = {}
        for suff, act in action.items():
             # Create subsidiary builders for every suffix in the
             # action dictionary.  If there's a src_builder that
             # matches the suffix, add that to the initializing
             # keywords so that a MultiStepBuilder will get created.
             kw = {'name' : name, 'action' : act, 'src_suffix' : suff}
             src_bld = filter(lambda x, s=suff: x.suffix == s, self.src_builder)
             if src_bld:
                 kw['src_builder'] = src_bld[0]
             self.builder_dict[suff] = apply(Builder, (), kw)

    def __call__(self, env, target = None, source = None):
        tlist, slist = BuilderBase._create_nodes(self, env,
                                                 target=target, source=source)

        # XXX These [bs]dict tables are invariant for each unique
        # CompositeBuilder + Environment pair, so we should cache them.
        bdict = {}
        sdict = {}
        for suffix, bld in self.builder_dict.items():
            bdict[env.subst(bld.src_suffix)] = bld
            sdict[suffix] = suffix
            for s in bld.src_suffixes():
                bdict[s] = bld
                sdict[s] = suffix

        for tnode in tlist:
            suflist = map(lambda x, s=sdict: s[os.path.splitext(x.path)[1]],
                          slist)
            last_suffix=''
            for suffix in suflist:
                if last_suffix and last_suffix != suffix:
                    raise UserError, "The builder for %s can only build source files of identical suffixes:  %s." % (tnode.path, str(map(lambda t: str(t.path), tnode.sources)))
                last_suffix = suffix
            if last_suffix:
                try:
                    bdict[last_suffix].__call__(env, target = tnode,
                                                source = slist)
                except KeyError:
                    raise UserError, "The builder for %s can not build files with suffix: %s" % (tnode.path, suffix)

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def src_suffixes(self):
        return reduce(lambda x, y: x + y,
                      map(lambda b: b.src_suffixes(),
                          self.builder_dict.values()))

print_actions = 1;
execute_actions = 1;

def Action(act):
    """A factory for action objects."""
    if callable(act):
	return FunctionAction(act)
    elif SCons.Util.is_String(act):
	return CommandAction(act)
    elif SCons.Util.is_List(act):
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

    def subst_dict(self, **kw):
        """Create a dictionary for substitution of construction
        variables.

        This translates the following special arguments:

            env    - the construction environment itself,
                     the values of which (CC, CCFLAGS, etc.)
                     are copied straight into the dictionary

            target - the target (object or array of objects),
                     used to generate the TARGET and TARGETS
                     construction variables

            source - the source (object or array of objects),
                     used to generate the SOURCES construction
                     variable

        Any other keyword arguments are copied into the
        dictionary."""

        dict = {}
        if kw.has_key('env'):
            dict.update(kw['env'])
            del kw['env']

        try:
            cwd = kw['dir']
        except:
            cwd = None
        else:
            del kw['dir']

        if kw.has_key('target'):
            t = kw['target']
            del kw['target']
            if not SCons.Util.is_List(t):
                t = [t]
            try:
                cwd = t[0].cwd
            except AttributeError:
                pass
            dict['TARGETS'] = SCons.Util.PathList(map(os.path.normpath, map(str, t)))
            if dict['TARGETS']:
                dict['TARGET'] = dict['TARGETS'][0]

        if kw.has_key('source'):
            s = kw['source']
            del kw['source']
            if not SCons.Util.is_List(s):
                s = [s]
            dict['SOURCES'] = SCons.Util.PathList(map(os.path.normpath, map(str, s)))

        dict.update(kw)

        # Autogenerate necessary construction variables.
        SCons.Util.autogenerate(dict, dir = cwd)

        return dict

class CommandAction(ActionBase):
    """Class for command-execution actions."""
    def __init__(self, string):
        self.command = string

    def execute(self, **kw):
        import SCons.Util
        dict = apply(self.subst_dict, (), kw)
        cmd_list = SCons.Util.scons_subst_list(self.command, dict, {})
        for cmd_line in cmd_list:
            if len(cmd_line):
                if print_actions:
                    self.show(string.join(cmd_line))
                if execute_actions:
                    try:
                        ENV = kw['env']['ENV']
                    except:
                        import SCons.Defaults
                        ENV = SCons.Defaults.ConstructionEnvironment['ENV']
                    ret = spawn(cmd_line[0], cmd_line, ENV)
                    if ret:
                        return ret
        return 0

    def get_contents(self, **kw):
        """Return the signature contents of this action's command line.

        For signature purposes, it doesn't matter what targets or
        sources we use, so long as we use the same ones every time
        so the signature stays the same.  We supply an array of two
        of each to allow for distinction between TARGET and TARGETS.
        """
        kw['target'] = ['__t1__', '__t2__']
        kw['source'] = ['__s1__', '__s2__']
        dict = apply(self.subst_dict, (), kw)
        return SCons.Util.scons_subst(self.command, dict, {})

class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
	self.function = function

    def execute(self, **kw):
	# if print_actions:
	# XXX:  WHAT SHOULD WE PRINT HERE?
	if execute_actions:
            if kw.has_key('target'):
                if SCons.Util.is_List(kw['target']):
                    kw['target'] = map(str, kw['target'])
                else:
                    kw['target'] = str(kw['target'])
            if kw.has_key('source'):
                kw['source'] = map(str, kw['source'])
            return apply(self.function, (), kw)

    def get_contents(self, **kw):
        """Return the signature contents of this callable action.

        By providing direct access to the code object of the
        function, Python makes this extremely easy.  Hooray!
        """
        #XXX DOES NOT ACCOUNT FOR CHANGES IN ENVIRONMENT VARIABLES
        #THE FUNCTION MAY USE
        try:
            # "self.function" is a function.
            code = self.function.func_code.co_code
        except:
            # "self.function" is a callable object.
            code = self.function.__call__.im_func.func_code.co_code
        return str(code)

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

    def get_contents(self, **kw):
        """Return the signature contents of this action list.

        Simple concatenation of the signatures of the elements.
        """

        return reduce(lambda x, y: x + str(y.get_contents()), self.list, "")
