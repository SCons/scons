"""engine.SCons.Action

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
import string
import sys
import UserDict

import SCons.Util
import SCons.Errors


print_actions = 1;
execute_actions = 1;

exitvalmap = {
    2 : 127,
    13 : 126,
}

default_ENV = None

def rfile(n):
    try:
        return n.rfile()
    except AttributeError:
        return n

def SetCommandHandler(func, escape = lambda x: x):
    raise SCons.Errors.UserError("SetCommandHandler() is no longer supported, use the SPAWN and ESCAPE construction variables.")

def GetCommandHandler():
    raise SCons.Errors.UserError("GetCommandHandler() is no longer supported, use the SPAWN construction variable.")

class CommandGenerator:
    """
    Wraps a command generator function so the Action() factory
    function can tell a generator function from a function action.
    """
    def __init__(self, generator):
        self.generator = generator

def _do_create_action(act):
    """This is the actual "implementation" for the
    Action factory method, below.  This handles the
    fact that passing lists to Action() itself has
    different semantics than passing lists as elements
    of lists.

    The former will create a ListAction, the latter
    will create a CommandAction by converting the inner
    list elements to strings."""

    if isinstance(act, ActionBase):
        return act
    elif SCons.Util.is_List(act):
        return CommandAction(act)
    elif isinstance(act, CommandGenerator):
        return CommandGeneratorAction(act.generator)
    elif callable(act):
        return FunctionAction(act)
    elif SCons.Util.is_String(act):
        var=SCons.Util.get_environment_var(act)
        if var:
            # This looks like a string that is purely an Environment
            # variable reference, like "$FOO" or "${FOO}".  We do
            # something special here...we lazily evaluate the contents
            # of that Environment variable, so a user could but something
            # like a function or a CommandGenerator in that variable
            # instead of a string.
            return CommandGeneratorAction(LazyCmdGenerator(var))
        listCmds = map(lambda x: CommandAction(string.split(x)),
                       string.split(act, '\n'))
        if len(listCmds) == 1:
            return listCmds[0]
        else:
            return ListAction(listCmds)
    else:
        return None

def Action(act):
    """A factory for action objects."""
    if SCons.Util.is_List(act):
        acts = filter(lambda x: not x is None,
                      map(_do_create_action, act))
        if len(acts) == 1:
            return acts[0]
        else:
            return ListAction(acts)
    else:
        return _do_create_action(act)

class ActionBase:
    """Base class for actions that create output objects."""
    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def show(self, string):
        print string

    def get_actions(self):
        return [self]

    def subst_dict(self, target, source, env):
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
                     used to generate the SOURCES and SOURCE
                     construction variables
        """

        dict = {}

        for k,v in env.items(): dict[k] = v

        if not SCons.Util.is_List(target):
            target = [target]

        dict['TARGETS'] = SCons.Util.PathList(map(os.path.normpath, map(str, target)))
        if dict['TARGETS']:
            dict['TARGET'] = dict['TARGETS'][0]

        def rstr(x):
            try:
                return x.rstr()
            except AttributeError:
                return str(x)
        if not SCons.Util.is_List(source):
            source = [source]
        dict['SOURCES'] = SCons.Util.PathList(map(os.path.normpath, map(rstr, source)))
        if dict['SOURCES']:
            dict['SOURCE'] = dict['SOURCES'][0]

        return dict

def _string_from_cmd_list(cmd_list):
    """Takes a list of command line arguments and returns a pretty
    representation for printing."""
    cl = []
    for arg in map(str, cmd_list):
        if ' ' in arg or '\t' in arg:
            arg = '"' + arg + '"'
        cl.append(arg)
    return string.join(cl)

_rm = re.compile(r'\$[()]')
_remove = re.compile(r'\$\(([^\$]|\$[^\(])*?\$\)')

