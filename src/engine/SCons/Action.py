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

if os.name == 'posix':

    def defaultSpawn(cmd, args, env):
        pid = os.fork()
        if not pid:
            # Child process.
            exitval = 127
            args = [ 'sh', '-c' ] + \
                   [ string.join(map(lambda x: string.replace(str(x),
                                                              ' ',
                                                              r'\ '),
                                     args)) ]
            try:
                os.execvpe('sh', args, env)
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
                return cmd
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
        return None

    # Attempt to find cmd.exe (for WinNT/2k/XP) or
    # command.com for Win9x

    cmd_interp = ''
    # First see if we can look in the registry...
    if SCons.Util.can_read_reg:
        try:
            # Look for Windows NT system root
            k=SCons.Util.RegOpenKeyEx(SCons.Util.hkey_mod.HKEY_LOCAL_MACHINE,
                                          'Software\\Microsoft\\Windows NT\\CurrentVersion')
            val, tok = SCons.Util.RegQueryValueEx(k, 'SystemRoot')
            cmd_interp = os.path.join(val, 'System32\\cmd.exe')
        except SCons.Util.RegError:
            try:
                # Okay, try the Windows 9x system root
                k=SCons.Util.RegOpenKeyEx(SCons.Util.hkey_mod.HKEY_LOCAL_MACHINE,
                                              'Software\\Microsoft\\Windows\\CurrentVersion')
                val, tok = SCons.Util.RegQueryValueEx(k, 'SystemRoot')
                cmd_interp = os.path.join(val, 'command.com')
            except:
                pass
    if not cmd_interp:
        cmd_interp = pathsearch('cmd', os.environ)
        if not cmd_interp:
            cmd_interp = pathsearch('command', os.environ)

    # The upshot of all this is that, if you are using Python 1.5.2,
    # you had better have cmd or command.com in your PATH when you run
    # scons.

    def defaultSpawn(cmd, args, env):
        if not cmd_interp:
            sys.stderr.write("scons: Could not find command interpreter, is it in your PATH?\n")
            return 127
        else:
            try:

                a = [ cmd_interp, '/C', args[0] ]
                for arg in args[1:]:
                    if ' ' in arg or '\t' in arg:
                        arg = '"' + arg + '"'
                    a.append(arg)
                ret = os.spawnve(os.P_WAIT, cmd_interp, a, env)
            except OSError, e:
                ret = exitvalmap[e[0]]
                sys.stderr.write("scons: %s: %s\n" % (cmd, e[1]))
            return ret
else:
    def defaultSpawn(cmd, args, env):
        sys.stderr.write("scons: Unknown os '%s', cannot spawn command interpreter.\n" % os.name)
        sys.stderr.write("scons: Set your command handler with SetCommandHandler().\n")
        return 127

spawn = defaultSpawn

def SetCommandHandler(func):
    global spawn
    spawn = func

def GetCommandHandler():
    global spawn
    return spawn

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
                     used to generate the SOURCES and SOURCE 
                     construction variables

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
            except (IndexError, AttributeError):
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
            if dict['SOURCES']:
                dict['SOURCE'] = dict['SOURCES'][0]

        dict.update(kw)

        return dict

def _string_from_cmd_list(cmd_list):
    """Takes a list of command line arguments and returns a pretty
    representation for printing."""
    cl = []
    for arg in cmd_list:
        if ' ' in arg or '\t' in arg:
            arg = '"' + arg + '"'
        cl.append(arg)
    return string.join(cl)

_rm = re.compile(r'\$[()]')
_remove = re.compile(r'\$\(([^\$]|\$[^\(])*?\$\)')

class EnvDictProxy(UserDict.UserDict):
    """This is a dictionary-like class that contains the
    Environment dictionary we pass to FunctionActions
    and CommandGeneratorActions.

    In addition to providing
    normal dictionary-like access to the variables in the
    Environment, it also exposes the functions subst()
    and subst_list(), allowing users to easily do variable
    interpolation when writing their FunctionActions
    and CommandGeneratorActions."""

    def __init__(self, env):
        UserDict.UserDict.__init__(self, env)

    def subst(self, string, raw=0):
        if raw:
            regex_remove = None
        else:
            regex_remove = _rm
        return SCons.Util.scons_subst(string, self.data, {}, regex_remove)

    def subst_list(self, string, raw=0):
        if raw:
            regex_remove = None
        else:
            regex_remove = _rm
        return SCons.Util.scons_subst_list(string, self.data, {}, regex_remove)

