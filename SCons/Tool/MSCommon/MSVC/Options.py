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

import os
from collections import namedtuple

import SCons.Script

from ..common import (
    debug,
    debug_extra,
)

from . import Config
from . import Util

from . import Dispatcher
Dispatcher.register_modulename(__name__)


CMDLINE_OPTIONS_FORCE = False
CMDLINE_OPTIONS_EVAR = 'SCONS_ENABLE_MSVC_OPTIONS'

class _Options(Util.AutoInitialize):

    enabled = CMDLINE_OPTIONS_FORCE

    vswhere_val = None
    vswhere_opt = '--vswhere'
    vswhere_dest = 'vswhere'

    msvs_channel_val = None
    msvs_channel_opt = '--msvs-channel'
    msvs_channel_dest = 'msvs_channel'

    debug_extra = None

    @classmethod
    def _setup(cls) -> None:

        if not cls.enabled:
            val = os.environ.get(CMDLINE_OPTIONS_EVAR)
            cls.enabled = bool(val in Config.BOOLEAN_SYMBOLS[True])

        if cls.enabled:

            SCons.Script.AddOption(
                cls.vswhere_opt,
                nargs=1,
                dest=cls.vswhere_dest,
                default=None,
                type="string",
                action="store",
                help='Add vswhere executable located at EXEPATH.',
                metavar='EXEPATH',
            )

            cls.vswhere_val = SCons.Script.GetOption(cls.vswhere_dest)

            SCons.Script.AddOption(
                cls.msvs_channel_opt,
                nargs=1,
                dest=cls.msvs_channel_dest,
                default=None,
                type="string",
                action="store",
                help='Set default msvs CHANNEL [Release, Preview, Any].',
                metavar='CHANNEL',
            )

            cls.msvs_channel_val = SCons.Script.GetOption(cls.msvs_channel_dest)

        debug(
            'enabled=%s, vswhere=%s, msvs_channel=%s',
            cls.enabled, repr(cls.vswhere_val), repr(cls.msvs_channel_val),
            extra=cls.debug_extra
        )

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls._setup()

def vswhere():
    return _Options.vswhere_val, _Options.vswhere_opt

def msvs_channel():
    return _Options.msvs_channel_val, _Options.msvs_channel_opt
