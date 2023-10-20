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
Command-line options for Microsoft Visual C/C++.
"""

import argparse
import os
import shlex

from collections import namedtuple

import SCons.Script

from ..common import (
    debug,
    debug_extra,
)

from . import Util

from .Exceptions import (
    MSVCInternalError,
    MSVCArgumentError,
)

from . import Dispatcher
Dispatcher.register_modulename(__name__)


MSVC_OPTIONS_EVAR = 'SCONS_MSVC_OPTIONS'

class MSVCOptionsParser(argparse.ArgumentParser, Util.AutoInitialize):

    debug_extra = None

    def __init__(self, *, environ_var, environ_val):
        super().__init__()
        self.debug_extra = debug_extra(self.__class__)
        self._environ_var = environ_var
        self._environ_val = environ_val
        self._environ_args = shlex.split(environ_val, posix=False)
        self.prog = f'{self.__class__.__name__}'
        debug('environ_args=%s', repr(self._environ_args), extra=self.debug_extra)

    def error(self, message) -> None:
        debug(
            'MSVCArgumentError: message=%s',
            repr(message), extra=self.debug_extra
        )
        errmsg = f'{self._environ_var} {message}\n  {self._environ_var}={self._environ_val}'
        raise MSVCArgumentError(errmsg)

    def exit(self, status=0, message=None) -> None:
        message = message.rstrip('\n')
        debug(
            'MSVCInternalError: status=%d, message=%s',
            status, repr(message), extra=self.debug_extra
        )
        raise MSVCInternalError(message)

    def parse_args(self) -> None:
        args = super().parse_args(self._environ_args)
        debug('args=%s', repr(args), extra=self.debug_extra)
        return args

class _Options(Util.AutoInitialize):

    debug_extra = None

    options_environ = None
    options_enabled = False

    _Option = namedtuple('Option', [
        'option',
        'dest',
        'default',
        'action',
        'help',
        'metavar',
        'type',
        'type_scons',
    ])

    msvs_channel_opt = _Option(
        option='--msvs-channel',
        dest='msvs_channel',
        default=None,
        type=str,
        type_scons='string',
        action='store',
        help='Set default msvs CHANNEL [Release, Preview, Any].',
        metavar='CHANNEL',
    )

    msvs_channel_val = msvs_channel_opt.default

    vswhere_opt = _Option(
        option='--vswhere',
        dest='vswhere',
        default=None,
        type=str,
        type_scons='string',
        action='store',
        help='Add vswhere executable located at EXEPATH.',
        metavar='EXEPATH',
    )

    vswhere_val = vswhere_opt.default

    @classmethod
    def _options_enabled(cls) -> bool:

        val = os.environ.get(MSVC_OPTIONS_EVAR)
        if val:
            val = val.strip()

        if val:
            cls.options_environ = val
            cls.options_enabled = True

        debug(
            'options_enabled=%s, options_environ=%s',
            cls.options_enabled, repr(cls.options_environ), extra=cls.debug_extra
        )

        return cls.options_enabled

    @classmethod
    def _options_parser(cls) -> None:

        parser = MSVCOptionsParser(
            environ_var=MSVC_OPTIONS_EVAR,
            environ_val=cls.options_environ,
        )

        parser.add_argument(
            cls.msvs_channel_opt.option,
            dest=cls.msvs_channel_opt.dest,
            default=cls.msvs_channel_opt.default,
            type=cls.msvs_channel_opt.type,
            action=cls.msvs_channel_opt.action,
            help=cls.msvs_channel_opt.help,
            metavar=cls.msvs_channel_opt.metavar,
        )

        parser.add_argument(
            cls.vswhere_opt.option,
            dest=cls.vswhere_opt.dest,
            default=cls.vswhere_opt.default,
            type=cls.vswhere_opt.type,
            action=cls.vswhere_opt.action,
            help=cls.vswhere_opt.help,
            metavar=cls.vswhere_opt.metavar,
        )

        args = parser.parse_args()

        msvs_channel_val = getattr(args, cls.msvs_channel_opt.dest)
        if msvs_channel_val:
            cls.msvs_channel_val = msvs_channel_val
            debug('msvs_channel=%s', repr(cls.msvs_channel_val), extra=cls.debug_extra)

        vswhere_val = getattr(args, cls.vswhere_opt.dest)
        if vswhere_val:
            cls.vswhere_val = vswhere_val
            debug('vswhere=%s', repr(cls.vswhere_val), extra=cls.debug_extra)

    @classmethod
    def _options_cmdline(cls) -> None:

        SCons.Script.AddOption(
            cls.msvs_channel_opt.option,
            dest=cls.msvs_channel_opt.dest,
            default=cls.msvs_channel_opt.default,
            type=cls.msvs_channel_opt.type_scons,
            action=cls.msvs_channel_opt.action,
            help=cls.msvs_channel_opt.help,
            metavar=cls.msvs_channel_opt.metavar,
            nargs=1,
        )

        SCons.Script.AddOption(
            cls.vswhere_opt.option,
            dest=cls.vswhere_opt.dest,
            default=cls.vswhere_opt.default,
            type=cls.vswhere_opt.type_scons,
            action=cls.vswhere_opt.action,
            help=cls.vswhere_opt.help,
            metavar=cls.vswhere_opt.metavar,
            nargs=1,
        )

        msvs_channel_val = SCons.Script.GetOption(cls.msvs_channel_opt.dest)
        if msvs_channel_val:
            cls.msvs_channel_val = msvs_channel_val
            debug('msvs_channel=%s', repr(cls.msvs_channel_val), extra=cls.debug_extra)

        vswhere_val = SCons.Script.GetOption(cls.vswhere_opt.dest)
        if vswhere_val:
            cls.vswhere_val = vswhere_val
            debug('vswhere=%s', repr(cls.vswhere_val), extra=cls.debug_extra)

    @classmethod
    def _options_finalize(cls) -> None:
        debug('msvs_channel=%s', repr(cls.msvs_channel_val), extra=cls.debug_extra)
        debug('vswhere=%s', repr(cls.vswhere_val), extra=cls.debug_extra)

    @classmethod
    def _initialize(cls) -> None:

        cls.debug_extra = debug_extra(cls)

        if cls._options_enabled():
            cls._options_parser()

        cls._options_cmdline()
        cls._options_finalize()

def msvs_channel():
    return _Options.msvs_channel_val, _Options.msvs_channel_opt.option

def vswhere():
    return _Options.vswhere_val, _Options.vswhere_opt.option