class CommandAction(ActionBase):
    """Class for command-execution actions."""
    def __init__(self, cmd):
        self.cmd_list = cmd

    def execute(self, target, source, env):
        """Execute a command action.

        This will handle lists of commands as well as individual commands,
        because construction variable substitution may turn a single
        "command" into a list.  This means that this class can actually
        handle lists of commands, even though that's not how we use it
        externally.
        """
        escape = env.get('ESCAPE', lambda x: x)

        import SCons.Errors
        
        if env.has_key('SHELL'):
            shell = env['SHELL']
        else:
            raise SCons.Errors.UserError('Missing SHELL construction variable.')

        if env.has_key('SPAWN'):
            spawn = env['SPAWN']
        else:
            raise SCons.Errors.UserError('Missing SPAWN construction variable.')

        dict = self.subst_dict(target, source, env)
        cmd_list = SCons.Util.scons_subst_list(self.cmd_list, dict, {}, _rm)
        for cmd_line in cmd_list:
            if len(cmd_line):
                if print_actions:
                    self.show(_string_from_cmd_list(cmd_line))
                if execute_actions:
                    try:
                        ENV = dict['ENV']
                    except KeyError:
                        global default_ENV
                        if not default_ENV:
                            import SCons.Environment
                            default_ENV = SCons.Environment.Environment()['ENV']
                        ENV = default_ENV
                    # Escape the command line for the command
                    # interpreter we are using
                    map(lambda x, e=escape: x.escape(e), cmd_line)
                    cmd_line = map(str, cmd_line)
                    ret = spawn(shell, escape, cmd_line[0], cmd_line, ENV)
                    if ret:
                        return ret
        return 0

    def _sig_dict(self, target, source, env):
        """Supply a dictionary for use in computing signatures.

        For signature purposes, it doesn't matter what targets or
        sources we use, so long as we use the same ones every time
        so the signature stays the same.  We supply an array of two
        of each to allow for distinction between TARGET and TARGETS.
        """
        return self.subst_dict(['__t1__', '__t2__'], ['__s1__', '__s2__'], env)

    def get_raw_contents(self, target, source, env):
        """Return the complete contents of this action's command line.
        """
        return SCons.Util.scons_subst(string.join(self.cmd_list),
                                      self._sig_dict(target, source, env), {})

    def get_contents(self, target, source, env):
        """Return the signature contents of this action's command line.

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
        return SCons.Util.scons_subst(string.join(map(str, self.cmd_list)),
                                      self._sig_dict(target, source, env), {}, _remove)

class CommandGeneratorAction(ActionBase):
    """Class for command-generator actions."""
    def __init__(self, generator):
        self.generator = generator

    def __generate(self, target, source, env, for_signature):
        import SCons.Util

        # ensure that target is a list, to make it easier to write
        # generator functions:
        if not SCons.Util.is_List(target):
            target = [target]

        ret = self.generator(target=target, source=source, env=env, for_signature=for_signature)
        gen_cmd = Action(ret)
        if not gen_cmd:
            raise SCons.Errors.UserError("Object returned from command generator: %s cannot be used to create an Action." % repr(ret))
        return gen_cmd

    def execute(self, target, source, env):
        if not SCons.Util.is_List(source):
            source = [source]
        rsources = map(rfile, source)
        return self.__generate(target, source, env, 0).execute(target, rsources, env)

    def get_contents(self, target, source, env):
        """Return the signature contents of this action's command line.

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
        return self.__generate(target, source, env, 1).get_contents(target, source, env)

class LazyCmdGenerator:
    """This is a simple callable class that acts as a command generator.
    It holds on to a key into an Environment dictionary, then waits
    until execution time to see what type it is, then tries to
    create an Action out of it."""
    def __init__(self, var):
        self.var = SCons.Util.to_String(var)

    def __call__(self, target, source, env, for_signature):
        if env.has_key(self.var):
            return env[self.var]
        else:
            # The variable reference substitutes to nothing.
            return ''

class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
        self.function = function

    def execute(self, target, source, env):
        # if print_actions:
        # XXX:  WHAT SHOULD WE PRINT HERE?
        if execute_actions:
            if not SCons.Util.is_List(target):
                target = [target]

            if not SCons.Util.is_List(source):
                source = [source]
            rsources = map(rfile, source)

            return self.function(target=target, source=rsources, env=env)

    def get_contents(self, target, source, env):
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

    def get_actions(self):
        return self.list

    def execute(self, target, source, env):
        for l in self.list:
            r = l.execute(target, source, env)
            if r:
                return r
        return 0

    def get_contents(self, target, source, env):
        """Return the signature contents of this action list.

        Simple concatenation of the signatures of the elements.
        """

        ret = ""
        for a in self.list:
            ret = ret + a.get_contents(target, source, env)
        return ret

