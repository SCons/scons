# MIT License
#
# Copyright The SCons Foundation
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

"""Platform-specific initialization for POSIX (Linux, UNIX, etc.) systems.

There normally shouldn't be any need to import this module directly.  It
will usually be imported through the generic SCons.Platform.Platform()
selection method.
"""

from __future__ import annotations

import platform
import subprocess
from collections.abc import Callable
from shlex import quote as escape

from SCons.Platform import TempFileMunge
from SCons.Platform.virtualenv import ImportVirtualenv
from SCons.Platform.virtualenv import ignore_virtualenv, enable_virtualenv

exitvalmap = {
    2 : 127,
    13 : 126,
}

def old_escape(arg: str) -> str:
    """Escapes shell special characters.

    This is the default escape function stored in ``env["ESCAPE"]`` for
    the posix platform, which, if not overridden, is passed to
    :func:`~SCons.Subst.escape_list` just before a command is spawned,
    as well to the actual spawner function (as defined by ``env["SPAWN"]``).

    TODO: we're trying to use shlex.quote as the escape function instead.
      Leave this function around (renamed) until we prove the replacement is valid.
    """
    slash = '\\'
    special = '"$'

    arg = arg.replace(slash, slash+slash)
    for c in special:
        arg = arg.replace(c, slash+c)

    # print("ESCAPE RESULT: %s" % arg)
    return '"' + arg + '"'


def spawn(
    sh: str,
    escape: Callable[[str], str],
    cmd: str,
    args: list[str],
    env: dict,
) -> int:
    """Run command line *args* using shell *sh*.

    Arguments:
      sh: the name of the command to use as the shell
      escape: a function to quote the produced command line. Ignored.
      cmd: conventionally, the name of the command, usually taken from
        the first item of *args*, but since the command is actually a
        shell, is ignored.
      args: the argument list representing the command to execute
      env: the execution environment for the command.

    Returns:
      the exit code of the command. :py:mod:`subprocess` is explicitly
      instructed not to raise an exception if the command fails.
    """
    cmdargs = [sh, '-c', ' '.join(args)]
    proc = subprocess.run(cmdargs, env=env, close_fds=True, check=False)
    return proc.returncode


def piped_spawn(
    sh: str,
    escape: Callable[[str], str],
    cmd: str,
    args: list[str],
    env: dict,
    stdout,  # : Scons.Util.Unbuffered
    stderr,  # : Scons.Util.Unbuffered
) -> int:
    """Run command line *args* using shell *sh*, capturing output.

    Similar to :func:`spawn`, but captures output - this is used by
    the SConf subsystem when running compile/configure checks, where
    we specifically need the result data. This ends up handled by
    a wrapper method :meth:`~SCons.SConf.SConfBase.pspawn_wrapper`.

    Arguments:
      sh: the name of the command to use as the shell
      escape: a function to quote the produced command line. Ignored.
      cmd: conventionally, the name of the command, usually taken from
        the first item of *args*, but since the command is actually a
        shell, is ignored.
      args: the argument list representing the command to execute
      env: the execution environment for the command.
      stdout: the place to send the output
      stderr: the place to send the error output

    Returns:
      the exit code of the command. :py:mod:`subprocess` is explicitly
      instructed not to raise an exception if the command fails.
    """
    cmdargs = [sh, '-c', ' '.join(args)]
    proc = subprocess.run(
        cmdargs, env=env, close_fds=True, stdout=stdout, stderr=stderr, check=False
    )
    return proc.returncode


def generate(env) -> None:
    if 'ENV' not in env:
        env['ENV']        = {}
    env['ENV']['PATH']    = '/usr/local/bin:/opt/bin:/bin:/usr/bin:/snap/bin'
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
    env['LIBPREFIXES']    = ['$LIBPREFIX']
    env['LIBSUFFIXES']    = ['$LIBSUFFIX', '$SHLIBSUFFIX']
    env['LIBLITERALPREFIX'] = ''
    env['HOST_OS']        = 'posix'
    env['HOST_ARCH']      = platform.machine()
    env['PSPAWN']         = piped_spawn
    env['SPAWN']          = spawn
    env['SHELL']          = 'sh'
    env['ESCAPE']         = escape
    env['TEMPFILE']       = TempFileMunge
    env['TEMPFILEPREFIX'] = '@'
    #Based on LINUX: ARG_MAX=ARG_MAX=131072 - 3000 for environment expansion
    #Note: specific platforms might rise or lower this value
    env['MAXLINELENGTH']  = 128072

    # This platform supports RPATH specifications.
    env['__RPATH'] = '$_RPATH'

    # GDC is GCC family, but DMD and LDC have different options.
    # Must be able to have GCC and DMD work in the same build, so:
    env['__DRPATH'] = '$_DRPATH'

    if enable_virtualenv and not ignore_virtualenv:
        ImportVirtualenv(env)
