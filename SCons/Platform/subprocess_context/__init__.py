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
Subprocess context handler support.
"""

__all__ = [
    'get_handler',
]

import abc
import os
import textwrap
from collections import namedtuple

try:
    import msvcrt  # pylint: disable=unused-import
except ModuleNotFoundError:
    _MSWINDOWS = False
else:
    _MSWINDOWS = True


_subprocess_context_registry = {}

def get_handler(platform):
    """Return context handler for the platform."""
    cls = _subprocess_context_registry.get(platform.lower())
    return cls

class SubprocessContextBase(abc.ABC):
    """Base subprocess context."""

    def __init_subclass__(cls, platforms, **kwargs):
        super().__init_subclass__(**kwargs)
        for platform in platforms:
            _subprocess_context_registry[platform.lower()] = cls

    @classmethod
    @abc.abstractmethod
    def context_create(cls, env=None):
        """Return subprocess context or None."""
        # pylint: disable=unused-argument
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def context_restore(cls, context, env=None):
        """Restore subprocess comspec context."""
        # pylint: disable=unused-argument
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def state_create(cls, env=None):
        """Return subprocess state or None."""
        # pylint: disable=unused-argument
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_warning_message_from_state(cls, state=None):
        """Return subprocess state warning message string or None."""
        # pylint: disable=unused-argument
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_warning_message(cls, env=None):
        """Return subprocess state warning message string or None."""
        # pylint: disable=unused-argument
        raise NotImplementedError

if _MSWINDOWS:

    try:
        import winreg
    except ImportError:
        _WINREG = False
    else:
        _WINREG = True

    _norm_path_cache = {}

    def _normalize_path(orig_path):
        """Normalize path for comparison."""
        norm_path = _norm_path_cache.get(orig_path)
        if norm_path is None:
            norm_path = os.path.normcase(os.path.normpath(orig_path))
            _norm_path_cache[orig_path] = norm_path
            _norm_path_cache[norm_path] = norm_path
        return norm_path

    class _WindowsCommandInterpreter:

        force_comspec_evar = 'SCONS_WIN32_COMSPEC_FORCE'

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

        _WindowsComspecValue = namedtuple("_WindowsComspecValue", [
            "is_comspec",    # is supported command interpreter (cmd.exe or command.com)
            "is_defined",    # is comspec defined
            "norm_comspec",  # normalized comspec for comparison
            "orig_comspec",  # original comspec (extension case may not be preserved)
        ])

        class WindowsComspecValue(_WindowsComspecValue):
            """Windows comspec command interpreter value."""

            _cache = {}

            @classmethod
            def _iscomspec(cls, comspec):
                if comspec and os.path.exists(comspec):
                    _, tail = os.path.split(comspec)
                    base, _ = os.path.splitext(tail)
                    base = base.lower()
                    if base in _WindowsCommandInterpreter.CMD_EXECUTABLE_BASENAME:
                        return True
                return False

            @classmethod
            def factory(cls, comspec):
                """Return a WindowsComspecValue instance."""

                if comspec:
                    orig_comspec = comspec
                else:
                    orig_comspec = ''

                rval = cls._cache.get(orig_comspec)
                if rval:
                    return rval

                if orig_comspec:
                    norm_comspec = _normalize_path(orig_comspec)
                else:
                    norm_comspec = orig_comspec

                if norm_comspec != orig_comspec:
                    rval = cls._cache.get(norm_comspec)
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

                cls._cache[orig_comspec] = rval

                if norm_comspec != orig_comspec:
                    cls._cache[norm_comspec] = rval

                return rval

        WindowsComspecContext = namedtuple("WindowsComspecContext", [
            "win_comspec",   # windows command interpreter
            "os_comspec",    # os.environ['COMSPEC'] command interpreter
            "env_comspec",   # scons ENV['COMSPEC'] command interpreter
        ])

        WindowsComspecState = namedtuple("WindowsComspecState", [
            "win_comspec",    # windows command interpreter
            "os_comspec",     # os.environ['COMSPEC'] command interpreter
            "os_force",       # force os.environ value
            "os_installed",   # os.environ['COMSPEC'] written
            "env_comspec",    # ENV['COMSPEC'] command interpreter
            "env_installed",  # ENV['COMSPEC'] written
            "is_force",       # force comspec enabled
            "is_user",        # user specified (True) or default (False)
        ])

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
                            system_root = sysroot
                            cmdexe = os.path.join(sysroot, subpath, cmdexec)
                            if os.path.exists(cmdexe) and cls._use_registry:
                                cmd_interpreter = cmdexe
                                return system_root, cmd_interpreter
                        except OSError:
                            pass

                cls._get_registry_systemroot_cache = (system_root, cmd_interpreter)

            return system_root, cmd_interpreter

        @classmethod
        def _get_osenviron_systemroot(cls, system_root):

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

        @classmethod
        def _get_osenviron_systempath(cls):

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

        @classmethod
        def _find_command_interpreter(cls):
            system_root, cmd_interpreter = cls._get_registry_systemroot()
            if cmd_interpreter:
                return cmd_interpreter
            system_root, cmd_interpreter = cls._get_osenviron_systemroot(system_root)
            if cmd_interpreter:
                return cmd_interpreter
            cmd_interpreter = cls._get_osenviron_systempath()
            if cmd_interpreter:
                return cmd_interpreter
            return None

        @classmethod
        def _get_osenviron_comspec(cls):
            comspec = os.environ.get('COMSPEC') if cls._use_oscomspec else None
            rval = cls.WindowsComspecValue.factory(comspec)
            return rval

        @classmethod
        def _get_command_interpreter(cls):
            comspec = cls._find_command_interpreter()
            rval = cls.WindowsComspecValue.factory(comspec)
            return rval

        @classmethod
        def _get_sconsenv_comspec(cls, env=None):
            comspec = env.get('COMSPEC') if env and cls._use_envcomspec else None
            rval = cls.WindowsComspecValue.factory(comspec)
            return rval

        @classmethod
        def comspec_context_create(cls, env):
            """Return windows comspec context or None."""

            os_comspec = cls._get_osenviron_comspec()
            if os_comspec.is_comspec:
                # os.environ is a supported command interpreter
                return None

            win_comspec = cls._get_command_interpreter()
            if not win_comspec.is_comspec:
                # could not find a supported command interpreter
                return None

            os.environ['COMSPEC'] = win_comspec.orig_comspec

            env_comspec = cls._get_sconsenv_comspec(env)
            if env_comspec.norm_comspec != win_comspec.norm_comspec:
                if env:
                    env['COMSPEC'] = win_comspec.orig_comspec

            rval = cls.WindowsComspecContext(
                win_comspec=win_comspec,
                os_comspec=os_comspec,
                env_comspec=env_comspec,
            )

            return rval

        @classmethod
        def comspec_context_restore(cls, context, env):
            """Restore windows comspec context."""

            if context:

                os_path = os.environ.get('COMSPEC')
                if os_path:
                    os_norm = _normalize_path(os_path)
                    if os_norm == context.win_comspec.norm_comspec:
                        # os.environ comspec has not changed
                        if not context.os_comspec.is_defined:
                            # remove key if original value is undefined
                            del os.environ['COMSPEC']
                        else:
                            # restore original value
                            os.environ['COMSPEC'] = context.os_comspec.orig_comspec

                if env:
                    env_path = env.get('COMSPEC')
                    if env_path:
                        env_norm = _normalize_path(env_path)
                        if env_norm == context.win_comspec.norm_comspec:
                            # env comspec has not changed
                            if not context.env_comspec.is_defined:
                                # remove key if original value is undefined
                                del env['COMSPEC']
                            else:
                                # restore original value
                                env['COMSPEC'] = context.env_comspec.orig_comspec

        @classmethod
        def _get_osenviron_force_comspec(cls):
            orig_val = os.environ.get(cls.force_comspec_evar, '')
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
        def _construct_state(cls, env=None):

            os_comspec = cls._get_osenviron_comspec()
            if os_comspec.is_comspec:
                return None

            win_comspec = cls._get_command_interpreter()
            env_comspec = cls._get_sconsenv_comspec(env=env)

            is_force, is_user, os_force = cls._get_osenviron_force_comspec()

            if win_comspec.is_comspec and is_force:
                os.environ['COMSPEC'] = win_comspec.orig_comspec
                os_installed = True
            else:
                os_installed = False

            if env_comspec.is_comspec and is_force:
                env['COMSPEC'] = win_comspec.orig_comspec
                env_installed = True
            else:
                env_installed = False

            rval = cls.WindowsComspecState(
                win_comspec=win_comspec,
                os_comspec=os_comspec,
                os_force=os_force,
                os_installed=os_installed,
                env_comspec=env_comspec,
                env_installed=env_installed,
                is_force=is_force,
                is_user=is_user,
            )
            return rval

        @classmethod
        def get_comspec_state(cls, env=None):
            """Return windows comspec state tuple or None."""
            state = cls._construct_state(env=env)
            return state

        # key = (os_installed, is_force, is_user)
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
        def get_comspec_state_warning(cls, state):
            """Return windows comspec warning message string or None."""

            if not state:
                return None

            key = (state.os_installed, state.is_force, state.is_user)
            kind = cls._warning_message_kind[key]

            if kind == 0:
                return None

            msg = None

            if kind == 1:
                # not os_installed, is_force

                os_force = state.os_force if state.os_force else ''

                msg = textwrap.dedent(
                    f""" \
                    Unsupported windows COMSPEC value, build may fail:
                       COMSPEC={state.os_comspec.orig_comspec}
                       {cls.force_comspec_evar}={os_force}
                       A valid command interpreter was not found.\
                    """
                )

            elif kind == 2:
                # not os_installed, not is_force, not is_user

                if state.win_comspec.is_comspec:
                    # found compatible command interpreter
                    msg = textwrap.dedent(
                        f""" \
                        Unsupported windows COMSPEC value, build may fail:
                           COMSPEC={state.os_comspec.orig_comspec}
                           Set this windows environment variable to override COMSPEC:
                              {cls.force_comspec_evar}=1
                           Set this windows environment variable to ignore this warning:
                              {cls.force_comspec_evar}=0\
                        """
                    )
                else:
                    # did not find compatible command interpreter
                    msg = textwrap.dedent(
                        f""" \
                        Unsupported windows COMSPEC value, build may fail:
                           COMSPEC={state.os_comspec.orig_comspec}
                           Set this windows environment variable to override COMSPEC:
                              {cls.force_comspec_evar}=1
                           Set this windows environment variable to ignore this warning:
                              {cls.force_comspec_evar}=0
                           A valid command interpreter was not found.\
                        """
                    )

            else:

                msg = f"Internal error: unhandled windows comspec warning ({kind})."

            return msg


    class SubprocessContextWindows(SubprocessContextBase, platforms=['win32', 'windows', 'msvcrt']):
        """Subprocess context for windows platform."""

        @classmethod
        def context_create(cls, env=None):
            """Return windows subprocess context or None."""
            context = _WindowsCommandInterpreter.comspec_context_create(env)
            return context

        @classmethod
        def context_restore(cls, context, env=None):
            """Restore windows subprocess context."""
            _WindowsCommandInterpreter.comspec_context_restore(context, env)

        @classmethod
        def state_create(cls, env=None):
            """Return windows subprocess state or None."""
            state = _WindowsCommandInterpreter.get_comspec_state(env)
            return state

        @classmethod
        def get_warning_message_from_state(cls, state=None):
            """Return windows subprocess state warning message string or None."""
            msg = _WindowsCommandInterpreter.get_comspec_state_warning(state)
            return msg

        @classmethod
        def get_warning_message(cls, env=None):
            """Return windows subprocess state warning message string or None."""
            state = _WindowsCommandInterpreter.get_comspec_state(env)
            msg = _WindowsCommandInterpreter.get_comspec_state_warning(state)
            return msg

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
