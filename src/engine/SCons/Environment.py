"""SCons.Environment

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


import copy
import os
import os.path
import re
import shutil
import string
import sys
import types
from UserDict import UserDict

import SCons.Action
import SCons.Builder
import SCons.Defaults
import SCons.Errors
import SCons.Node
import SCons.Node.FS
import SCons.Platform
import SCons.Tool
import SCons.Util
import SCons.Warnings

def installString(target, source):
    return 'Install file: "%s" as "%s"' % (source[0], target[0])

installAction = SCons.Action.Action(SCons.Node.FS.LinkFunc, installString)

InstallBuilder = SCons.Builder.Builder(name='Install', action=installAction)

def our_deepcopy(x):
   """deepcopy lists and dictionaries, and just copy the reference
   for everything else."""
   if SCons.Util.is_Dict(x):
       copy = {}
       for key in x.keys():
           copy[key] = our_deepcopy(x[key])
   elif SCons.Util.is_List(x):
       copy = map(our_deepcopy, x)
   else:
       copy = x
   return copy

class BuilderDict(UserDict):
    """This is a dictionary-like class used by Environment
    to hold Builders.  We need to do this, because every time
    someone changes the Builders in the Environment's BUILDERS
    dictionary, we need to update the Environment's attributes."""
    def setEnvironment(self, env):
        self.env = env
        
    def __setitem__(self, item, val):
        UserDict.__setitem__(self, item, val)
        try:
            self.env.Replace() # re-compute Builders
        except AttributeError:
            # Have to catch this because sometimes
            # __setitem__ gets called out of __init__, when
            # we don't have an env attribute yet, nor do
            # we want one!
            pass

    def __delitem__(self, item):
        UserDict.__delitem__(self, item)
        self.env.Replace()

_rm = re.compile(r'\$[()]')