class CommandAction(ActionBase):
    """Class for command-execution actions."""
    def __init__(self, cmd):
        import SCons.Util
        
        self.cmd_list = map(SCons.Util.to_String, cmd)

    def execute(self, **kw):
        dict = apply(self.subst_dict, (), kw)
        import SCons.Util
        cmd_list = SCons.Util.scons_subst_list(self.cmd_list, dict, {}, _rm)
        for cmd_line in cmd_list:
            if len(cmd_line):
                if print_actions:
                    self.show(_string_from_cmd_list(cmd_line))
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

    def _sig_dict(self, kw):
        """Supply a dictionary for use in computing signatures.

        For signature purposes, it doesn't matter what targets or
        sources we use, so long as we use the same ones every time
        so the signature stays the same.  We supply an array of two
        of each to allow for distinction between TARGET and TARGETS.
        """
        kw['target'] = ['__t1__', '__t2__']
        kw['source'] = ['__s1__', '__s2__']
        return apply(self.subst_dict, (), kw)

    def get_raw_contents(self, **kw):
        """Return the complete contents of this action's command line.
        """
        return SCons.Util.scons_subst(string.join(self.cmd_list),
                                      self._sig_dict(kw), {})

    def get_contents(self, **kw):
        """Return the signature contents of this action's command line.

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
        return SCons.Util.scons_subst(string.join(self.cmd_list),
                                      self._sig_dict(kw), {}, _remove)

class CommandGeneratorAction(ActionBase):
    """Class for command-generator actions."""
    def __init__(self, generator):
        self.generator = generator

    def __generate(self, kw, for_signature):
        import SCons.Util

        # Wrap the environment dictionary in an EnvDictProxy
        # object to make variable interpolation easier for the
        # client.
        args = copy.copy(kw)
        args['for_signature'] = for_signature
        if args.has_key("env") and not isinstance(args["env"], EnvDictProxy):
            args["env"] = EnvDictProxy(args["env"])

        # ensure that target is a list, to make it easier to write
        # generator functions:
        if args.has_key("target") and not SCons.Util.is_List(args["target"]):
            args["target"] = [args["target"]]

        ret = apply(self.generator, (), args)
        gen_cmd = Action(ret)
        if not gen_cmd:
            raise SCons.Errors.UserError("Object returned from command generator: %s cannot be used to create an Action." % repr(ret))
        return gen_cmd

    def execute(self, **kw):
        return apply(self.__generate(kw, 0).execute, (), kw)

    def get_contents(self, **kw):
        """Return the signature contents of this action's command line.

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
        return apply(self.__generate(kw, 1).get_contents, (), kw)

class LazyCmdGenerator:
    """This is a simple callable class that acts as a command generator.
    It holds on to a key into an Environment dictionary, then waits
    until execution time to see what type it is, then tries to
    create an Action out of it."""
    def __init__(self, var):
        self.var = SCons.Util.to_String(var)

    def __call__(self, env, **kw):
        if env.has_key(self.var):
            return env[self.var]
        else:
            # The variable reference substitutes to nothing.
            return ''

class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
        self.function = function

    def execute(self, **kw):
        # if print_actions:
        # XXX:  WHAT SHOULD WE PRINT HERE?
        if execute_actions:
            if kw.has_key('target') and not \
               SCons.Util.is_List(kw['target']):
                kw['target'] = [ kw['target'] ]
            if kw.has_key('source') and not \
               SCons.Util.is_List(kw['source']):
                kw['source'] = [ kw['source'] ]
            if kw.has_key("env") and not isinstance(kw["env"], EnvDictProxy):
                kw["env"] = EnvDictProxy(kw["env"])
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
