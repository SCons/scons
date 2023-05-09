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

"""
Process and shell context support.
"""

__all__ = [
    'ProcessContext',
    'ShellContext',
]

import os
from collections import namedtuple
import textwrap

try:
    import msvcrt  # pylint: disable=unused-import
except ModuleNotFoundError:
    _MSWINDOWS = False
else:
    _MSWINDOWS = True

class ProcessContextBase:
    """Process context base."""
    # pylint: disable=too-few-public-methods

    @classmethod
    def update_environ(cls):
        """Update process context and return warning message string or None."""
        # pylint: disable=unused-argument
        return None

    @classmethod
    def subprocess_command(cls, cmd):
        """Update and return process subprocess command."""
        return cmd

class ShellContextBase:
    """Shell context base."""
    # pylint: disable=too-few-public-methods

    @classmethod
    def update_env(cls, env):
        """Update shell context and return warning message string or None."""
        # pylint: disable=unused-argument
        return None

ProcessContext = ProcessContextBase
ShellContext = ShellContextBase

if _MSWINDOWS:

    try:
        import winreg
    except ImportError:
        _WINREG = False
    else:
        _WINREG = True

    class _Windows:
        # pylint: disable=too-few-public-methods

        DEFAULT_CMD_INTERPRETER = 'cmd.exe'

        FORCE_COMSPEC_EVAR = 'SCONS_WIN32_COMSPEC_FORCE'

        # accepted values (case-insensitive) for evar value
        EVAR_LCASE_TRUE = ('true', 't', 'yes', 'y', '1')
        EVAR_LCASE_FALSE = ('false', 'f', 'no', 'n', '0')

        # registry config for systemroot and command interpreter
        CMD_EXECUTABLE_REGISTRY = [
            # cmd.exe (Windows NT)
            (
                r'Software\Microsoft\Windows NT\CurrentVersion',
                'SystemRoot',
                'System32',
                'cmd.exe'
            ),
            # command.com (Windows 95/98/ME)
            (
                r'Software\Microsoft\Windows\CurrentVersion',
                'SystemRoot',
                '',
                'command.com'
            ),
        ]

        # last two elements of registry config for environment config
        CMD_EXECUTABLE_ENVIRONMENT = [
            t[-2:]
            for t in CMD_EXECUTABLE_REGISTRY
        ]

        # last element of environment config for executable basename
        CMD_EXECUTABLE_BASENAME = [
            os.path.splitext(t[-1])[0]
            for t in CMD_EXECUTABLE_ENVIRONMENT
        ]

        # internal debugging/testing
        _use_registry = True
        _use_systemroot = True
        _use_systempath = True
        _use_oscomspec = True
        _use_envcomspec = True

        # query registry for SystemRoot and command interpreter

        _get_registry_systemroot_cache = None

        @classmethod
        def _get_registry_systemroot(cls):

            if cls._get_registry_systemroot_cache is not None:

                system_root, cmd_interpreter = cls._get_registry_systemroot_cache

            else:

                system_root = None
                cmd_interpreter = None

                if _WINREG:
                    for cmdreg_t in cls.CMD_EXECUTABLE_REGISTRY:
                        subkey, valname, subpath, cmdexec = cmdreg_t
                        try:
                            winkey = winreg.OpenKeyEx(
                                winreg.HKEY_LOCAL_MACHINE, subkey
                            )
                            sysroot, _ = winreg.QueryValueEx(winkey, valname)
                            if not os.path.exists(sysroot):
                                continue
                            cmdexe = os.path.join(sysroot, subpath, cmdexec)
                            if os.path.exists(cmdexe) and cls._use_registry:
                                system_root = sysroot
                                cmd_interpreter = cmdexe
                                break
                        except OSError:
                            pass

                cls._get_registry_systemroot_cache = (system_root, cmd_interpreter)

            return system_root, cmd_interpreter

        # query os.environ for SystemRoot and command interpreter

        @classmethod
        def _get_process_systemroot(cls, system_root):

            cmd_interpreter = None

            if not system_root:
                sysroot = os.environ.get('SystemRoot', r'C:\WINDOWS')
                if os.path.exists(sysroot):
                    system_root = sysroot

            if system_root:
                for subpath, cmdexec in cls.CMD_EXECUTABLE_ENVIRONMENT:
                    cmdexe = os.path.join(system_root, subpath, cmdexec)
                    if os.path.exists(cmdexe) and cls._use_systemroot:
                        cmd_interpreter = cmdexe
                        return system_root, cmd_interpreter

            return system_root, cmd_interpreter

        # query system PATH for command interpreter

        @classmethod
        def _get_process_systempath(cls):

            cmd_interpreter = None

            env_path = os.environ.get('PATH', '')
            env_path_list = env_path.split(os.pathsep)

            env_pathext = os.environ.get('PATHEXT', '.com;.exe;.bat;.cmd').lower()
            env_pathext_list = env_pathext.split(os.pathsep)

            for syspath in env_path_list:
                for ext in env_pathext_list:
                    for basename in cls.CMD_EXECUTABLE_BASENAME:
                        cmdexe = os.path.join(syspath, basename + ext)
                        if os.path.exists(cmdexe) and cls._use_systempath:
                            cmd_interpreter = cmdexe
                            return cmd_interpreter

            return cmd_interpreter

        # find supported command interpreter

        @classmethod
        def _find_command_interpreter(cls):
            system_root, cmd_interpreter = cls._get_registry_systemroot()
            if cmd_interpreter:
                return cmd_interpreter
            system_root, cmd_interpreter = cls._get_process_systemroot(system_root)
            if cmd_interpreter:
                return cmd_interpreter
            cmd_interpreter = cls._get_process_systempath()
            if cmd_interpreter:
                return cmd_interpreter
            return None

        # normalize paths for comparison purposes

        _normalize_path_cache = {}

        @classmethod
        def normalize_path(cls, orig_path):
            """Normalize path for comparison."""
            norm_path = cls._normalize_path_cache.get(orig_path)
            if norm_path is None:
                norm_path = os.path.normcase(os.path.normpath(orig_path))
                cls._normalize_path_cache[orig_path] = norm_path
                cls._normalize_path_cache[norm_path] = norm_path
            return norm_path

        # processed windows COMSPEC data structure

        _WindowsComspecValue = namedtuple("_WindowsComspecValue", [
            "is_comspec",    # is supported command interpreter (cmd.exe or command.com)
            "is_defined",    # is comspec defined
            "norm_comspec",  # normalized comspec for comparison
            "orig_comspec",  # original comspec (extension case may not be preserved)
        ])

        class WindowsComspecValue(_WindowsComspecValue):
            """Windows comspec command interpreter value."""

            _windows_comspec_cache = {}

            @classmethod
            def _iscomspec(cls, comspec):
                if comspec and os.path.exists(comspec):
                    _, tail = os.path.split(comspec)
                    base, _ = os.path.splitext(tail)
                    base = base.lower()
                    if base in _Windows.CMD_EXECUTABLE_BASENAME:
                        return True
                return False

            @classmethod
            def factory(cls, comspec):
                """Return a WindowsComspecValue instance."""

                if comspec:
                    orig_comspec = comspec
                else:
                    orig_comspec = ''

                rval = cls._windows_comspec_cache.get(orig_comspec)
                if rval:
                    return rval

                if orig_comspec:
                    norm_comspec = _Windows.normalize_path(orig_comspec)
                else:
                    norm_comspec = orig_comspec

                if norm_comspec != orig_comspec:
                    rval = cls._windows_comspec_cache.get(norm_comspec)
                    if rval:
                        return rval

                is_comspec = cls._iscomspec(norm_comspec)
                is_defined = bool(orig_comspec)

                rval = cls(
                    is_comspec=is_comspec,
                    is_defined=is_defined,
                    norm_comspec=norm_comspec,
                    orig_comspec=orig_comspec,
                )

                cls._windows_comspec_cache[orig_comspec] = rval

                if norm_comspec != orig_comspec:
                    cls._windows_comspec_cache[norm_comspec] = rval

                return rval

        @classmethod
        def get_windows_comspec(cls):
            """Return windows command interpreter."""
            comspec = cls._find_command_interpreter()
            rval = cls.WindowsComspecValue.factory(comspec)
            return rval

        @classmethod
        def get_process_comspec(cls):
            """Return process command interpreter."""
            comspec = os.environ.get('COMSPEC') if cls._use_oscomspec else None
            rval = cls.WindowsComspecValue.factory(comspec)
            return rval

        @classmethod
        def get_shell_comspec(cls, env=None):
            """Return environment command interpreter."""
            comspec = env.get('COMSPEC') if env and cls._use_envcomspec else None
            rval = cls.WindowsComspecValue.factory(comspec)
            return rval

        @classmethod
        def get_process_force_comspec(cls):
            """Return force process command interpreter configuration."""
            orig_val = os.environ.get(_Windows.FORCE_COMSPEC_EVAR, '')
            val = orig_val.lower() if orig_val else ''
            if val:
                if val in cls.EVAR_LCASE_TRUE:
                    # is_force=True, is_user=True
                    return True, True, orig_val
                if val in cls.EVAR_LCASE_FALSE:
                    # is_force=False, is_user=True
                    return False, True, orig_val
                # unrecognized symbol
            # is_force=default, is_user=False
            return False, False, orig_val

        @classmethod
        def get_command_interpreter(cls):
            """Return windows command interpreter."""
            win_comspec = cls.get_windows_comspec()
            if win_comspec.is_comspec:
                cmd_interpreter = win_comspec.orig_comspec
            else:
                cmd_interpreter = cls.DEFAULT_CMD_INTERPRETER
            return cmd_interpreter

    class WindowsProcessContext(ProcessContextBase):
        """Windows process context."""
        # pylint: disable=too-few-public-methods

        WindowsProcessState = namedtuple("WindowsProcessState", [
            "windows_comspec",    # windows command interpreter
            "process_comspec",    # os.environ['COMSPEC'] command interpreter
            "process_force",      # force os.environ['COMSPEC'] value
            "process_installed",  # os.environ['COMSPEC'] written
            "is_force",           # force comspec enabled
            "is_user",            # user specified (True) or default (False)
        ])

        @classmethod
        def _get_process_state(cls):

            process_comspec = _Windows.get_process_comspec()
            if process_comspec.is_comspec:
                return None

            windows_comspec = _Windows.get_windows_comspec()

            is_force, is_user, process_force = _Windows.get_process_force_comspec()

            if windows_comspec.is_comspec and is_force:
                os.environ['COMSPEC'] = windows_comspec.orig_comspec
                process_installed = True
            else:
                process_installed = False

            rval = cls.WindowsProcessState(
                windows_comspec=windows_comspec,
                process_comspec=process_comspec,
                process_force=process_force,
                process_installed=process_installed,
                is_force=is_force,
                is_user=is_user,
            )
            return rval

        # key = (process_installed, is_force, is_user)
        _warning_message_kind = {

            (True,  True,   True): 0,   # user override (no message)
            (True,  True,  False): 0,   # default override (no message)
            (False, True,   True): 1,   # user override failed (unsupported: no cmd)
            (False, True,  False): 1,   # default override failed (unsupported: no cmd)

            (True,  False,  True): -1,  # impossible (internal error)
            (True,  False, False): -2,  # impossible (internal error)
            (False, False,  True): 0,   # user suppress unsupported (no message)
            (False, False, False): 2,   # unsupported (unsupported: no cmd or set)

        }

        @classmethod
        def _get_process_state_warning(cls, state):

            if not state:
                return None

            key = (state.process_installed, state.is_force, state.is_user)
            kind = cls._warning_message_kind[key]

            if kind == 0:
                return None

            msg = None

            if kind == 1:
                # not process_installed, is_force

                process_force = state.process_force if state.process_force else ''

                msg = textwrap.dedent(
                    f""" \
                    Unsupported windows COMSPEC value, build may fail:
                       COMSPEC={state.process_comspec.orig_comspec}
                       {_Windows.FORCE_COMSPEC_EVAR}={process_force}
                       A valid command interpreter was not found.\
                    """
                )

            elif kind == 2:
                # not process_installed, not is_force, not is_user

                if state.windows_comspec.is_comspec:
                    # found compatible command interpreter
                    msg = textwrap.dedent(
                        f""" \
                        Unsupported windows COMSPEC value, build may fail:
                           COMSPEC={state.process_comspec.orig_comspec}
                           Set this windows environment variable to override COMSPEC:
                              {_Windows.FORCE_COMSPEC_EVAR}=1
                           Set this windows environment variable to ignore this warning:
                              {_Windows.FORCE_COMSPEC_EVAR}=0\
                        """
                    )
                else:
                    # did not find compatible command interpreter
                    msg = textwrap.dedent(
                        f""" \
                        Unsupported windows COMSPEC value, build may fail:
                           COMSPEC={state.process_comspec.orig_comspec}
                           Set this windows environment variable to override COMSPEC:
                              {_Windows.FORCE_COMSPEC_EVAR}=1
                           Set this windows environment variable to ignore this warning:
                              {_Windows.FORCE_COMSPEC_EVAR}=0
                           A valid command interpreter was not found.\
                        """
                    )

            else:

                msg = f"Internal error: unhandled windows comspec warning ({kind})."

            return msg

        @classmethod
        def update_environ(cls):
            """Update windows process context and return warning message string or None."""
            state = cls._get_process_state()
            message = cls._get_process_state_warning(state)
            return message

        @classmethod
        def subprocess_command(cls, cmd):
            """Update and return windows subprocess command."""
            cmd_prefix = ['"' + _Windows.get_command_interpreter() + '"', '/c']
            if cmd is None:
                new_cmd = ' '.join(cmd_prefix)
            elif isinstance(cmd, str):
                new_cmd = ' '.join(cmd_prefix) + ' ' + cmd
            else:
                # TODO: assuming type that can be converted to a list
                new_cmd = cmd_prefix + list(cmd)
            return new_cmd

    class WindowsShellContext(ShellContextBase):
        """Windows shell context."""
        # pylint: disable=too-few-public-methods

        WindowsShellState = namedtuple("WindowsShellState", [
            "windows_comspec",  # windows command interpreter
            "shell_comspec",    # env['COMSPEC'] command interpreter
            "shell_installed",  # env['COMSPEC'] written
        ])

        @classmethod
        def _get_shell_state(cls, env):

            shell_comspec = _Windows.get_shell_comspec(env)
            if shell_comspec.is_comspec:
                return None

            windows_comspec = _Windows.get_windows_comspec()

            if windows_comspec.is_comspec:
                env['COMSPEC'] = windows_comspec.orig_comspec
                shell_installed = True
            else:
                shell_installed = False

            rval = cls.WindowsShellState(
                windows_comspec=windows_comspec,
                shell_comspec=shell_comspec,
                shell_installed=shell_installed,
            )
            return rval

        @classmethod
        def _get_shell_state_warning(cls, state):

            if not state:
                # shell comspec is supported
                return None

            if state.shell_installed:
                # installed supported shell comspec
                return None

            msg = textwrap.dedent(
                f""" \
                Unsupported shell COMSPEC value, build may fail:
                   COMSPEC={state.shell_comspec.orig_comspec}
                   A valid command interpreter was not found.\
                """
            )

            return msg

        @classmethod
        def update_env(cls, env):
            """Update windows shell context and return warning message string or None."""
            state = cls._get_shell_state(env)
            message = cls._get_shell_state_warning(state)
            return message

    ProcessContext = WindowsProcessContext
    ShellContext = WindowsShellContext

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
