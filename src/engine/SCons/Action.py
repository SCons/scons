"""engine.SCons.Action

XXX

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

import os
import os.path
import re
import string

import SCons.Errors
import SCons.Util

class _Null:
    pass

_null = _Null

print_actions = 1;
execute_actions = 1;

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

def _actionAppend(act1, act2):
    # This function knows how to slap two actions together.
    # Mainly, it handles ListActions by concatenating into
    # a single ListAction.
    a1 = Action(act1)
    a2 = Action(act2)
    if a1 is None or a2 is None:
        raise TypeError, "Cannot append %s to %s" % (type(act1), type(act2))
    if isinstance(a1, ListAction):
        if isinstance(a2, ListAction):
            return ListAction(a1.list + a2.list)
        else:
            return ListAction(a1.list + [ a2 ])
    else:
        if isinstance(a2, ListAction):
            return ListAction([ a1 ] + a2.list)
        else:
            return ListAction([ a1, a2 ])

class CommandGenerator:
    """
    Wraps a command generator function so the Action() factory
    function can tell a generator function from a function action.
    """
    def __init__(self, generator):
        self.generator = generator

    def __add__(self, other):
        return _actionAppend(self, other)

    def __radd__(self, other):
        return _actionAppend(other, self)

def _do_create_action(act, strfunction=_null, varlist=[]):
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
        return FunctionAction(act, strfunction=strfunction, varlist=varlist)
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
        listCmds = map(lambda x: CommandAction(x), string.split(act, '\n'))
        if len(listCmds) == 1:
            return listCmds[0]
        else:
            return ListAction(listCmds)
    else:
        return None

def Action(act, strfunction=_null, varlist=[]):
    """A factory for action objects."""
    if SCons.Util.is_List(act):
        acts = map(lambda x, s=strfunction, v=varlist:
                          _do_create_action(x, s, v),
                   act)
        acts = filter(lambda x: not x is None, acts)
        if len(acts) == 1:
            return acts[0]
        else:
            return ListAction(acts)
    else:
        return _do_create_action(act, strfunction=strfunction, varlist=varlist)

class ActionBase:
    """Base class for actions that create output objects."""
    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def show(self, string):
        if print_actions:
            print string

    def get_actions(self):
        return [self]

    def __add__(self, other):
        return _actionAppend(self, other)

    def __radd__(self, other):
        return _actionAppend(other, self)

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
        # Cmd list can actually be a list or a single item...basically
        # anything that we could pass in as the first arg to
        # scons_subst_list().
        self.cmd_list = cmd

    def strfunction(self, target, source, env):
        cmd_list = SCons.Util.scons_subst_list(self.cmd_list, env, _rm,
                                               target, source)
        return map(_string_from_cmd_list, cmd_list)

    def __call__(self, target, source, env):
        """Execute a command action.

        This will handle lists of commands as well as individual commands,
        because construction variable substitution may turn a single
        "command" into a list.  This means that this class can actually
        handle lists of commands, even though that's not how we use it
        externally.
        """
        import SCons.Util

        escape = env.get('ESCAPE', lambda x: x)

        if env.has_key('SHELL'):
            shell = env['SHELL']
        else:
            raise SCons.Errors.UserError('Missing SHELL construction variable.')

        # for SConf support (by now): check, if we want to pipe the command
        # output to somewhere else
        if env.has_key('PIPE_BUILD'):
            pipe_build = 1
            if env.has_key('PSPAWN'):
                pspawn = env['PSPAWN']
            else:
                raise SCons.Errors.UserError('Missing PSPAWN construction variable.')
            if env.has_key('PSTDOUT'):
                pstdout = env['PSTDOUT']
            else:
                raise SCons.Errors.UserError('Missing PSTDOUT construction variable.')
            if env.has_key('PSTDERR'):
                pstderr = env['PSTDERR']
            else:
                raise SCons.Errors.UserError('Missing PSTDOUT construction variable.')
        else:
            pipe_build = 0
            if env.has_key('SPAWN'):
                spawn = env['SPAWN']
            else:
                raise SCons.Errors.UserError('Missing SPAWN construction variable.')

        cmd_list = SCons.Util.scons_subst_list(self.cmd_list, env, _rm,
                                               target, source)
        for cmd_line in cmd_list:
            if len(cmd_line):
                if print_actions:
                    self.show(_string_from_cmd_list(cmd_line))
                if execute_actions:
                    try:
                        ENV = env['ENV']
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
                    if pipe_build:
                        ret = pspawn( shell, escape, cmd_line[0], cmd_line,
                                      ENV, pstdout, pstderr )
                    else:
                        ret = spawn(shell, escape, cmd_line[0], cmd_line, ENV)
                    if ret:
                        return ret
        return 0

    def get_raw_contents(self, target, source, env):
        """Return the complete contents of this action's command line.
        """
        # We've discusssed using the real target and source names in
        # a CommandAction's signature contents.  This would have the
        # advantage of recompiling when a file's name changes (keeping
        # debug info current), but it would currently break repository
        # logic that will change the file name based on whether the
        # files come from a repository or locally.  If we ever move to
        # that scheme, though, here's how we'd do it:
        #return SCons.Util.scons_subst(string.join(self.cmd_list),
        #                              self.subst_dict(target, source, env),
        #                              {})
        cmd = self.cmd_list
        if not SCons.Util.is_List(cmd):
            cmd = [ cmd ]
        return SCons.Util.scons_subst(string.join(map(str, cmd)),
                                      env)

    def get_contents(self, target, source, env):
        """Return the signature contents of this action's command line.

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
        # We've discusssed using the real target and source names in
        # a CommandAction's signature contents.  This would have the
        # advantage of recompiling when a file's name changes (keeping
        # debug info current), but it would currently break repository
        # logic that will change the file name based on whether the
        # files come from a repository or locally.  If we ever move to
        # that scheme, though, here's how we'd do it:
        #return SCons.Util.scons_subst(string.join(map(str, self.cmd_list)),
        #                              self.subst_dict(target, source, env),
        #                              {},
        #                              _remove)
        cmd = self.cmd_list
        if not SCons.Util.is_List(cmd):
            cmd = [ cmd ]
        return SCons.Util.scons_subst(string.join(map(str, cmd)),
                                      env,
                                      _remove)

