"""SCons.Environment

Base class for construction Environments.  These are
the primary objects used to communicate dependency and
construction information to the build engine.

Keyword arguments supplied when the construction Environment
is created are construction variables used to initialize the
Environment 
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
import os
import os.path
import string
import re
import shutil
from UserDict import UserDict

import SCons.Action
import SCons.Builder
from SCons.Debug import logInstanceCreation
import SCons.Defaults
import SCons.Errors
import SCons.Node
import SCons.Node.Alias
import SCons.Node.FS
import SCons.Node.Python
import SCons.Platform
import SCons.Sig
import SCons.Sig.MD5
import SCons.Sig.TimeStamp
import SCons.Tool
import SCons.Util
import SCons.Warnings

class _Null:
    pass

_null = _Null

CleanTargets = {}
CalculatorArgs = {}

# Pull UserError into the global name space for the benefit of
# Environment().SourceSignatures(), which has some import statements
# which seem to mess up its ability to reference SCons directly.
UserError = SCons.Errors.UserError

def installFunc(target, source, env):
    """Install a source file into a target using the function specified
    as the INSTALL construction variable."""
    try:
        install = env['INSTALL']
    except KeyError:
        raise SCons.Errors.UserError('Missing INSTALL construction variable.')
    return install(target[0].path, source[0].path, env)

def installString(target, source, env):
    return 'Install file: "%s" as "%s"' % (source[0], target[0])

installAction = SCons.Action.Action(installFunc, installString)

InstallBuilder = SCons.Builder.Builder(action=installAction)

def alias_builder(env, target, source):
    pass

AliasBuilder = SCons.Builder.Builder(action = alias_builder,
                                     target_factory = SCons.Node.Alias.default_ans.Alias,
                                     source_factory = SCons.Node.FS.default_fs.Entry,
                                     multi = 1)

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

def apply_tools(env, tools, toolpath):
    if tools:
        for tool in tools:
            if SCons.Util.is_String(tool):
                env.Tool(tool, toolpath)
            else:
                tool(env)

class BuilderWrapper:
    """Wrapper class that associates an environment with a Builder at
    instantiation."""
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

class BuilderDict(UserDict):
    """This is a dictionary-like class used by an Environment to hold
    the Builders.  We need to do this because every time someone changes
    the Builders in the Environment's BUILDERS dictionary, we must
    update the Environment's attributes."""
    def __init__(self, dict, env):
        # Set self.env before calling the superclass initialization,
        # because it will end up calling our other methods, which will
        # need to point the values in this dictionary to self.env.
        self.env = env
        UserDict.__init__(self, dict)

    def __setitem__(self, item, val):
        UserDict.__setitem__(self, item, val)
        try:
            self.setenvattr(item, val)
        except AttributeError:
            # Have to catch this because sometimes __setitem__ gets
            # called out of __init__, when we don't have an env
            # attribute yet, nor do we want one!
            pass

    def setenvattr(self, item, val):
        """Set the corresponding environment attribute for this Builder.

        If the value is already a BuilderWrapper, we pull the builder
        out of it and make another one, so that making a copy of an
        existing BuilderDict is guaranteed separate wrappers for each
        Builder + Environment pair."""
        try:
            builder = val.builder
        except AttributeError:
            builder = val
        setattr(self.env, item, BuilderWrapper(self.env, builder))

    def __delitem__(self, item):
        UserDict.__delitem__(self, item)
        delattr(self.env, item)

    def update(self, dict):
        for i, v in dict.items():
            self.__setitem__(i, v)

