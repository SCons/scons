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

import os
import os.path
import re
import string
import sys

import SCons.Util

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

class CommandGenerator:
    """
    Wrappes a command generator function so the Action() factory
    function can tell a generator function from a function action.
    """
    def __init__(self, generator):
        self.generator = generator


def Action(act):
    """A factory for action objects."""
    if isinstance(act, ActionBase):
        return act
    elif isinstance(act, CommandGenerator):
        return CommandGeneratorAction(act.generator)
    elif callable(act):
        return FunctionAction(act)
    elif SCons.Util.is_String(act):
        return CommandAction(act)
    elif SCons.Util.is_List(act):
        return ListAction(act)
    else:
        return None

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

_rm = re.compile(r'\$[()]')
_remove = re.compile(r'\$\(([^\$]|\$[^\(])*?\$\)')

class CommandAction(ActionBase):
    """Class for command-execution actions."""
    def __init__(self, string):
        self.command = string

    def execute(self, **kw):
        import SCons.Util
        dict = apply(self.subst_dict, (), kw)
        cmd_list = SCons.Util.scons_subst_list(self.command, dict, {}, _rm)
        for cmd_line in cmd_list:
            if len(cmd_line):
                if print_actions:
                    cl = []
                    for arg in cmd_line:
                        if ' ' in arg or '\t' in arg:
                            arg = '"' + arg + '"'
                        cl.append(arg)
                    self.show(string.join(cl))
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
        return SCons.Util.scons_subst(self.command, self._sig_dict(kw), {})

    def get_contents(self, **kw):
        """Return the signature contents of this action's command line.

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
        return SCons.Util.scons_subst(self.command, self._sig_dict(kw), {}, _remove)

class CommandGeneratorAction(ActionBase):
    """Class for command-generator actions."""
    def __init__(self, generator):
        self.generator = generator

    def execute(self, **kw):
        # ensure that target is a list, to make it easier to write
        # generator functions:
        import SCons.Util
        if kw.has_key("target") and not SCons.Util.is_List(kw["target"]):
            kw["target"] = [kw["target"]]

        cmd_list = apply(self.generator, (), kw)

        cmd_list = map(lambda x: map(str, x), cmd_list)
        for cmd_line in cmd_list:
            if print_actions:
                self.show(cmd_line)
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

        This strips $(-$) and everything in between the string,
        since those parts don't affect signatures.
        """
	kw['source'] = ["__s1__", "__s2__"]
	kw['target'] = ["__t1__", "__t2__"]
	cmd_list = apply(self.generator, (), kw)
	cmd_list = map(lambda x: map(str, x), cmd_list)
	cmd_list = map(lambda x: string.join(x,  "\0"), cmd_list)
	cmd_list = map(lambda x: _remove.sub('', x), cmd_list)
	cmd_list = map(lambda x: filter(lambda y: y, string.split(x, "\0")), cmd_list)
	return cmd_list

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
