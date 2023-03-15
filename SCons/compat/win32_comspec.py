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
Windows COMSPEC command interpreter configuration.
"""

import sys
import os
import textwrap
from collections import namedtuple

__all__ = [
    'windows_comspec_warning_message',
]


if sys.platform == 'win32':

    try:
        import winreg
    except ImportError:
        winreg = None

    class _WindowsCommandInterpreter:

        force_comspec_evar = 'SCONS_WIN32_COMSPEC_FORCE'

        # accepted values (case-insensitive) for evar value
        _EVAR_LCASE_TRUE = ('true', 't', 'yes', 'y', '1')
        _EVAR_LCASE_FALSE = ('false', 'f', 'no', 'n', '0')

        # internal debugging/testing
        _use_registry = True
        _use_systemroot = True
        _use_systempath = True

        # registry config for systemroot and command interpreter
        _CMD_EXECUTABLE_REGISTRY = [
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
        _CMD_EXECUTABLE_ENVIRONMENT = [
            t[-2:]
            for t in _CMD_EXECUTABLE_REGISTRY
        ]

        # last element of environment config for executable basename
        _CMD_EXECUTABLE_BASENAME = [
            os.path.splitext(t[-1])[0]
            for t in _CMD_EXECUTABLE_ENVIRONMENT
        ]

        WindowsComspecValue = namedtuple("WindowsComspecValue", [
            "is_comspec",    # is expected command interpreter (cmd.exe or command.com)
            "norm_comspec",  # normalized comspec for comparison
            "orig_comspec",  # original comspec (extension case may not be preserved)
        ])

        WindowsComspecContext = namedtuple("WindowsComspecContext", [
            "env_comspec",   # environment command interpreter
            "cmd_comspec",   # windows command interpreter
            "env_force",     # scons force os.environ value
            "is_force",      # force os.environ['COMSPEC'] enabled
            "is_user",       # user specified (True) or default (False)
            "is_installed",  # set os.environ['COMSPEC']
        ])

        @classmethod
        def _inspect_registry_systemroot(cls):

            system_root = None
            cmd_interpreter = None

            if winreg:
                for subkey, valname, subpath, cmdexec in cls._CMD_EXECUTABLE_REGISTRY:
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

            return system_root, cmd_interpreter

        @classmethod
        def _inspect_environ_systemroot(cls, system_root):

            cmd_interpreter = None

            if not system_root:
                sysroot = os.environ.get('SystemRoot', r'C:\WINDOWS')
                if os.path.exists(sysroot):
                    system_root = sysroot

            if system_root:
                for subpath, cmdexec in cls._CMD_EXECUTABLE_ENVIRONMENT:
                    cmdexe = os.path.join(system_root, subpath, cmdexec)
                    if os.path.exists(cmdexe) and cls._use_systemroot:
                        cmd_interpreter = cmdexe
                        return system_root, cmd_interpreter

            return system_root, cmd_interpreter

        @classmethod
        def _inspect_environ_systempath(cls):

            cmd_interpreter = None

            env_path = os.environ.get('PATH', '')
            env_path_list = env_path.split(os.pathsep)

            env_pathext = os.environ.get('PATHEXT', '.com;.exe;.bat;.cmd').lower()
            env_pathext_list = env_pathext.split(os.pathsep)

            for syspath in env_path_list:
                for ext in env_pathext_list:
                    for basename in cls._CMD_EXECUTABLE_BASENAME:
                        cmdexe = os.path.join(syspath, basename + ext)
                        if os.path.exists(cmdexe) and cls._use_systempath:
                            cmd_interpreter = cmdexe
                            return cmd_interpreter

            return cmd_interpreter

        @classmethod
        def _find_command_interpreter(cls):
            system_root, cmd_interpreter = cls._inspect_registry_systemroot()
            if cmd_interpreter:
                return cmd_interpreter
            system_root, cmd_interpreter = cls._inspect_environ_systemroot(system_root)
            if cmd_interpreter:
                return cmd_interpreter
            cmd_interpreter = cls._inspect_environ_systempath()
            if cmd_interpreter:
                return cmd_interpreter
            return None

        @classmethod
        def _iscomspec(cls, comspec):
            if comspec and os.path.exists(comspec):
                _, tail = os.path.split(comspec)
                base, _ = os.path.splitext(tail)
                if base.lower() in cls._CMD_EXECUTABLE_BASENAME:
                    return True
            return False

        @classmethod
        def _construct_comspec(cls, comspec):
            if comspec:
                norm_comspec = os.path.normcase(os.path.normpath(comspec))
                is_comspec = cls._iscomspec(norm_comspec)
            else:
                norm_comspec = comspec
                is_comspec = False
            rval = cls.WindowsComspecValue(
                is_comspec=is_comspec,
                norm_comspec=norm_comspec,
                orig_comspec=comspec
            )
            return rval

        @classmethod
        def _get_environ_comspec(cls):
            comspec = os.environ.get('COMSPEC', '')
            return cls._construct_comspec(comspec)

        @classmethod
        def _get_command_interpreter(cls):
            cmd_interpreter = cls._find_command_interpreter()
            return cls._construct_comspec(cmd_interpreter)

        @classmethod
        def _get_environ_force_comspec(cls):
            orig_val = os.environ.get(cls.force_comspec_evar)
            val = orig_val.lower() if orig_val else ''
            if val:
                if val in cls._EVAR_LCASE_TRUE:
                    # is_force=True, is_user=True
                    return True, True, orig_val
                if val in cls._EVAR_LCASE_FALSE:
                    # is_force=False, is_user=True
                    return False, True, orig_val
                # unrecognized symbol
                return False, False, orig_val
            # is_force=default, is_user=False
            return False, False, orig_val

        @classmethod
        def _construct_context(cls):
            env_comspec = cls._get_environ_comspec()
            if env_comspec.is_comspec:
                return None
            cmd_comspec = cls._get_command_interpreter()
            is_force, is_user, env_force = cls._get_environ_force_comspec()
            if cmd_comspec and cmd_comspec.is_comspec and is_force:
                os.environ['COMSPEC'] = cmd_comspec.orig_comspec
                is_installed = True
            else:
                is_installed = False
            rval = cls.WindowsComspecContext(
                env_comspec=env_comspec,
                cmd_comspec=cmd_comspec,
                env_force=env_force,
                is_force=is_force,
                is_user=is_user,
                is_installed=is_installed,
            )
            return rval

        @classmethod
        def get_comspec_context(cls):
            """Return windows comspec context tuple or None."""
            context = cls._construct_context()
            return context

        # key = (is_supported, is_force, is_user)
        _warning_message_kind = {
            (True,  True,   True): 0,   # user suppress override (no message)
            (True,  True,  False): -1,  # impossible (internal error)
            (True,  False,  True): -2,  # impossible (internal error)
            (True,  False, False): -3,  # impossible (internal error)
            (False, True,   True): 1,   # user override failed (unsupported: no cmd)
            (False, True,  False): -4,  # impossible (internal error)
            (False, False,  True): 0,   # user suppress unsupported (no message)
            (False, False, False): 2,   # unsupported (unsupported: no cmd or set)
        }

        @classmethod
        def get_comspec_warning(cls, context):
            """Return windows comspec warning message string or None."""

            if not context:
                return None

            key = (context.is_installed, context.is_force, context.is_user)
            kind = cls._warning_message_kind[key]

            if kind == 0:
                return None

            msg = None

            if kind == 1:
                # not is_installed, is_force, is_user

                msg = textwrap.dedent(
                    f""" \
                    Unsupported windows COMSPEC value, build may fail:
                       COMSPEC={context.env_comspec.orig_comspec}
                       {cls.force_comspec_evar}={context.env_force}
                       A valid command interpreter was not found.\
                    """
                )

            elif kind == 2:
                # not is_installed, not is_force, not is_user

                if context.cmd_comspec.is_comspec:
                    # found compatible command interpreter
                    msg = textwrap.dedent(
                        f""" \
                        Unsupported windows COMSPEC value, build may fail:
                           COMSPEC={context.env_comspec.orig_comspec}
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
                           COMSPEC={context.env_comspec.orig_comspec}
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

    _WINDOWS_COMSPEC_CONTEXT = _WindowsCommandInterpreter.get_comspec_context()

    def windows_comspec_warning_message():
        """Return windows comspec warning message string or None."""
        msg = _WindowsCommandInterpreter.get_comspec_warning(_WINDOWS_COMSPEC_CONTEXT)
        return msg

else:

    def windows_comspec_warning_message():
        """Return windows comspec warning message string or None."""
        return None

# print(windows_comspec_warning_message(), file=sys.stderr)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