class Base:
    """Base class for construction Environments.  These are
    the primary objects used to communicate dependency and
    construction information to the build engine.

    Keyword arguments supplied when the construction Environment
    is created are construction variables used to initialize the
    Environment.
    """

    #######################################################################
    # This is THE class for interacting with the SCons build engine,
    # and it contains a lot of stuff, so we're going to try to keep this
    # a little organized by grouping the methods.
    #######################################################################

    #######################################################################
    # Methods that make an Environment act like a dictionary.  These have
    # the expected standard names for Python mapping objects.  Note that
    # we don't actually make an Environment a subclass of UserDict for
    # performance reasons.  Note also that we only supply methods for
    # dictionary functionality that we actually need and use.
    #######################################################################

    def __init__(self,
                 platform=None,
                 tools=None,
                 toolpath=[],
                 options=None,
                 **kw):
        if __debug__: logInstanceCreation(self)
        self.fs = SCons.Node.FS.default_fs
        self.ans = SCons.Node.Alias.default_ans
        self.lookup_list = SCons.Node.arg2nodes_lookups
        self._dict = our_deepcopy(SCons.Defaults.ConstructionEnvironment)

        self._dict['__env__'] = self
        self._dict['BUILDERS'] = BuilderDict(self._dict['BUILDERS'], self)

        if platform is None:
            platform = self._dict.get('PLATFORM', None)
            if platform is None:
                platform = SCons.Platform.Platform()
        if SCons.Util.is_String(platform):
            platform = SCons.Platform.Platform(platform)
        self._dict['PLATFORM'] = str(platform)
        platform(self)

        # Apply the passed-in variables before calling the tools,
        # because they may use some of them:
        apply(self.Replace, (), kw)
        
        # Update the environment with the customizable options
        # before calling the tools, since they may use some of the options: 
        if options:
            options.Update(self)

        if tools is None:
            tools = self._dict.get('TOOLS', None)
            if tools is None:
                tools = ['default']
        apply_tools(self, tools, toolpath)

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

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        if key in ['TARGET', 'TARGETS', 'SOURCE', 'SOURCES']:
            SCons.Warnings.warn(SCons.Warnings.ReservedVariableWarning,
                                "Ignoring attempt to set reserved variable `%s'" % key)
        elif key == 'BUILDERS':
            try:
                bd = self._dict[key]
                for k in bd.keys():
                    del bd[k]
            except KeyError:
                self._dict[key] = BuilderDict(kwbd, self)
            self._dict[key].update(value)
        else:
            if not SCons.Util.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def items(self):
        "Emulates the items() method of dictionaries."""
        return self._dict.items()

    def has_key(self, key):
        return self._dict.has_key(key)

    def get(self, key, default=None):
        "Emulates the get() method of dictionaries."""
        return self._dict.get(key, default)

    #######################################################################
    # Utility methods that are primarily for internal use by SCons.
    # These begin with lower-case letters.  Note that the subst() method
    # is actually already out of the closet and used by people.
    #######################################################################

    def arg2nodes(self, args, node_factory=_null, lookup_list=_null):
        if node_factory is _null:
            node_factory = self.fs.File
        if lookup_list is _null:
            lookup_list = self.lookup_list

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
                    if SCons.Util.is_String(n):
                        n = self.subst(n, raw=1)
                        if node_factory:
                            n = node_factory(n)
                    nodes.append(n)
                elif node_factory:
                    v = self.subst(v, raw=1)
                    nodes.append(node_factory(v))
            else:
                nodes.append(v)
    
        return nodes

    def get_calculator(self):
        try:
            return self._calculator
        except AttributeError:
            try:
                module = self._calc_module
                c = apply(SCons.Sig.Calculator, (module,), CalculatorArgs)
            except AttributeError:
                # Note that we're calling get_calculator() here, so the
                # DefaultEnvironment() must have a _calc_module attribute
                # to avoid infinite recursion.
                c = SCons.Defaults.DefaultEnvironment().get_calculator()
            self._calculator = c
            return c

    def get_builder(self, name):
        """Fetch the builder with the specified name from the environment.
        """
        try:
            return self._dict['BUILDERS'][name]
        except KeyError:
            return None

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

    def subst(self, string, raw=0, target=None, source=None, dict=None, conv=None):
        """Recursively interpolates construction variables from the
        Environment into the specified string, returning the expanded
        result.  Construction variables are specified by a $ prefix
        in the string and begin with an initial underscore or
        alphabetic character followed by any number of underscores
        or alphanumeric characters.  The construction variable names
        may be surrounded by curly braces to separate the name from
        trailing characters.
        """
        return SCons.Util.scons_subst(string, self, raw, target, source, dict, conv)

    def subst_kw(self, kw, raw=0, target=None, source=None, dict=None):
        nkw = {}
        for k, v in kw.items():
            k = self.subst(k, raw, target, source, dict)
            if SCons.Util.is_String(v):
                v = self.subst(v, raw, target, source, dict)
            nkw[k] = v
        return nkw

    def subst_list(self, string, raw=0, target=None, source=None, dict=None, conv=None):
        """Calls through to SCons.Util.scons_subst_list().  See
        the documentation for that function."""
        return SCons.Util.scons_subst_list(string, self, raw, target, source, dict, conv)


    def subst_path(self, path):
        """Substitute a path list, turning EntryProxies into Nodes
        and leaving Nodes (and other objects) as-is."""

        if not SCons.Util.is_List(path):
            path = [path]

        def s(obj):
            """This is the "string conversion" routine that we have our
            substitutions use to return Nodes, not strings.  This relies
            on the fact that an EntryProxy object has a get() method that
            returns the underlying Node that it wraps, which is a bit of
            architectural dependence that we might need to break or modify
            in the future in response to additional requirements."""
            try:
                get = obj.get
            except AttributeError:
                pass
            else:
                obj = get()
            return obj

        r = []
        for p in path:
            if SCons.Util.is_String(p):
                p = self.subst(p, conv=s)
                if SCons.Util.is_List(p):
                    p = p[0]
            else:
                p = s(p)
            r.append(p)
        return r

    def _update(self, dict):
        """Update an environment's values directly, bypassing the normal
        checks that occur when users try to set items.
        """
        self._dict.update(dict)

    def use_build_signature(self):
        try:
            return self._build_signature
        except AttributeError:
            b = SCons.Defaults.DefaultEnvironment()._build_signature
            self._build_signature = b
            return b

    #######################################################################
    # Public methods for manipulating an Environment.  These begin with
    # upper-case letters.  The essential characteristic of methods in
    # this section is that they do *not* have corresponding same-named
    # global functions.  For example, a stand-alone Append() function
    # makes no sense, because Append() is all about appending values to
    # an Environment's construction variables.
    #######################################################################

    def Append(self, **kw):
        """Append values to existing construction variables
        in an Environment.
        """
        kw = our_deepcopy(kw)
        for key, val in kw.items():
            try:
                orig = self._dict[key]
            except KeyError:
                # No existing variable in the environment, so just set
                # it to the new value.
                self._dict[key] = val
                continue

            try:
                # Most straightforward:  just try to add them together.
                # This will work in most cases, when the original and
                # new values are of compatible types.
                self._dict[key] = orig + val
                continue
            except TypeError:
                pass

            try:
                # Try to update a dictionary value with another.
                # If orig isn't a dictionary, it won't have an
                # update() method; if val isn't a dictionary, it
                # won't have a keys() method.  Either way, it's
                # an AttributeError.
                orig.update(val)
                continue
            except AttributeError:
                pass

            try:
                # Check if the original is a list.
                add_to_orig = orig.append
            except AttributeError:
                pass
            else:
                # The original is a list, so append the new value to it
                # (if there's a value to append).
                if val:
                    add_to_orig(val)
                continue

            # The original isn't a list, but the new value is (by process
            # of elimination), so insert the original in the new value
            # (if there's one to insert) and replace the variable with it.
            if orig:
                val.insert(0, orig)
            self._dict[key] = val

    def AppendENVPath(self, name, newpath, envname = 'ENV', sep = os.pathsep):
        """Append path elements to the path 'name' in the 'ENV'
        dictionary for this environment.  Will only add any particular
        path once, and will normpath and normcase all paths to help
        assure this.  This can also handle the case where the env
        variable is a list instead of a string.
        """

        orig = ''
        if self._dict.has_key(envname) and self._dict[envname].has_key(name):
            orig = self._dict[envname][name]

        nv = SCons.Util.AppendPath(orig, newpath, sep)
            
        if not self._dict.has_key(envname):
            self._dict[envname] = {}

        self._dict[envname][name] = nv

    def AppendUnique(self, **kw):
        """Append values to existing construction variables
        in an Environment, if they're not already there.
        """
        kw = our_deepcopy(kw)
        for key, val in kw.items():
            if not self._dict.has_key(key):
                self._dict[key] = val
            elif SCons.Util.is_Dict(self._dict[key]) and \
                 SCons.Util.is_Dict(val):
                self._dict[key].update(val)
            elif SCons.Util.is_List(val):
                dk = self._dict[key]
                if not SCons.Util.is_List(dk):
                    dk = [dk]
                val = filter(lambda x, dk=dk: x not in dk, val)
                self._dict[key] = dk + val
            else:
                dk = self._dict[key]
                if SCons.Util.is_List(dk):
                    if not val in dk:
                        self._dict[key] = dk + val
                else:
                    self._dict[key] = self._dict[key] + val

    def Copy(self, tools=None, toolpath=[], **kw):
        """Return a copy of a construction Environment.  The
        copy is like a Python "deep copy"--that is, independent
        copies are made recursively of each objects--except that
        a reference is copied when an object is not deep-copyable
        (like a function).  There are no references to any mutable
        objects in the original Environment.
        """
        clone = copy.copy(self)
        clone._dict = our_deepcopy(self._dict)
        clone['__env__'] = clone
        try:
            cbd = clone._dict['BUILDERS']
            clone._dict['BUILDERS'] = BuilderDict(cbd, clone)
        except KeyError:
            pass
        
        apply_tools(clone, tools, toolpath)

        # Apply passed-in variables after the new tools.
        new = {}
        for key, value in kw.items():
            new[key] = SCons.Util.scons_subst_once(value, self, key)
        apply(clone.Replace, (), new)
        return clone

    def Detect(self, progs):
        """Return the first available program in progs.
        """
        if not SCons.Util.is_List(progs):
            progs = [ progs ]
        for prog in progs:
            path = self.WhereIs(prog)
            if path: return prog
        return None

    def Dictionary(self, *args):
	if not args:
	    return self._dict
	dlist = map(lambda x, s=self: s._dict[x], args)
	if len(dlist) == 1:
	    dlist = dlist[0]
	return dlist

    def FindIxes(self, paths, prefix, suffix):
        """
        Search a list of paths for something that matches the prefix and suffix.

        paths - the list of paths or nodes.
        prefix - construction variable for the prefix.
        suffix - construction variable for the suffix.
        """

        suffix = self.subst('$'+suffix)
        prefix = self.subst('$'+prefix)

        for path in paths:
            dir,name = os.path.split(str(path))
            if name[:len(prefix)] == prefix and name[-len(suffix):] == suffix: 
                return path

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
            env['__env__'] = env
            new = {}
            for key, value in overrides.items():
                new[key] = SCons.Util.scons_subst_once(value, self, key)
            env._dict.update(new)
            return env
        else:
            return self

    def ParseConfig(self, command, function=None):
        """
        Use the specified function to parse the output of the command
        in order to modify the current environment. The 'command'
        can be a string or a list of strings representing a command and
        it's arguments. 'Function' is an optional argument that takes
        the environment and the output of the command. If no function is
        specified, the output will be treated as the output of a typical
        'X-config' command (i.e. gtk-config) and used to set the CPPPATH,
        LIBPATH, LIBS, and CCFLAGS variables.
        """

        # the default parse function
        def parse_conf(env, output):
            dict = {
                'CPPPATH' : [],
                'LIBPATH' : [],
                'LIBS'    : [],
                'CCFLAGS' : [],
            }
            static_libs = []
    
            params = string.split(output)
            for arg in params:
                switch = arg[0:1]
                opt = arg[1:2]
                if switch == '-':
                    if opt == 'L':
                        dict['LIBPATH'].append(arg[2:])
                    elif opt == 'l':
                        dict['LIBS'].append(arg[2:])
                    elif opt == 'I':
                        dict['CPPPATH'].append(arg[2:])
                    else:
                        dict['CCFLAGS'].append(arg)
                else:
                    static_libs.append(arg)
            apply(env.Append, (), dict)
            return static_libs
    
        if function is None:
            function = parse_conf
        if type(command) is type([]):
            command = string.join(command)
        command = self.subst(command)
        return function(self, os.popen(command).read())

    def Platform(self, platform):
        platform = self.subst(platform)
        return SCons.Platform.Platform(platform)(self)

    def Prepend(self, **kw):
        """Prepend values to existing construction variables
        in an Environment.
        """
        kw = our_deepcopy(kw)
        for key, val in kw.items():
            try:
                orig = self._dict[key]
            except KeyError:
                # No existing variable in the environment, so just set
                # it to the new value.
                self._dict[key] = val
                continue

            try:
                # Most straightforward:  just try to add them together.
                # This will work in most cases, when the original and
                # new values are of compatible types.
                self._dict[key] = val + orig
                continue
            except TypeError:
                pass

            try:
                # Try to update a dictionary value with another.
                # If orig isn't a dictionary, it won't have an
                # update() method; if val isn't a dictionary, it
                # won't have a keys() method.  Either way, it's
                # an AttributeError.
                orig.update(val)
                continue
            except AttributeError:
                pass

            try:
                # Check if the added value is a list.
                add_to_val = val.append
            except AttributeError:
                pass
            else:
                # The added value is a list, so append the original to it
                # (if there's a value to append).
                if orig:
                    add_to_val(orig)
                self._dict[key] = val
                continue

            # The added value isn't a list, but the original is (by
            # process of elimination), so insert the the new value in
            # the original (if there's one to insert).
            if val:
                orig.insert(0, val)

    def PrependENVPath(self, name, newpath, envname = 'ENV', sep = os.pathsep):
        """Prepend path elements to the path 'name' in the 'ENV'
        dictionary for this environment.  Will only add any particular
        path once, and will normpath and normcase all paths to help
        assure this.  This can also handle the case where the env
        variable is a list instead of a string.
        """

        orig = ''
        if self._dict.has_key(envname) and self._dict[envname].has_key(name):
            orig = self._dict[envname][name]

        nv = SCons.Util.PrependPath(orig, newpath, sep)
            
        if not self._dict.has_key(envname):
            self._dict[envname] = {}

        self._dict[envname][name] = nv

    def PrependUnique(self, **kw):
        """Append values to existing construction variables
        in an Environment, if they're not already there.
        """
        kw = our_deepcopy(kw)
        for key, val in kw.items():
            if not self._dict.has_key(key):
                self._dict[key] = val
            elif SCons.Util.is_Dict(self._dict[key]) and \
                 SCons.Util.is_Dict(val):
                self._dict[key].update(val)
            elif SCons.Util.is_List(val):
                dk = self._dict[key]
                if not SCons.Util.is_List(dk):
                    dk = [dk]
                val = filter(lambda x, dk=dk: x not in dk, val)
                self._dict[key] = val + dk
            else:
                dk = self._dict[key]
                if SCons.Util.is_List(dk):
                    if not val in dk:
                        self._dict[key] = val + dk
                else:
                    self._dict[key] = val + dk

    def Replace(self, **kw):
        """Replace existing construction variables in an Environment
        with new construction variables and/or values.
        """
        try:
            kwbd = our_deepcopy(kw['BUILDERS'])
            del kw['BUILDERS']
            self.__setitem__('BUILDERS', kwbd)
        except KeyError:
            pass
        self._dict.update(our_deepcopy(kw))

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
        old_prefix = self.subst('$'+old_prefix)
        old_suffix = self.subst('$'+old_suffix)

        new_prefix = self.subst('$'+new_prefix)
        new_suffix = self.subst('$'+new_suffix)

        dir,name = os.path.split(str(path))
        if name[:len(old_prefix)] == old_prefix:
            name = name[len(old_prefix):]
        if name[-len(old_suffix):] == old_suffix:
            name = name[:-len(old_suffix)]
        return os.path.join(dir, new_prefix+name+new_suffix)

    def Tool(self, tool, toolpath=[]):
        tool = self.subst(tool)
        return SCons.Tool.Tool(tool, map(self.subst, toolpath))(self)

    def WhereIs(self, prog, path=None, pathext=None):
        """Find prog in the path.  
        """
        if path is None:
            try:
                path = self['ENV']['PATH']
            except KeyError:
                pass
        elif SCons.Util.is_String(path):
            path = self.subst(path)
        if pathext is None:
            try:
                pathext = self['ENV']['PATHEXT']
            except KeyError:
                pass
        elif SCons.Util.is_String(pathext):
            pathext = self.subst(pathext)
        path = SCons.Util.WhereIs(prog, path, pathext)
        if path: return path
        return None

    #######################################################################
    # Public methods for doing real "SCons stuff" (manipulating
    # dependencies, setting attributes on targets, etc.).  These begin
    # with upper-case letters.  The essential characteristic of methods
    # in this section is that they all *should* have corresponding
    # same-named global functions.
    #######################################################################

    def Action(self, *args, **kw):
        nargs = self.subst(args)
        nkw = self.subst_kw(kw)
        return apply(SCons.Action.Action, nargs, nkw)

    def AddPreAction(self, files, action):
        nodes = self.arg2nodes(files, self.fs.Entry)
        action = SCons.Action.Action(action)
        for n in nodes:
            n.add_pre_action(action)
        return nodes
    
    def AddPostAction(self, files, action):
        nodes = self.arg2nodes(files, self.fs.Entry)
        action = SCons.Action.Action(action)
        for n in nodes:
            n.add_post_action(action)
        return nodes

    def Alias(self, target, *source, **kw):
        if not SCons.Util.is_List(target):
            target = [target]
        tlist = []
        for t in target:
            if not isinstance(t, SCons.Node.Alias.Alias):
                t = self.arg2nodes(self.subst(t), self.ans.Alias)[0]
            tlist.append(t)
        try:
            s = kw['source']
        except KeyError:
            try:
                s = source[0]
            except IndexError:
                s = None
        if s:
            if not SCons.Util.is_List(s):
                s = [s]
            s = filter(None, s)
            s = self.arg2nodes(s, self.fs.Entry)
            for t in tlist:
                AliasBuilder(self, t, s)
        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def AlwaysBuild(self, *targets):
        tlist = []
        for t in targets:
            tlist.extend(self.arg2nodes(t, self.fs.File))

        for t in tlist:
            t.set_always_build()

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def BuildDir(self, build_dir, src_dir, duplicate=1):
        build_dir = self.arg2nodes(build_dir, self.fs.Dir)[0]
        src_dir = self.arg2nodes(src_dir, self.fs.Dir)[0]
        self.fs.BuildDir(build_dir, src_dir, duplicate)

    def Builder(self, **kw):
        nkw = self.subst_kw(kw)
        return apply(SCons.Builder.Builder, [], nkw)

    def CacheDir(self, path):
        self.fs.CacheDir(self.subst(path))

    def Clean(self, target, files):
        global CleanTargets

        if not isinstance(target, SCons.Node.Node):
            target = self.subst(target)
            target = self.fs.Entry(target, create=1)
    
        if not SCons.Util.is_List(files):
            files = [files]
    
        nodes = []
        for f in files:
            if isinstance(f, SCons.Node.Node):
                nodes.append(f)
            else:
                nodes.extend(self.arg2nodes(f, self.fs.Entry))
    
        try:
            CleanTargets[target].extend(nodes)
        except KeyError:
            CleanTargets[target] = nodes

    def Configure(self, *args, **kw):
        nargs = [self]
        if args:
            nargs = nargs + self.subst_list(args)[0]
        nkw = self.subst_kw(kw)
        try:
            nkw['custom_tests'] = self.subst_kw(nkw['custom_tests'])
        except KeyError:
            pass
        return apply(SCons.SConf.SConf, nargs, nkw)

    def Command(self, target, source, action, **kw):
        """Builds the supplied target files from the supplied
        source files using the supplied action.  Action may
        be any type that the Builder constructor will accept
        for an action."""
        nkw = self.subst_kw(kw)
        nkw['action'] = action
        nkw['source_factory'] = self.fs.Entry
        bld = apply(SCons.Builder.Builder, (), nkw)
        return bld(self, target, source)

    def Depends(self, target, dependency):
        """Explicity specify that 'target's depend on 'dependency'."""
        tlist = self.arg2nodes(target, self.fs.Entry)
        dlist = self.arg2nodes(dependency, self.fs.Entry)
        for t in tlist:
            t.add_dependency(dlist)

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def Dir(self, name, *args, **kw):
        """
        """
        return apply(self.fs.Dir, (self.subst(name),) + args, kw)

    def Environment(self, **kw):
        return apply(SCons.Environment.Environment, [], self.subst_kw(kw))

    def Execute(self, action, *args, **kw):
        """Directly execute an action through an Environment
        """
        action = apply(self.Action, (action,) + args, kw)
        return action([], [], self)

    def File(self, name, *args, **kw):
        """
        """
        return apply(self.fs.File, (self.subst(name),) + args, kw)

    def FindFile(self, file, dirs):
        file = self.subst(file)
        nodes = self.arg2nodes(dirs, self.fs.Dir)
        return SCons.Node.FS.find_file(file, nodes, self.fs.File)

    def GetBuildPath(self, files):
        ret = map(str, self.arg2nodes(files, self.fs.Entry))
        if len(ret) == 1:
            return ret[0]
        return ret

    def Ignore(self, target, dependency):
        """Ignore a dependency."""
        tlist = self.arg2nodes(target, self.fs.Entry)
        dlist = self.arg2nodes(dependency, self.fs.Entry)
        for t in tlist:
            t.add_ignore(dlist)

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def Install(self, dir, source):
        """Install specified files in the given directory."""
        try:
            dnodes = self.arg2nodes(dir, self.fs.Dir)
        except TypeError:
            raise SCons.Errors.UserError, "Target `%s' of Install() is a file, but should be a directory.  Perhaps you have the Install() arguments backwards?" % str(dir)
        try:
            sources = self.arg2nodes(source, self.fs.File)
        except TypeError:
            if SCons.Util.is_List(source):
                raise SCons.Errors.UserError, "Source `%s' of Install() contains one or more non-files.  Install() source must be one or more files." % repr(map(str, source))
            else:
                raise SCons.Errors.UserError, "Source `%s' of Install() is not a file.  Install() source must be one or more files." % str(source)
        tgt = []
        for dnode in dnodes:
            for src in sources:
                target = self.fs.File(src.name, dnode)
                tgt.append(InstallBuilder(self, target, src))
        if len(tgt) == 1:
            tgt = tgt[0]
        return tgt

    def InstallAs(self, target, source):
        """Install sources as targets."""
        sources = self.arg2nodes(source, self.fs.File)
        targets = self.arg2nodes(target, self.fs.File)
        ret = []
        for src, tgt in map(lambda x, y: (x, y), sources, targets):
            ret.append(InstallBuilder(self, tgt, src))
        if len(ret) == 1:
            ret = ret[0]
        return ret

    def Literal(self, string):
        return SCons.Util.Literal(string)

    def Local(self, *targets):
        ret = []
        for targ in targets:
            if isinstance(targ, SCons.Node.Node):
                targ.set_local()
                ret.append(targ)
            else:
                for t in self.arg2nodes(targ, self.fs.Entry):
                   t.set_local()
                   ret.append(t)
        return ret

    def Precious(self, *targets):
        tlist = []
        for t in targets:
            tlist.extend(self.arg2nodes(t, self.fs.Entry))

        for t in tlist:
            t.set_precious()

        if len(tlist) == 1:
            tlist = tlist[0]
        return tlist

    def Repository(self, *dirs, **kw):
        dirs = self.arg2nodes(list(dirs), self.fs.Dir)
        apply(self.fs.Repository, dirs, kw)

    def Scanner(self, *args, **kw):
        nargs = []
        for arg in args:
            if SCons.Util.is_String(arg):
                arg = self.subst(arg)
            nargs.append(arg)
        nkw = self.subst_kw(kw)
        return apply(SCons.Scanner.Base, nargs, nkw)

    def SConsignFile(self, name=".sconsign.dbm", dbm_module=None):
        name = self.subst(name)
        if not os.path.isabs(name):
            name = os.path.join(str(self.fs.SConstruct_dir), name)
        SCons.Sig.SConsignFile(name, dbm_module)

    def SideEffect(self, side_effect, target):
        """Tell scons that side_effects are built as side 
        effects of building targets."""
        side_effects = self.arg2nodes(side_effect, self.fs.Entry)
        targets = self.arg2nodes(target, self.fs.Entry)

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

    def SourceCode(self, entry, builder):
        """Arrange for a source code builder for (part of) a tree."""
        entries = self.arg2nodes(entry, self.fs.Entry)
        for entry in entries:
            entry.set_src_builder(builder)
        if len(entries) == 1:
            return entries[0]
        return entries

    def SourceSignatures(self, type):
        type = self.subst(type)
        if type == 'MD5':
            import SCons.Sig.MD5
            self._calc_module = SCons.Sig.MD5
        elif type == 'timestamp':
            import SCons.Sig.TimeStamp
            self._calc_module = SCons.Sig.TimeStamp
        else:
            raise UserError, "Unknown source signature type '%s'"%type

    def Split(self, arg):
        """This function converts a string or list into a list of strings
        or Nodes.  This makes things easier for users by allowing files to
        be specified as a white-space separated list to be split.
        The input rules are:
            - A single string containing names separated by spaces. These will be
              split apart at the spaces.
            - A single Node instance
            - A list containing either strings or Node instances. Any strings
              in the list are not split at spaces.
        In all cases, the function returns a list of Nodes and strings."""
        if SCons.Util.is_List(arg):
            return map(self.subst, arg)
        elif SCons.Util.is_String(arg):
            return string.split(self.subst(arg))
        else:
            return [self.subst(arg)]

    def TargetSignatures(self, type):
        type = self.subst(type)
        if type == 'build':
            self._build_signature = 1
        elif type == 'content':
            self._build_signature = 0
        else:
            raise SCons.Errors.UserError, "Unknown target signature type '%s'"%type

    def Value(self, value):
        """
        """
        return SCons.Node.Python.Value(value)

# The entry point that will be used by the external world
# to refer to a construction environment.  This allows the wrapper
# interface to extend a construction environment for its own purposes
# by subclassing SCons.Environment.Base and then assigning the
# class to SCons.Environment.Environment.

Environment = Base
