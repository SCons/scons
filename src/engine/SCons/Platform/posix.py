"""SCons.Platform.posix

Platform-specific initialization for POSIX (Linux, UNIX, etc.) systems.

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
import popen2
import string
import sys

import SCons.Util

exitvalmap = {
    2 : 127,
    13 : 126,
}

def escape(arg):
    "escape shell special characters"
    slash = '\\'
    special = '"$'

    arg = string.replace(arg, slash, slash+slash)
    for c in special:
        arg = string.replace(arg, c, slash+c)

    return '"' + arg + '"'

def _get_env_command(sh, escape, cmd, args, env):
    if env:
        s = 'env -i '
        for key in env.keys():
            s = s + '%s=%s '%(key, escape(env[key]))
        s = s + sh + ' -c '
        s = s + escape(string.join(args))
    else:
        s = string.join(args)
    return s

def env_spawn(sh, escape, cmd, args, env):
    s = _get_env_command( sh, escape, cmd, args, env)
    stat = os.system(s)
    if stat & 0xff:
        return stat | 0x80
    return stat >> 8

def fork_spawn(sh, escape, cmd, args, env):
    pid = os.fork()
    if not pid:
        # Child process.
        exitval = 127
        args = [sh, '-c', string.join(args)]
        try:
            os.execvpe(sh, args, env)
        except OSError, e:
            exitval = exitvalmap[e[0]]
            sys.stderr.write("scons: %s: %s\n" % (cmd, e[1]))
        os._exit(exitval)
    else:
        # Parent process.
        pid, stat = os.waitpid(pid, 0)
        if stat & 0xff:
            return stat | 0x80
        return stat >> 8

def piped_env_spawn(sh, escape, cmd, args, env, stdout, stderr):
    # spawn using Popen3 combined with the env command
    # the command name and the command's stdout is written to stdout
    # the command's stderr is written to stderr
    s = _get_env_command( sh, escape, cmd, args, env)
    # write the command line out
    if stdout != None:
        stdout.write(string.join(args) + '\n')
    proc = popen2.Popen3(s, 1)
    # process stdout
    if stdout != None:
        #for line in proc.fromchild.xreadlines():
        #    stdout.write(line)
        while 1:
            line = proc.fromchild.readline()
            if not line:
                break
            stdout.write(line)
    # process stderr
    if stderr != None:
        #for line in proc.childerr.xreadlines():
        #    stderr.write(line)
        while 1:
            line = proc.childerr.readline()
            if not line:
                break
            stderr.write(line)
    stat = proc.wait()
    if stat & 0xff:
        return stat | 0x80
    return stat >> 8
    
def piped_fork_spawn(sh, escape, cmd, args, env, stdout, stderr):
    # spawn using fork / exec and providing a pipe for the command's
    # stdout / stderr stream
    if stdout != stderr:
        (rFdOut, wFdOut) = os.pipe()
        (rFdErr, wFdErr) = os.pipe()
    else:
        (rFdOut, wFdOut) = os.pipe()
        rFdErr = rFdOut
        wFdErr = wFdOut
    # write the command line out
    if stdout != None:
        stdout.write(string.join(args) + '\n')
    # do the fork
    pid = os.fork()
    if not pid:
        # Child process
        os.close( rFdOut )
        if rFdOut != rFdErr:
            os.close( rFdErr )
        os.dup2( wFdOut, 1 ) # is there some symbolic way to do that ?
        os.dup2( wFdErr, 2 )
        os.close( wFdOut )
        if stdout != stderr:
            os.close( wFdErr )
        exitval = 127
        args = [sh, '-c', string.join(args)]
        try:
            os.execvpe(sh, args, env)
        except OSError, e:
            exitval = exitvalmap[e[0]]
            stderr.write("scons: %s: %s\n" % (cmd, e[1]))
        os._exit(exitval)
    else:
        # Parent process
        pid, stat = os.waitpid(pid, 0)
        os.close( wFdOut )
        if stdout != stderr:
            os.close( wFdErr )        
        childOut = os.fdopen( rFdOut )
        if stdout != stderr:
            childErr = os.fdopen( rFdErr )
        else:
            childErr = childOut
        # process stdout
        if stdout != None:
            #for line in childOut.xreadlines():
            #    stdout.write(line)
            while 1:
                line = childOut.readline()
                if not line:
                    break
                stdout.write(line)
        # process stderr
        if stderr != None:
            #for line in childErr.xreadlines():
            #    stderr.write(line)
            while 1:
                line = childErr.readline()
                if not line:
                    break
                stdout.write(line)
        os.close( rFdOut )
        if stdout != stderr:
            os.close( rFdErr )
        if stat & 0xff:
            return stat | 0x80
        return stat >> 8

           
    
def generate(env):

    # If the env command exists, then we can use os.system()
    # to spawn commands, otherwise we fall back on os.fork()/os.exec().
    # os.system() is prefered because it seems to work better with
    # threads (i.e. -j) and is more efficient than forking Python.
    if env.Detect('env'):
        spawn = env_spawn
        pspawn = piped_env_spawn
    else:
        spawn = fork_spawn
        pspawn = piped_fork_spawn

    if not env.has_key('ENV'):
        env['ENV']        = {}
    env['ENV']['PATH']    = '/usr/local/bin:/bin:/usr/bin'
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.o'
    env['SHOBJPREFIX']    = '$OBJPREFIX'
    env['SHOBJSUFFIX']    = '$OBJSUFFIX'
    env['PROGPREFIX']     = ''
    env['PROGSUFFIX']     = ''
    env['LIBPREFIX']      = 'lib'
    env['LIBSUFFIX']      = '.a'
    env['SHLIBPREFIX']    = '$LIBPREFIX'
    env['SHLIBSUFFIX']    = '.so'
    env['LIBPREFIXES']    = '$LIBPREFIX'
    env['LIBSUFFIXES']    = [ '$LIBSUFFIX', '$SHLIBSUFFIX' ]
    env['PSPAWN']         = pspawn
    env['SPAWN']          = spawn
    env['SHELL']          = 'sh'
    env['ESCAPE']         = escape
