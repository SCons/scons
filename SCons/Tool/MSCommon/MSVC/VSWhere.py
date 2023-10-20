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
VSWhere executable locations for Microsoft Visual C/C++.
"""

import os
from collections import namedtuple

import SCons.Util

from ..common import (
    debug,
    debug_extra,
)

from . import Config
from . import Util
from . import Options
from . import Warnings

from . import Dispatcher
Dispatcher.register_modulename(__name__)

# priority: env > cmdline > environ > (user, initial, user)

VSWHERE_EXE = 'vswhere.exe'

VSWHERE_PATHS = [
    os.path.join(p, VSWHERE_EXE)
    for p in [
        # For bug 3333: support default location of vswhere for both
        # 64 and 32 bit windows installs.
        # For bug 3542: also accommodate not being on C: drive.
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft Visual Studio\Installer"),
        os.path.expandvars(r"%ChocolateyInstall%\bin"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
        os.path.expanduser(r"~\scoop\shims"),
        os.path.expandvars(r"%SCOOP%\shims"),
    ]
    if not p.startswith('%')
]

class _VSWhere(Util.AutoInitialize):

    # TODO(JCB): review reset

    VSWhereExecutable = namedtuple('VSWhereExecutable', [
        'path',
        'norm',
    ])

    debug_extra = None

    vswhere_cmdline = None
    vswhere_executables = []

    _cache_user_vswhere_paths = {}

    @classmethod
    def _cmdline(cls) -> None:
        vswhere, option = Options.vswhere()
        if vswhere:
            vswhere_exec = cls.user_path(vswhere, option)
            if vswhere_exec:
                cls.vswhere_cmdline = vswhere_exec
        debug('vswhere_cmdline=%s', cls.vswhere_cmdline, extra=cls.debug_extra)

    @classmethod
    def _setup(cls) -> None:
        for pval in VSWHERE_PATHS:
            if not os.path.exists(pval):
                continue
            vswhere_exec = cls.VSWhereExecutable(path=pval, norm=Util.normalize_path(pval))
            cls.vswhere_executables.append(vswhere_exec)
        debug('vswhere_executables=%s', cls.vswhere_executables, extra=cls.debug_extra)
        cls._cmdline()

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls.reset()
        cls._setup()

    @classmethod
    def reset(cls) -> None:
        cls._cache_user_vswhere_paths = {}

    # validate user-specified vswhere executable

    @classmethod
    def user_path(cls, pval, source):

        rval = cls._cache_user_vswhere_paths.get(pval, Config.UNDEFINED)
        if rval != Config.UNDEFINED:
            debug('vswhere_exec=%s', repr(rval), extra=cls.debug_extra)
            return rval

        vswhere_exec = None
        if pval:

            if not os.path.exists(pval):

                warn_msg = f'vswhere executable path not found: {pval!r} ({source})'
                debug(warn_msg, extra=cls.debug_extra)
                SCons.Warnings.warn(Warnings.VSWherePathWarning, warn_msg)

            else:

                norm = Util.normalize_path(pval)
                tail = os.path.split(norm)[-1]
                if tail != VSWHERE_EXE:

                    warn_msg = f'unsupported vswhere executable (expected {VSWHERE_EXE!r}, found {tail!r}): {pval!r} ({source})'
                    debug(warn_msg, extra=cls.debug_extra)
                    SCons.Warnings.warn(Warnings.VSWherePathWarning, warn_msg)

                else:

                    vswhere_exec = cls.VSWhereExecutable(path=pval, norm=norm)
                    debug('vswhere_exec=%s', repr(vswhere_exec), extra=cls.debug_extra)

        cls._cache_user_vswhere_paths[pval] = vswhere_exec

        return vswhere_exec

    # user-specified vswhere executables

    @classmethod
    def user_pathlist(cls, path_list, front, source) -> None:

        user_executables = []
        for pval in path_list:
            vswhere_exec = cls.user_path(pval, source)
            if vswhere_exec:
                user_executables.append(vswhere_exec)

        if user_executables:

            if front:
                all_executables = user_executables + cls.vswhere_executables
            else:
                all_executables = cls.vswhere_executables + user_executables

            seen = set()
            unique_executables = []
            for vswhere_exec in all_executables:
                if vswhere_exec.norm in seen:
                    continue
                seen.add(vswhere_exec.norm)
                unique_executables.append(vswhere_exec)

            cls.vswhere_executables = unique_executables
            debug('vswhere_executables=%s', cls.vswhere_executables)

# user vswhere executable location(s)

def vswhere_push_location(string_or_list, front=False) -> None:
    # TODO(JCB): need docstring
    path_list = SCons.Util.flatten(string_or_list)
    if path_list:
        _VSWhere.user_pathlist(path_list, front, 'vswhere_push_location')

# all vswhere executables

def vswhere_get_executables(vswhere_env=None):

    vswhere_executables = []

    # env['VSWHERE']=path
    if vswhere_env:
        vswhere_exec = _VSWhere.user_path(vswhere_env, "env['VSWHERE']")
        if vswhere_exec:
            vswhere_executables.append(vswhere_exec)

    # --vswhere=EXEPATH
    if _VSWhere.vswhere_cmdline:
        vswhere_executables.append(_VSWhere.vswhere_cmdline)

    # default paths and user paths (vswhere_push_location)
    if _VSWhere.vswhere_executables:
        vswhere_executables.extend(_VSWhere.vswhere_executables)

    return vswhere_executables

def vswhere_get_executables_env(env=None):
    vswhere_env = Util.env_query(env, 'VSWHERE', subst=True)
    vswhere_executables = vswhere_get_executables(vswhere_env)
    return vswhere_executables

# reset state

def reset() -> None:
    _VSWhere.reset()