class Environment:
    """Base class for construction Environments.  These are
    the primary objects used to communicate dependency and
    construction information to the build engine.

    Keyword arguments supplied when the construction Environment
    is created are construction variables used to initialize the
    Environment.
    """

    def __init__(self,
                 platform=SCons.Platform.Platform(),
                 tools=None,
                 options=None,
                 **kw):
        self.fs = SCons.Node.FS.default_fs
        self._dict = our_deepcopy(SCons.Defaults.ConstructionEnvironment)

        if SCons.Util.is_String(platform):
            platform = SCons.Platform.Platform(platform)
        platform(self)

        # Apply the passed-in variables before calling the tools,
        # because they may use some of them:
        apply(self.Replace, (), kw)
        
        # Update the environment with the customizable options
        # before calling the tools, since they may use some of the options: 
        if options:
            options.Update(self)

        if tools is None:
            tools = ['default']
        for tool in tools:
            if SCons.Util.is_String(tool):
                tool = SCons.Tool.Tool(tool)
            tool(self, platform)

        # Reapply the passed in variables after calling the tools,
        # since they should overide anything set by the tools:
        apply(self.Replace, (), kw)

        # Update the environment with the customizable options
        # after calling the tools, since they should override anything
        # set by the tools:
        if options:
            options.Update(self)

    def __cmp__(self, other):
	return cmp(self._dict, other._dict)

    def Builders(self):
	pass	# XXX

    def Copy(self, **kw):
	"""Return a copy of a construction Environment.  The
	copy is like a Python "deep copy"--that is, independent
	copies are made recursively of each objects--except that
	a reference is copied when an object is not deep-copyable
	(like a function).  There are no references to any mutable
	objects in the original Environment.
	"""
        clone = copy.copy(self)
        clone._dict = our_deepcopy(self._dict)
        apply(clone.Replace, (), kw)
	return clone

    def Scanners(self):
	pass	# XXX

    def	Update(self, **kw):
        """A deprecated synonym for Replace().
        """
        apply(self.Replace, (), kw)

    def __updateBuildersAndScanners(self):
        """Update attributes for builders and scanners.

        Have to be careful in this function...we can't
        call functions like __setitem__() or Replace(), or
        we will have infinite recursion."""
        
        if self._dict.has_key('SCANNERS') and \
           not SCons.Util.is_List(self._dict['SCANNERS']):
            self._dict['SCANNERS'] = [self._dict['SCANNERS']]

        class BuilderWrapper:
            """Wrapper class that allows an environment to
            be associated with a Builder at instantiation.
            """
            def __init__(self, env, builder):
                self.env = env
                self.builder = builder

            def __call__(self, *args, **kw):
                return apply(self.builder, (self.env,) + args, kw)

            # This allows a Builder to be executed directly
            # through the Environment to which it's attached.
            # In practice, we shouldn't need this, because
            # builders actually get executed through a Node.
            # But we do have a unit test for this, and can't
            # yet rule out that it would be useful in the
            # future, so leave it for now.
            def execute(self, **kw):
                kw['env'] = self.env
                apply(self.builder.execute, (), kw)

        if self._dict.has_key('BUILDERS'):
            if SCons.Util.is_Dict(self._dict['BUILDERS']):
                bd = self._dict['BUILDERS']
                if not isinstance(bd, BuilderDict):
                    # Convert it to a BuilderDict.  This class
                    # Updates our builder attributes every time
                    # someone changes it.
                    bd = BuilderDict(bd)
                    bd.setEnvironment(self)
                    self._dict['BUILDERS'] = bd
                for name, builder in bd.items():
                    setattr(self, name, BuilderWrapper(self, builder))
            else:
                raise SCons.Errors.UserError, "The use of the BUILDERS Environment variable as a list or Builder instance is deprecated.  BUILDERS should be a dictionary of name->Builder instead."
        for s in self._dict['SCANNERS']:
            setattr(self, s.name, s)
        

    def Replace(self, **kw):
        """Replace existing construction variables in an Environment
        with new construction variables and/or values.
        """
        self._dict.update(our_deepcopy(kw))
        self.__updateBuildersAndScanners()

    def Append(self, **kw):
        """Append values to existing construction variables
        in an Environment.
        """
        kw = our_deepcopy(kw)
        for key in kw.keys():
            if not self._dict.has_key(key):
                self._dict[key] = kw[key]
            elif SCons.Util.is_List(self._dict[key]) and not \
                 SCons.Util.is_List(kw[key]):
                self._dict[key] = self._dict[key] + [ kw[key] ]
            elif SCons.Util.is_List(kw[key]) and not \
                 SCons.Util.is_List(self._dict[key]):
                self._dict[key] = [ self._dict[key] ] + kw[key]
            else:
                self._dict[key] = self._dict[key] + kw[key]
        self.__updateBuildersAndScanners()

    def Prepend(self, **kw):
        """Prepend values to existing construction variables
        in an Environment.
        """
        kw = our_deepcopy(kw)
        for key in kw.keys():
            if not self._dict.has_key(key):
                self._dict[key] = kw[key]
            elif SCons.Util.is_List(self._dict[key]) and not \
                 SCons.Util.is_List(kw[key]):
                self._dict[key] = [ kw[key] ] + self._dict[key]
            elif SCons.Util.is_List(kw[key]) and not \
                 SCons.Util.is_List(self._dict[key]):
                self._dict[key] = kw[key] + [ self._dict[key] ]
            else:
                self._dict[key] = kw[key] + self._dict[key]
        self.__updateBuildersAndScanners()

    def	Depends(self, target, dependency):
	"""Explicity specify that 'target's depend on 'dependency'."""
        tlist = SCons.Node.arg2nodes(target, self.fs.File)
        dlist = SCons.Node.arg2nodes(dependency, self.fs.File)
	for t in tlist:
	    t.add_dependency(dlist)

	if len(tlist) == 1:
	    tlist = tlist[0]
	return tlist

    def Ignore(self, target, dependency):
        """Ignore a dependency."""
        tlist = SCons.Node.arg2nodes(target, self.fs.File)
        dlist = SCons.Node.arg2nodes(dependency, self.fs.File)
        for t in tlist:
            t.add_ignore(dlist)

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def Precious(self, *targets):
        tlist = []
        for t in targets:
            tlist.extend(SCons.Node.arg2nodes(t, self.fs.File))

        for t in tlist:
            t.set_precious()

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def Dictionary(self, *args):
	if not args:
	    return self._dict
	dlist = map(lambda x, s=self: s._dict[x], args)
	if len(dlist) == 1:
	    dlist = dlist[0]
	return dlist

    def __setitem__(self, key, value):
        self._dict[key] = value
        self.__updateBuildersAndScanners()

    def __getitem__(self, key):
        return self._dict[key]

    def __delitem__(self, key):
        del self._dict[key]

    def has_key(self, key):
        return self._dict.has_key(key)

    def Command(self, target, source, action):
        """Builds the supplied target files from the supplied
        source files using the supplied action.  Action may
        be any type that the Builder constructor will accept
        for an action."""
        bld = SCons.Builder.Builder(action=action)
        return bld(self, target, source)

    def Install(self, dir, source):
        """Install specified files in the given directory."""
        sources = SCons.Node.arg2nodes(source, self.fs.File)
        dnodes = SCons.Node.arg2nodes(dir, self.fs.Dir)
        tgt = []
        for dnode in dnodes:
            for src in sources:
                target = SCons.Node.FS.default_fs.File(src.name, dnode)
                tgt.append(InstallBuilder(self, target, src))
        if len(tgt) == 1:
            tgt = tgt[0]
        return tgt

    def InstallAs(self, target, source):
        """Install sources as targets."""
        sources = SCons.Node.arg2nodes(source, self.fs.File)
        targets = SCons.Node.arg2nodes(target, self.fs.File)
        ret = []
        for src, tgt in map(lambda x, y: (x, y), sources, targets):
            ret.append(InstallBuilder(self, tgt, src))
        if len(ret) == 1:
            ret = ret[0]
        return ret

    def SideEffect(self, side_effect, target):
        """Tell scons that side_effects are built as side 
        effects of building targets."""
        side_effects = SCons.Node.arg2nodes(side_effect, self.fs.File)
        targets = SCons.Node.arg2nodes(target, self.fs.File)

        for side_effect in side_effects:
            # A builder of 1 means the node is supposed to appear
            # buildable without actually having a builder, so we allow
            # it to be a side effect as well.
            if side_effect.has_builder() and side_effect.builder != 1:
                raise SCons.Errors.UserError, "Multiple ways to build the same target were specified for: %s" % str(side_effect)
            side_effect.add_source(targets)
            side_effect.side_effect = 1
            self.Precious(side_effect)
            for target in targets:
                target.side_effects.append(side_effect)
        if len(side_effects) == 1:
            return side_effects[0]
        else:
            return side_effects

    def subst(self, string, raw=0):
	"""Recursively interpolates construction variables from the
	Environment into the specified string, returning the expanded
	result.  Construction variables are specified by a $ prefix
	in the string and begin with an initial underscore or
	alphabetic character followed by any number of underscores
	or alphanumeric characters.  The construction variable names
	may be surrounded by curly braces to separate the name from
	trailing characters.
	"""
        if raw:
            regex_remove = None
        else:
            regex_remove = _rm
        return SCons.Util.scons_subst(string, self._dict, {}, regex_remove)
    
    def subst_list(self, string, raw=0):
        """Calls through to SCons.Util.scons_subst_list().  See
        the documentation for that function."""
        if raw:
            regex_remove = None
        else:
            regex_remove = _rm
        return SCons.Util.scons_subst_list(string, self._dict, {}, regex_remove)

    def get_scanner(self, skey):
        """Find the appropriate scanner given a key (usually a file suffix).
        Does a linear search. Could be sped up by creating a dictionary if
        this proves too slow.
        """
        if self._dict['SCANNERS']:
            for scanner in self._dict['SCANNERS']:
                if skey in scanner.skeys:
                    return scanner
        return None

    def get_builder(self, name):
        """Fetch the builder with the specified name from the environment.
        """
        try:
            return self._dict['BUILDERS'][name]
        except KeyError:
            return None

    def Detect(self, progs):
        """Return the first available program in progs.
        """
        if not SCons.Util.is_List(progs):
            progs = [ progs ]
        for prog in progs:
            path = self.WhereIs(prog)
            if path: return prog
        return None

    def WhereIs(self, prog):
        """Find prog in the path.  
        """
        path = None
        pathext = None
        if self.has_key('ENV'):
            if self['ENV'].has_key('PATH'):
                path = self['ENV']['PATH']
            if self['ENV'].has_key('PATHEXT'):
                pathext = self['ENV']['PATHEXT']
        path = SCons.Util.WhereIs(prog, path, pathext)
        if path: return path
        return None

    def Override(self, overrides):
        """
        Produce a modified environment whose variables
        are overriden by the overrides dictionaries.

        overrides - a dictionary that will override
        the variables of this environment.

        This function is much more efficient than Copy()
        or creating a new Environment because it doesn't do
        a deep copy of the dictionary, and doesn't do a copy
        at all if there are no overrides.
        """

        if overrides:
            env = copy.copy(self)
            env._dict = copy.copy(self._dict)
            env._dict.update(overrides)
            return env
        else:
            return self

    def get(self, key, default=None):
        "Emulates the get() method of dictionaries."""
        return self._dict.get(key, default)

    def items(self):
        "Emulates the items() method of dictionaries."""
        return self._dict.items()

    def FindIxes(self, paths, prefix, suffix):
        """
        Search a list of paths for something that matches the prefix and suffix.

        paths - the list of paths or nodes.
        prefix - construction variable for the prefix.
        suffix - construction variable for the suffix.
        """

        suffix = self.subst('$%s'%suffix)
        prefix = self.subst('$%s'%prefix)

        for path in paths:
            dir,name = os.path.split(str(path))
            if name[:len(prefix)] == prefix and name[-len(suffix):] == suffix: 
                return path

    def ReplaceIxes(self, path, old_prefix, old_suffix, new_prefix, new_suffix):
        """
        Replace old_prefix with new_prefix and old_suffix with new_suffix.

        env - Environment used to interpolate variables.
        path - the path that will be modified.
        old_prefix - construction variable for the old prefix.
        old_suffix - construction variable for the old suffix.
        new_prefix - construction variable for the new prefix.
        new_suffix - construction variable for the new suffix.
        """
        old_prefix = self.subst('$%s'%old_prefix)
        old_suffix = self.subst('$%s'%old_suffix)

        new_prefix = self.subst('$%s'%new_prefix)
        new_suffix = self.subst('$%s'%new_suffix)

        dir,name = os.path.split(str(path))
        if name[:len(old_prefix)] == old_prefix:
            name = name[len(old_prefix):]
        if name[-len(old_suffix):] == old_suffix:
            name = name[:-len(old_suffix)]
        return os.path.join(dir, new_prefix+name+new_suffix)
    
