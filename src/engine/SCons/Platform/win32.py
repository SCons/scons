"""SCons.Platform.win32

Platform-specific initialization for Win32 systems.

There normally shouldn't be any need to import this module directly.  It
will usually be imported through the generic SCons.Platform.Platform()
selection method.
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
import string
import sys
import tempfile
from SCons.Platform.posix import exitvalmap

import SCons.Util

class TempFileMunge:
    """A callable class.  You can set an Environment variable to this,
    then call it with a string argument, then it will perform temporary
    file substitution on it.  This is used to circumvent the win32 long command
    line limitation.

    Example usage:
    env["TEMPFILE"] = TempFileMunge
    env["LINKCOM"] = "${TEMPFILE('$LINK $TARGET $SOURCES')}"
    """
    def __init__(self, cmd):
        self.cmd = cmd

    def __call__(self, target, source, env, for_signature):
        cmd = env.subst_list(self.cmd, 0, target, source)[0]
        if for_signature or \
           (reduce(lambda x, y: x + len(y), cmd, 0) + len(cmd)) <= 2048:
            return self.cmd
        else:
            # In Cygwin, we want to use rm to delete the temporary file,
            # because del does not exist in the sh shell.
            rm = env.Detect('rm') or 'del'

            # We do a normpath because mktemp() has what appears to be
            # a bug in Win32 that will use a forward slash as a path
            # delimiter.  Win32's link mistakes that for a command line
            # switch and barfs.
            tmp = os.path.normpath(tempfile.mktemp())
            native_tmp = SCons.Util.get_native_path(tmp)

            # The sh shell will try to escape the backslashes in the
            # path, so unescape them.
            if env['SHELL'] and env['SHELL'] == 'sh':
                native_tmp = string.replace(native_tmp, '\\', r'\\\\')

            args = map(SCons.Util.quote_spaces, cmd[1:])
            open(tmp, 'w').write(string.join(args, " ") + "\n")
            return [ cmd[0], '@' + native_tmp + '\n' + rm, native_tmp ]

# The upshot of all this is that, if you are using Python 1.5.2,
# you had better have cmd or command.com in your PATH when you run
# scons.

def piped_spawn(sh, escape, cmd, args, env, stdout, stderr):
    if not sh:
        sys.stderr.write("scons: Could not find command interpreter, is it in your PATH?\n")
        return 127
    else:
        # NOTE: This is just a big, big hack.  What we do is simply pipe the
        # output to a temporary file and then write it to the streams.
        # I DO NOT know the effect of adding these to a command line that
        # already has indirection symbols.
        tmpFile = os.path.normpath(tempfile.mktemp())
        args.append(">" + str(tmpFile))
        args.append("2>&1")
        if stdout != None:
            # ToDo: use the printaction instead of that
            stdout.write(string.join(args) + "\n")
        try:
            try:
                args = [sh, '/C', escape(string.join(args)) ]
                ret = os.spawnve(os.P_WAIT, sh, args, env)
            except OSError, e:
                ret = exitvalmap[e[0]]
                stderr.write("scons: %s: %s\n" % (cmd, e[1]))
            try:
                input = open( tmpFile, "r" )
                while 1:
                    line = input.readline()
                    if not line:
                        break
                    if stdout != None:
                        stdout.write(line)
                    if stderr != None and stderr != stdout:
                        stderr.write(line)
            finally:
                input.close()
        finally:
            try:
                os.remove( tmpFile )
            except OSError:
                # What went wrong here ??
                pass
        return ret

def spawn(sh, escape, cmd, args, env):
    if not sh:
        sys.stderr.write("scons: Could not find command interpreter, is it in your PATH?\n")
        return 127
    else:
        try:
            args = [sh, '/C', escape(string.join(args)) ]
            ret = os.spawnve(os.P_WAIT, sh, args, env)
        except OSError, e:
            ret = exitvalmap[e[0]]
            sys.stderr.write("scons: %s: %s\n" % (cmd, e[1]))
        return ret

# Windows does not allow special characters in file names
# anyway, so no need for an escape function, we will just quote
# the arg.
escape = lambda x: '"' + x + '"'

# Get the windows system directory name
def get_system_root():
    # A resonable default if we can't read the registry
    try:
        val = os.environ['SYSTEMROOT']
    except:
        val = "C:/WINDOWS"
        pass

    # First see if we can look in the registry...
    if SCons.Util.can_read_reg:
        try:
            # Look for Windows NT system root
            k=SCons.Util.RegOpenKeyEx(SCons.Util.hkey_mod.HKEY_LOCAL_MACHINE,
                                      'Software\\Microsoft\\Windows NT\\CurrentVersion')
            val, tok = SCons.Util.RegQueryValueEx(k, 'SystemRoot')
        except SCons.Util.RegError:
            try:
                # Okay, try the Windows 9x system root
                k=SCons.Util.RegOpenKeyEx(SCons.Util.hkey_mod.HKEY_LOCAL_MACHINE,
                                          'Software\\Microsoft\\Windows\\CurrentVersion')
                val, tok = SCons.Util.RegQueryValueEx(k, 'SystemRoot')
            except:
                pass
    return val

# Get the location of the program files directory
def get_program_files_dir():
    # Now see if we can look in the registry...
    val = ''
    if SCons.Util.can_read_reg:
        try:
            # Look for Windows Program Files directory
            k=SCons.Util.RegOpenKeyEx(SCons.Util.hkey_mod.HKEY_LOCAL_MACHINE,
                                      'Software\\Microsoft\\Windows\\CurrentVersion')
            val, tok = SCons.Util.RegQueryValueEx(k, 'ProgramFilesDir')
        except SCons.Util.RegError:
            val = ''
            pass

    if val == '':
        # A reasonable default if we can't read the registry
        # (Actually, it's pretty reasonable even if we can :-)
        val = os.path.join(os.path.dirname(get_system_root()),"Program Files")
        
    return val

def generate(env):
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
        cmd_interp = env.Detect('cmd')
        if not cmd_interp:
            cmd_interp = env.Detect('command')
    
    if not env.has_key('ENV'):
        env['ENV']        = {}

    # Import things from the external environment to the construction
    # environment's ENV.  This is a potential slippery slope, because we
    # *don't* want to make builds dependent on the user's environment by
    # default.  We're doing this for SYSTEMROOT, though, because it's
    # needed for anything that uses sockets, and seldom changes.  Weigh
    # the impact carefully before adding other variables to this list.
    import_env = [ 'SYSTEMROOT' ]
    for var in import_env:
        v = os.environ.get(var)
        if v:
            env['ENV'][var] = v

    env['ENV']['PATHEXT'] = '.COM;.EXE;.BAT;.CMD'
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.obj'
    env['SHOBJPREFIX']    = '$OBJPREFIX'
    env['SHOBJSUFFIX']    = '$OBJSUFFIX'
    env['PROGPREFIX']     = ''
    env['PROGSUFFIX']     = '.exe'
    env['LIBPREFIX']      = ''
    env['LIBSUFFIX']      = '.lib'
    env['SHLIBPREFIX']    = ''
    env['SHLIBSUFFIX']    = '.dll'
    env['LIBPREFIXES']    = [ '$LIBPREFIX', '$SHLIBPREFIX' ]
    env['LIBSUFFIXES']    = [ '$LIBSUFFIX', '$SHLIBSUFFIX' ]
    env['PSPAWN']         = piped_spawn
    env['SPAWN']          = spawn
    env['SHELL']          = cmd_interp
    env['TEMPFILE']       = TempFileMunge
    env['ESCAPE']         = escape
