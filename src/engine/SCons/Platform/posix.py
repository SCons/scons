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

import SCons.Util
import string
import os
import sys
import os.path

def escape(arg):
    "escape shell special characters"
    slash = '\\'
    special = '"$'

    arg = string.replace(arg, slash, slash+slash)
    for c in special:
        arg = string.replace(arg, c, slash+c)

    return '"' + arg + '"'

def env_spawn(sh, escape, cmd, args, env):
    if env:
        s = 'env -i '
        for key in env.keys():
            s = s + '%s=%s '%(key, escape(env[key]))
        s = s + sh + ' -c '
        s = s + escape(string.join(args))
    else:
        s = string.join(args)

    return os.system(s) >> 8

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
        ret = stat >> 8
        return ret
            
def generate(env):

    # If the env command exists, then we can use os.system()
    # to spawn commands, otherwise we fall back on os.fork()/os.exec().
    # os.system() is prefered because it seems to work better with
    # threads (i.e. -j) and is more efficient than forking Python.
    if env.Detect('env'):
        spawn = env_spawn
    else:
        spawn = fork_spawn

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
    env['SPAWN']          = spawn
    env['SHELL']          = 'sh'
    env['ESCAPE']         = escape