class CommandGeneratorAction(ActionBase):
    """Class for command-generator actions."""
    def __init__(self, generator):
        self.generator = generator

    def __generate(self, target, source, env, for_signature):
        # ensure that target is a list, to make it easier to write
        # generator functions:
        if not SCons.Util.is_List(target):
            target = [target]

        ret = self.generator(target=target, source=source, env=env, for_signature=for_signature)
        gen_cmd = Action(ret)
        if not gen_cmd:
            raise SCons.Errors.UserError("Object returned from command generator: %s cannot be used to create an Action." % repr(ret))
        return gen_cmd

    def __call__(self, target, source, env):
        if not SCons.Util.is_List(source):
            source = [source]
        rsources = map(rfile, source)
        act = self.__generate(target, source, env, 0)
        return act(target, rsources, env)

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

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

class FunctionAction(ActionBase):
    """Class for Python function actions."""

    def __init__(self, execfunction, strfunction=_null, varlist=[]):
        self.execfunction = execfunction
        if strfunction is _null:
            def strfunction(target, source, env, execfunction=execfunction):
                def quote(s):
                    return '"' + str(s) + '"'
                def array(a, q=quote):
                    return '[' + string.join(map(lambda x, q=q: q(x), a), ", ") + ']'
                try:
                    name = execfunction.__name__
                except AttributeError:
                    try:
                        name = execfunction.__class__.__name__
                    except AttributeError:
                        name = "unknown_python_function"
                tstr = len(target) == 1 and quote(target[0]) or array(target)
                sstr = len(source) == 1 and quote(source[0]) or array(source)
                return "%s(%s, %s)" % (name, tstr, sstr)
        self.strfunction = strfunction
        self.varlist = varlist

    def __call__(self, target, source, env):
        r = 0
        if not SCons.Util.is_List(target):
            target = [target]
        if not SCons.Util.is_List(source):
            source = [source]
        if print_actions and self.strfunction:
            s = self.strfunction(target, source, env)
            if s:
                self.show(s)
        if execute_actions:
            rsources = map(rfile, source)
            r = self.execfunction(target=target, source=rsources, env=env)
        return r

    def get_contents(self, target, source, env):
        """Return the signature contents of this callable action.

        By providing direct access to the code object of the
        function, Python makes this extremely easy.  Hooray!
        """
        try:
            # "self.execfunction" is a function.
            code = self.execfunction.func_code.co_code
        except:
            # "self.execfunction" is a callable object.
            code = self.execfunction.__call__.im_func.func_code.co_code
        return str(code) + env.subst(string.join(map(lambda v: '${'+v+'}',
                                                     self.varlist)))

class ListAction(ActionBase):
    """Class for lists of other actions."""
    def __init__(self, list):
        self.list = map(lambda x: Action(x), list)

    def get_actions(self):
        return self.list

    def __call__(self, target, source, env):
        for l in self.list:
            r = l(target, source, env)
            if r:
                return r
        return 0

    def get_contents(self, target, source, env):
        """Return the signature contents of this action list.

        Simple concatenation of the signatures of the elements.
        """
        return string.join(map(lambda x, t=target, s=source, e=env:
                                      x.get_contents(t, s, e),
                               self.list),
                           "")
