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
Visual Studio detection for Microsoft Visual C/C++.
"""

import json
import os
import re
import subprocess

from collections import namedtuple
from functools import cmp_to_key

import SCons.Util
import SCons.Warnings

from .. import common

from ..common import (
    debug,
    debug_extra,
    DEBUG_ENABLED,
)

from . import Config
from . import Exceptions
from . import Options
from . import Util
from . import Registry
from . import Validate
from . import VSWhere
from . import Warnings

from . import Dispatcher
Dispatcher.register_modulename(__name__)

# TODO(JCB): temporary

_msvc_instance_check_files_exist = None

def register_msvc_instance_check_files_exist(func):
    global _msvc_instance_check_files_exist
    _msvc_instance_check_files_exist = func

class _VSUtil(Util.AutoInitialize):

    debug_extra = None

    # cached values
    _normalized_path = {}
    _path_exists = {}

    @classmethod
    def reset(cls) -> None:
        cls._normalized_path = {}
        cls._path_exists = {}

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls.reset()

    # normalized paths

    @classmethod
    def normalize_path(cls, pval):
        rval = cls._normalized_path.get(pval, Config.UNDEFINED)
        if rval == Config.UNDEFINED:
            rval = Util.normalize_path(pval)
            cls._normalized_path[pval] = rval
            debug('norm=%s, pval=%s', repr(rval), repr(pval), extra=cls.debug_extra)
        return rval

    # path existence

    @classmethod
    def path_exists(cls, pval):
        rval = cls._path_exists.get(pval, Config.UNDEFINED)
        if rval == Config.UNDEFINED:
            rval = os.path.exists(pval)
            cls._path_exists[pval] = rval
            debug('exists=%s, pval=%s', rval, repr(pval), extra=cls.debug_extra)
        return rval


class _VSConfig:

    # MSVS IDE binaries

    BITFIELD_DEVELOP     = 0b_1000
    BITFIELD_EXPRESS     = 0b_0100
    BITFIELD_EXPRESS_WIN = 0b_0010
    BITFIELD_EXPRESS_WEB = 0b_0001

    EXECUTABLE_MASK = BITFIELD_DEVELOP | BITFIELD_EXPRESS

    VSProgram = namedtuple("VSProgram", [
        'program',
        'bitfield'
    ])

    DEVENV_COM = VSProgram(program='devenv.com', bitfield=BITFIELD_DEVELOP)
    MSDEV_COM = VSProgram(program='msdev.com', bitfield=BITFIELD_DEVELOP)

    WDEXPRESS_EXE = VSProgram(program='WDExpress.exe', bitfield=BITFIELD_EXPRESS)
    VCEXPRESS_EXE = VSProgram(program='VCExpress.exe', bitfield=BITFIELD_EXPRESS)

    VSWINEXPRESS_EXE = VSProgram(program='VSWinExpress.exe', bitfield=BITFIELD_EXPRESS_WIN)
    VWDEXPRESS_EXE = VSProgram(program='VWDExpress.exe', bitfield=BITFIELD_EXPRESS_WEB)

    # MSVS IDE binary

    VSBinaryConfig = namedtuple("VSBinaryConfig", [
        'pathcomp',  # vs root -> ide dir
        'programs',  # ide binaries
    ])

    # MSVS batch file

    VSBatchConfig = namedtuple("VSBatchConfig", [
        'pathcomp',  # vs root -> batch dir
        'script',  # vs script
    ])

    # detect configuration

    DetectConfig = namedtuple("DetectConfig", [
        'vs_cfg',  # vs configuration
        'vc_cfg',  # vc configuration
    ])

    VSDetectConfig = namedtuple("VSDetectConfig", [
        'root',  # relative path vc dir -> vs root
        'vs_binary_cfg',  # vs executable
        'vs_batch_cfg',  # vs batch file
    ])

    VCDetectConfigRegistry = namedtuple("VCDetectConfigRegistry", [
        'regkeys',
    ])

    _VCRegistryKey = namedtuple("_VCRegistryKey", [
        'hkroot',
        'key',
        'is_vsroot',
        'is_vcforpython',
    ])

    class VCRegKey(_VCRegistryKey):

        @classmethod
        def factory(
            cls, *,
            key,
            hkroot=SCons.Util.HKEY_LOCAL_MACHINE,
            is_vsroot=False,
            is_vcforpython=False,
        ):

            regkey = cls(
                hkroot=hkroot,
                key=key,
                is_vsroot=is_vsroot,
                is_vcforpython=is_vcforpython,
            )

            return regkey

    _regkey = VCRegKey.factory

    # vs detect configuration: vswhere

    DETECT_VSWHERE = {

        '2022': DetectConfig(  # 14.3
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='VsDevCmd.bat',
                ),
            ),
            vc_cfg=None,
        ),

        '2019': DetectConfig(  # 14.2
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='VsDevCmd.bat',
                ),
            ),
            vc_cfg=None,
        ),

        '2017': DetectConfig(  # 14.1
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, WDEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='VsDevCmd.bat',
                ),
            ),
            vc_cfg=None,
        ),

    }

    # vs detect configuration: registry

    DETECT_REGISTRY = {

        '2015': DetectConfig(  # 14.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, WDEXPRESS_EXE, VSWINEXPRESS_EXE, VWDEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    # VsDevCmd.bat and vsvars32.bat appear to be different
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\14.0\Setup\VC\ProductDir'),
                    _regkey(key=r'Microsoft\WDExpress\14.0\Setup\VS\ProductDir', is_vsroot=True),
                    _regkey(key=r'Microsoft\VCExpress\14.0\Setup\VC\ProductDir'),  # not populated?
                ],
            ),
        ),

        '2013': DetectConfig(  # 12.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, WDEXPRESS_EXE, VSWINEXPRESS_EXE, VWDEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    # VsDevCmd.bat and vsvars32.bat appear to be different
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\12.0\Setup\VC\ProductDir'),
                    _regkey(key=r'Microsoft\VCExpress\12.0\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '2012': DetectConfig(  # 11.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, WDEXPRESS_EXE, VSWINEXPRESS_EXE, VWDEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    # VsDevCmd.bat and vsvars32.bat appear to be identical
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\11.0\Setup\VC\ProductDir'),
                    _regkey(key=r'Microsoft\VCExpress\11.0\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '2010': DetectConfig(  # 10.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, VCEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\10.0\Setup\VC\ProductDir'),
                    _regkey(key=r'Microsoft\VCExpress\10.0\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '2008': DetectConfig(  # 9.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, VCEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(
                        hkroot=SCons.Util.HKEY_CURRENT_USER,
                        key=r'Microsoft\DevDiv\VCForPython\9.0\InstallDir',
                        is_vsroot=True, is_vcforpython=True,
                    ),
                    _regkey(
                        key=r'Microsoft\DevDiv\VCForPython\9.0\InstallDir',
                        is_vsroot=True, is_vcforpython=True
                    ),
                    _regkey(key=r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir'),
                    _regkey(key=r'Microsoft\VCExpress\9.0\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '2005': DetectConfig(  # 8.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM, VCEXPRESS_EXE],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\8.0\Setup\VC\ProductDir'),
                    _regkey(key=r'Microsoft\VCExpress\8.0\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '2003': DetectConfig(  # 7.1
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='vsvars32.bat',
                ),
            ),
                vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\7.1\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '2002': DetectConfig(  # 7.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common7\IDE',
                    programs=[DEVENV_COM],
                ),
                vs_batch_cfg=VSBatchConfig(
                    pathcomp=r'Common7\Tools',
                    script='vsvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\7.0\Setup\VC\ProductDir'),
                ]
            ),
        ),

        '1998': DetectConfig(  # 6.0
            vs_cfg=VSDetectConfig(
                root=os.pardir,
                vs_binary_cfg=VSBinaryConfig(
                    pathcomp=r'Common\MSDev98\Bin',
                    programs=[MSDEV_COM],
                ),
                vs_batch_cfg=VSBatchConfig(
                    # There is no vsvars32.bat batch file
                    pathcomp=r'VC98\bin',
                    script='vcvars32.bat',
                ),
            ),
            vc_cfg=VCDetectConfigRegistry(
                regkeys=[
                    _regkey(key=r'Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++\ProductDir'),
                ]
            ),
        ),

    }


class _VSChannel(Util.AutoInitialize):

    # TODO(JCB): review reset

    # priority: cmdline > user > initial

    debug_extra = None

    vs_channel_initial = None
    vs_channel_cmdline = None

    # reset

    vs_channel_user = None
    vs_channel_def = None
    vs_channel_retrieved = False

    @classmethod
    def _initial(cls) -> None:
        cls.vs_channel_initial = Config.MSVS_CHANNEL_RELEASE
        cls.vs_channel_def = cls.vs_channel_initial
        debug('vs_channel_initial=%s',
            cls.vs_channel_initial.vs_channel_id,
            extra=cls.debug_extra
        )

    @classmethod
    def _cmdline(cls) -> None:
        channel, option = Options.msvs_channel()
        if channel:
            vs_channel_def = Validate.validate_msvs_channel(
                channel, option
            )
            if vs_channel_def:
                cls.vs_channel_cmdline = vs_channel_def
                cls.vs_channel_def = cls.vs_channel_cmdline
                debug('vs_channel_cmdline=%s',
                    cls.vs_channel_cmdline.vs_channel_id,
                    extra=cls.debug_extra
                )

    @classmethod
    def _setup(cls) -> None:
        cls._initial()
        cls._cmdline()

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls._setup()

    @classmethod
    def reset(cls) -> None:
        cls.vs_channel_user = None
        cls.vs_channel_def = None
        cls.vs_channel_retrieved = False
        cls._setup()

    @classmethod
    def get_default_channel(cls):
        if not cls.vs_channel_retrieved:
            cls.vs_channel_retrieved = True
            if cls.vs_channel_cmdline:
                cls.vs_channel_def = cls.vs_channel_cmdline
            elif cls.vs_channel_user:
                cls.vs_channel_def = cls.vs_channel_user
            else:
                cls.vs_channel_def = cls.vs_channel_initial
        debug(
            'vs_channel=%s',
            cls.vs_channel_def.vs_channel_id,
            extra=cls.debug_extra
        )
        return cls.vs_channel_def

    @classmethod
    def set_default_channel(cls, msvs_channel, source) -> bool:

        rval = False

        if cls.vs_channel_retrieved:

            warn_msg = f'msvs channel {msvs_channel!r} ({source}) ignored: must be set before first use.'
            debug(warn_msg, extra=cls.debug_extra)
            SCons.Warnings.warn(Warnings.MSVSChannelWarning, warn_msg)

        else:

            vs_channel_def = Validate.validate_msvs_channel(msvs_channel, source)
            if vs_channel_def:

                cls.vs_channel_user = vs_channel_def
                debug(
                    'vs_channel_user=%s',
                    cls.vs_channel_user.vs_channel_id,
                    extra=cls.debug_extra
                )

                if not cls.vs_channel_cmdline:
                    # priority: cmdline > user > initial
                    cls.vs_channel_def = cls.vs_channel_user
                    debug(
                        'vs_channel=%s',
                        cls.vs_channel_def.vs_channel_id,
                        extra=cls.debug_extra
                    )
                    rval = True

                debug(
                    'vs_channel=%s',
                    cls.vs_channel_def.vs_channel_id,
                    extra=cls.debug_extra
                )

        return rval

def msvs_set_channel_default(msvs_channel) -> bool:
    """Set the default msvs channel.

    Args:
        msvs_channel: str
            string representing the msvs channel

            Case-insensitive values are:
                Release, Rel, Preview, Pre, Any, *

    Returns:
        bool: True if the default msvs channel was accepted.
              False if the default msvs channel was not accepted.

    """
    rval = _VSChannel.set_default_channel(msvs_channel, 'msvs_set_channel_default')
    return rval

def msvs_get_channel_default():
    """Get the default msvs channel.

    Returns:
        str: default msvs channel

    """
    return _VSChannel.vs_channel_def.vs_channel_id


class _VSKeys(Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)

    # edition key: (product, channel, component/None, seqnbr/None)

    _MSVSEditionKey = namedtuple('_MSVSEditionKey', [
        'vs_product_def',
        'vs_channel_def',
        'vs_componentid_def',
        'vs_sequence_nbr',
    ])

    class MSVSEditionKey(_MSVSEditionKey):

        def serialize(self):
            values = [
                self.vs_product_def.vs_product,
                self.vs_channel_def.vs_channel_suffix,
            ]
            if self.vs_componentid_def:
                values.append(self.vs_componentid_def.vs_component_suffix)
            if self.vs_sequence_nbr:
                values.append(str(self.vs_sequence_nbr))
            rval = '-'.join(values)
            return rval

        @classmethod
        def factory(
            cls, *,
            vs_product_def,
            vs_channel_def,
            vs_componentid_def,
            vs_sequence_nbr,
        ):

            vs_edition_key = cls(
                vs_product_def=vs_product_def,
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
                vs_sequence_nbr=vs_sequence_nbr
            )

            return vs_edition_key

    @classmethod
    def msvs_edition_key(
        cls, *,
        vs_product_def=None,
        vs_channel_def=None,
        vs_componentid_def=None,
        vs_sequence_nbr=None,
    ):

        if not vs_product_def:
            errmsg = 'vs_product_def is undefined'
            debug('MSVCInternalError: %s', errmsg, extra=cls.debug_extra)
            raise Exceptions.MSVCInternalError(errmsg)

        if not vs_channel_def:
            errmsg = 'vs_channel_def is undefined'
            debug('MSVCInternalError: %s', errmsg, extra=cls.debug_extra)
            raise Exceptions.MSVCInternalError(errmsg)

        vs_edition_key = cls.MSVSEditionKey.factory(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
            vs_sequence_nbr=vs_sequence_nbr
        )

        return vs_edition_key

    # channel key: (channel, component/None)

    _MSVSChannelKey = namedtuple('_MSVSChannelKey', [
        'vs_channel_def',
        'vs_componentid_def',
    ])

    class MSVSChannelKey(_MSVSChannelKey):

        def serialize(self):
            values = [
                self.vs_channel_def.vs_channel_suffix,
            ]
            if self.vs_componentid_def:
                values.append(self.vs_componentid_def.vs_component_suffix)
            rval = '-'.join(values)
            return rval

        @classmethod
        def factory(
            cls, *,
            vs_channel_def,
            vs_componentid_def,
        ):

            vs_channel_key = cls(
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
            )

            return vs_channel_key

    @classmethod
    def msvs_channel_key(
        cls, *,
        vs_channel_def=None,
        vs_componentid_def=None,
    ):

        if not vs_channel_def:
            errmsg = 'vs_channel_def is undefined'
            debug('MSVCInternalError: %s', errmsg, extra=cls.debug_extra)
            raise Exceptions.MSVCInternalError(errmsg)

        vs_channel_key = cls.MSVSChannelKey.factory(
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        return vs_channel_key


_MSVSBase = namedtuple('_MSVSBase', [
    'id_str',
    'id_comps',
    'vs_product_def',
    'vs_channel_def',
    'vs_component_def',
    'vs_sequence_nbr',
    'vs_dir',
    'vs_dir_norm',
    'vs_version',
    'is_express',
    'is_buildtools',
    'is_vcforpython',
    'vs_edition_channel_component_seqnbr_key',
    'vs_edition_channel_component_key',
    'vs_edition_channel_key',
    'vs_channel_component_key',
    'vs_channel_key',
    'instance_map',
])

class MSVSBase(_MSVSBase):

    def _is_express(vs_component_def) -> bool:
        vs_componentid_def = vs_component_def.vs_componentid_def
        is_express = bool(vs_componentid_def == Config.MSVS_COMPONENTID_EXPRESS)
        return is_express

    @staticmethod
    def _is_buildtools(vs_component_def) -> bool:
        vs_componentid_def = vs_component_def.vs_componentid_def
        is_buildtools = bool(vs_componentid_def == Config.MSVS_COMPONENTID_BUILDTOOLS)
        return is_buildtools

    @staticmethod
    def _is_vcforpython(vs_component_def) -> bool:
        vs_componentid_def = vs_component_def.vs_componentid_def
        is_vcforpython = bool(vs_componentid_def == Config.MSVS_COMPONENTID_PYTHON)
        return is_vcforpython

    @classmethod
    def factory(
        cls, *,
        vs_product_def,
        vs_channel_def,
        vs_component_def,
        vs_sequence_nbr,
        vs_dir,
        vs_version,
    ):

        vs_componentid_def = vs_component_def.vs_componentid_def

        vs_edition_channel_component_seqnbr_key = _VSKeys.msvs_edition_key(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
            vs_sequence_nbr=vs_sequence_nbr,
        )

        vs_edition_channel_component_key = _VSKeys.msvs_edition_key(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        vs_edition_channel_key = _VSKeys.msvs_edition_key(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
        )

        vs_channel_component_key = _VSKeys.msvs_channel_key(
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        vs_channel_key = _VSKeys.msvs_channel_key(
            vs_channel_def=vs_channel_def,
        )

        instance_map = {
            'msvs_instance': None,
            'msvc_instance': None,
        }

        id_comps = (
            vs_product_def.vs_product,
            vs_channel_def.vs_channel_suffix,
            vs_component_def.vs_componentid_def.vs_component_suffix,
            str(vs_sequence_nbr),
        )

        id_str = '{}({})'.format(cls.__name__, ', '.join(id_comps))

        msvs_base = cls(
            id_str=id_str,
            id_comps=id_comps,
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_component_def=vs_component_def,
            vs_sequence_nbr=vs_sequence_nbr,
            vs_dir=vs_dir,
            vs_dir_norm=_VSUtil.normalize_path(vs_dir),
            vs_version=vs_version,
            is_express=cls._is_express(vs_component_def),
            is_buildtools=cls._is_buildtools(vs_component_def),
            is_vcforpython=cls._is_vcforpython(vs_component_def),
            vs_edition_channel_component_seqnbr_key=vs_edition_channel_component_seqnbr_key,
            vs_edition_channel_component_key=vs_edition_channel_component_key,
            vs_edition_channel_key=vs_edition_channel_key,
            vs_channel_component_key=vs_channel_component_key,
            vs_channel_key=vs_channel_key,
            instance_map=instance_map,
        )

        return msvs_base

    @staticmethod
    def default_order(a, b):
        # vs product numeric: descending order
        if a.vs_product_def.vs_product_numeric != b.vs_product_def.vs_product_numeric:
            return 1 if a.vs_product_def.vs_product_numeric < b.vs_product_def.vs_product_numeric else -1
        # vs channel: ascending order (release, preview)
        if a.vs_channel_def.vs_channel_rank != b.vs_channel_def.vs_channel_rank:
            return 1 if a.vs_channel_def.vs_channel_rank > b.vs_channel_def.vs_channel_rank else -1
        # component rank: descending order
        if a.vs_component_def.vs_component_rank != b.vs_component_def.vs_component_rank:
            return 1 if a.vs_component_def.vs_component_rank < b.vs_component_def.vs_component_rank else -1
        # sequence number: ascending order
        if a.vs_sequence_nbr != b.vs_sequence_nbr:
            return 1 if a.vs_sequence_nbr > b.vs_sequence_nbr else -1
        return 0

    def register_msvs_instance(self, msvs_instance) -> None:
        self.instance_map['msvs_instance'] = msvs_instance

    def register_msvc_instance(self, msvc_instance) -> None:
        self.instance_map['msvc_instance'] = msvc_instance

    @property
    def msvs_instance(self):
        return self.instance_map.get('msvs_instance')

    @property
    def msvc_instance(self):
        return self.instance_map.get('msvc_instance')

    @property
    def vs_component_suffix(self):
        return self.vs_component_def.vs_componentid_def.vs_component_suffix


_MSVSInstance = namedtuple('_MSVSInstance', [
    'id_str',
    'msvs_base',
    'vs_executable',
    'vs_executable_norm',
    'vs_script',
    'vs_script_norm',
    'vc_version_def',
])

class MSVSInstance(_MSVSInstance):

    @classmethod
    def factory(
        cls, *,
        msvs_base,
        vs_executable,
        vs_script,
        vc_version_def,
    ):

        id_str = '{}({})'.format(cls.__name__, ', '.join(msvs_base.id_comps))

        msvs_instance = cls(
            id_str=id_str,
            msvs_base=msvs_base,
            vs_executable=vs_executable,
            vs_executable_norm=_VSUtil.normalize_path(vs_executable),
            vs_script=vs_script,
            vs_script_norm=_VSUtil.normalize_path(vs_script),
            vc_version_def=vc_version_def,
        )

        return msvs_instance

    @staticmethod
    def default_order(a, b):
        return MSVSBase.default_order(a.msvs_base, b.msvs_base)

    @property
    def id_comps(self):
        return self.msvs_base.id_comps

    @property
    def msvc_instance(self):
        return self.msvs_base.msvc_instance

    @property
    def vs_dir(self):
        return self.msvs_base.vs_dir

    @property
    def vs_version(self):
        return self.msvs_base.vs_version

    @property
    def vs_edition_channel_component_seqnbr_key(self):
        return self.msvs_base.vs_edition_channel_component_seqnbr_key

    @property
    def vs_edition_channel_component_key(self):
        return self.msvs_base.vs_edition_channel_component_key

    @property
    def vs_edition_channel_key(self):
        return self.msvs_base.vs_edition_channel_key

    @property
    def vs_channel_component_key(self):
        return self.msvs_base.vs_channel_component_key

    @property
    def vs_channel_key(self):
        return self.msvs_base.vs_channel_key

    @property
    def msvc_version(self):
        return self.vc_version_def.msvc_version

    @property
    def msvc_verstr(self):
        return self.vc_version_def.msvc_verstr

    @property
    def vs_product_def(self):
        return self.msvs_base.vs_product_def

    @property
    def vs_channel_def(self):
        return self.msvs_base.vs_channel_def

    @property
    def vs_componentid_def(self):
        return self.msvs_base.vs_component_def.vs_componentid_def

    @property
    def vs_product(self):
        return self.msvs_base.vs_product_def.vs_product

    @property
    def vs_channel_id(self):
        return self.msvs_base.vs_channel_def.vs_channel_id

    @property
    def vs_component_id(self):
        return self.msvs_base.vs_component_def.vs_componentid_def.vs_component_id

    @property
    def vs_sequence_nbr(self):
        return self.msvs_base.vs_sequence_nbr


_MSVSInstalled = namedtuple('_MSVSInstalled', [
    'msvs_instances',
    'msvs_edition_instances_map',
    'msvs_channel_instances_map',
    'msvs_channel_map', # TODO(JCB): remove?
])

class MSVSInstalled(_MSVSInstalled, Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(
        cls, *,
        msvs_instances,
    ):

        msvs_instances = sorted(
            msvs_instances, key=cmp_to_key(MSVSInstance.default_order)
        )

        msvs_channel_map = {
            vs_channel_def: {}
            for vs_channel_def in Config.MSVS_CHANNEL_DEFINITION_LIST
        }

        vs_edition_instances = {}
        vs_channel_instances = {}

        # channel key: (ANY, None)
        vs_anychannel_key = _VSKeys.msvs_channel_key(
            vs_channel_def=Config.MSVS_CHANNEL_ANY,
        )

        for msvs_instance in msvs_instances:

            debug(
                'msvs instance: id_str=%s, msvc_version=%s, vs_dir=%s, vs_exec=%s',
                repr(msvs_instance.id_str),
                repr(msvs_instance.msvc_version),
                repr(msvs_instance.vs_dir),
                repr(msvs_instance.vs_executable_norm),
                extra=cls.debug_extra,
            )

            # edition key: (product, ANY, None, None)
            vs_edition_any_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvs_instance.vs_product_def,
                vs_channel_def=Config.MSVS_CHANNEL_ANY,
            )

            # edition key: (product, ANY, component, None)
            vs_edition_anychannel_component_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvs_instance.vs_product_def,
                vs_channel_def=Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvs_instance.vs_componentid_def,
            )

            # all editions keys
            vs_edition_keys = (
                vs_edition_any_key,
                msvs_instance.vs_edition_channel_key,
                vs_edition_anychannel_component_key,
                msvs_instance.vs_edition_channel_component_key,
                msvs_instance.vs_edition_channel_component_seqnbr_key,
            )

            # channel key: (ANY, component)
            vs_anychannel_component_key = _VSKeys.msvs_channel_key(
                vs_channel_def=Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvs_instance.vs_componentid_def,
            )

            # all channel keys
            vs_channel_keys = (
                vs_anychannel_key,
                msvs_instance.vs_channel_key,
                vs_anychannel_component_key,
                msvs_instance.vs_channel_component_key,
            )

            for vs_edition_key in vs_edition_keys:
                vs_edition_instances.setdefault(vs_edition_key, []).append(msvs_instance)

            for vs_channel_key in vs_channel_keys:
                vs_channel_instances.setdefault(vs_channel_key, []).append(msvs_instance)

            # msvc_version support

            if msvs_instance.msvc_version != msvs_instance.msvc_verstr:
                versions = [msvs_instance.msvc_verstr, msvs_instance.msvc_version]
            else:
                versions = [msvs_instance.msvc_verstr]

            vs_channel_defs = Config.MSVS_CHANNEL_MEMBERLISTS[msvs_instance.vs_channel_def]

            for vcver in versions:
                for vs_channel_def in vs_channel_defs:

                    msvs_version_map = msvs_channel_map[vs_channel_def]

                    msvs_instance_list = msvs_version_map.setdefault(vcver, [])
                    msvs_instance_list.append(msvs_instance)

        msvs_installed = cls(
            msvs_instances=msvs_instances,
            msvs_edition_instances_map=vs_edition_instances,
            msvs_channel_instances_map=vs_channel_instances,
            msvs_channel_map=msvs_channel_map,
        )

        if DEBUG_ENABLED:
            msvs_installed._debug_dump()

        return msvs_installed

    def _debug_dump(self) -> None:

        for vs_channel_key, msvc_instance_list in self.msvs_channel_instances_map.items():
            msvc_instances = [msvc_instance.id_str for msvc_instance in msvc_instance_list]
            debug(
                'msvs_channel_instances_map[%s]=%s',
                repr(vs_channel_key.serialize()),
                repr(msvc_instances),
                extra=self.debug_extra,
            )

        for vs_edition_key, msvc_instance_list in self.msvs_edition_instances_map.items():
            msvc_instances = [msvc_instance.id_str for msvc_instance in msvc_instance_list]
            debug(
                'msvs_edition_instances_map[%s]=%s',
                repr(vs_edition_key.serialize()),
                repr(msvc_instances),
                extra=self.debug_extra,
            )

        for vs_channel_def, msvs_version_map in self.msvs_channel_map.items():
            for vcver, msvs_instance_list in msvs_version_map.items():
                msvs_instances = [msvs_instance.id_str for msvs_instance in msvs_instance_list]
                debug(
                    'msvs_version_map[%s][%s]=%s',
                    repr(vs_channel_def.vs_channel_suffix),
                    repr(vcver),
                    repr(msvs_instances),
                    extra=self.debug_extra,
                )

    def _query_instances_internal(
        self, *,
        vs_product_def=None,
        vs_channel_def=None,
        vs_componentid_def=None,
        vs_sequence_nbr=None,
    ):

        if not vs_channel_def:
            vs_channel_def = _VSChannel.get_default_channel()

        if vs_product_def:

            query_key = _VSKeys.msvs_edition_key(
                vs_product_def=vs_product_def,
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
                vs_sequence_nbr=vs_sequence_nbr
            )

            msvs_instances = self.msvs_edition_instances_map.get(query_key, [])

        else:

            query_key = _VSKeys.msvs_channel_key(
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
            )

            msvs_instances = self.msvs_channel_instances_map.get(query_key, [])

        debug(
            'query_key=%s, n_msvs_instances=%s',
            repr(query_key.serialize()),
            repr(len(msvs_instances)),
            extra=self.debug_extra,
        )

        return msvs_instances, query_key


_MSVCInstance = namedtuple('_MSVCInstance', [
    'id_str',
    'msvs_base',
    'vc_version_def',
    'vc_feature_map',
    'vc_dir',
    'vc_dir_norm',
    'is_sdkversion_supported',
])

class MSVCInstance(_MSVCInstance, Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(
        cls, *,
        msvs_base,
        vc_version_def,
        vc_feature_map,
        vc_dir,
    ):

        id_str = '{}({})'.format(cls.__name__, ', '.join(msvs_base.id_comps))

        if vc_feature_map is None:
            vc_feature_map = {}

        msvc_instance = cls(
            id_str=id_str,
            msvs_base=msvs_base,
            vc_version_def=vc_version_def,
            vc_feature_map=vc_feature_map,
            vc_dir=vc_dir,
            vc_dir_norm=_VSUtil.normalize_path(vc_dir),
            is_sdkversion_supported=cls._is_sdkversion_supported(msvs_base),
        )

        return msvc_instance

    @staticmethod
    def default_order(a, b):
        return MSVSBase.default_order(a.msvs_base, b.msvs_base)

    @property
    def id_comps(self):
        return self.msvs_base.id_comps

    @property
    def msvs_instance(self):
        return self.msvs_base.msvs_instance

    @staticmethod
    def _is_sdkversion_supported(msvs_base) -> bool:

        vs_componentid_def = msvs_base.vs_component_def.vs_componentid_def
        vs_product_numeric = msvs_base.vs_product_def.vs_product_numeric

        if vs_product_numeric >= 2017:
            # VS2017 and later
            is_supported = True
        elif vs_product_numeric == 2015:
            # VS2015:
            #   False: Express, BuildTools
            #   True:  Develop, CmdLine
            if vs_componentid_def == Config.MSVS_COMPONENTID_EXPRESS:
                is_supported = False
            elif vs_componentid_def == Config.MSVS_COMPONENTID_BUILDTOOLS:
                is_supported = False
            else:
                is_supported = True
        else:
            # VS2013 and earlier
            is_supported = False

        return is_supported

    def skip_uwp_target(self, env) -> bool:
        skip = False
        if self.vc_feature_map:
            target_arch = env.get('TARGET_ARCH')
            uwp_target_is_supported = self.vc_feature_map.get('uwp_target_is_supported', {})
            is_supported = uwp_target_is_supported.get(target_arch, True)
            skip = bool(not is_supported)
        debug(
            'skip=%s, msvc_version=%s',
            repr(skip), repr(self.vc_version_def.msvc_version), extra=self.debug_extra
        )
        return skip

    def is_uwp_target_supported(self, target_arch=None) -> bool:

        vs_componentid_def = self.msvs_base.vs_component_def.vs_componentid_def
        vs_product_numeric = self.msvs_base.vs_product_def.vs_product_numeric

        is_target = False
        if vs_product_numeric >= 2017:
            # VS2017 and later
            is_supported = True
        elif vs_product_numeric == 2015:
            # VS2015:
            #   Maybe: Express
            #   False: BuildTools
            #   True:  Develop, CmdLine
            if vs_componentid_def == Config.MSVS_COMPONENTID_EXPRESS:
                uwp_target_is_supported = self.vc_feature_map.get('uwp_target_is_supported', {})
                is_supported = uwp_target_is_supported.get(target_arch, True)
                is_target = True
            elif vs_componentid_def == Config.MSVS_COMPONENTID_BUILDTOOLS:
                is_supported = False
            else:
                is_supported = True
        else:
            # VS2013 and earlier
            is_supported = False

        debug(
            'is_supported=%s, is_target=%s, msvc_version=%s, msvs_component=%s, target_arch=%s',
            is_supported, is_target,
            repr(self.vc_version_def.msvc_version),
            repr(vs_componentid_def.vs_component_id),
            repr(target_arch),
            extra=self.debug_extra,
        )

        return is_supported, is_target

    # convenience properties: reduce member lookup chain for readability

    @property
    def is_express(self) -> bool:
        return self.msvs_base.is_express

    @property
    def is_buildtools(self) -> bool:
        return self.msvs_base.is_buildtools

    @property
    def is_vcforpython(self) -> bool:
        return self.msvs_base.is_vcforpython

    @property
    def vs_edition_channel_component_seqnbr_key(self):
        return self.msvs_base.vs_edition_channel_component_seqnbr_key

    @property
    def vs_edition_channel_component_key(self):
        return self.msvs_base.vs_edition_channel_component_key

    @property
    def vs_edition_channel_key(self):
        return self.msvs_base.vs_edition_channel_key

    @property
    def vs_channel_component_key(self):
        return self.msvs_base.vs_channel_component_key

    @property
    def vs_channel_key(self):
        return self.msvs_base.vs_channel_key

    @property
    def msvc_version(self):
        return self.vc_version_def.msvc_version

    @property
    def msvc_vernum(self):
        return self.vc_version_def.msvc_vernum

    @property
    def msvc_verstr(self):
        return self.vc_version_def.msvc_verstr

    @property
    def vs_product_def(self):
        return self.msvs_base.vs_product_def

    @property
    def vs_channel_def(self):
        return self.msvs_base.vs_channel_def

    @property
    def vs_componentid_def(self):
        return self.msvs_base.vs_component_def.vs_componentid_def

    @property
    def vs_product(self):
        return self.msvs_base.vs_product_def.vs_product

    @property
    def vs_product_numeric(self):
        return self.msvs_base.vs_product_def.vs_product_numeric

    @property
    def vs_channel_id(self):
        return self.msvs_base.vs_channel_def.vs_channel_id

    @property
    def vs_component_id(self):
        return self.msvs_base.vs_component_def.vs_componentid_def.vs_component_id

    @property
    def vs_sequence_nbr(self):
        return self.msvs_base.vs_sequence_nbr


_MSVCInstalled = namedtuple('_MSVCInstalled', [
    'msvc_instances',
    'msvs_edition_instances_map',
    'msvs_channel_instances_map',
    'msvs_channel_map', # TODO(JCB): remove?
])

class MSVCInstalled(_MSVCInstalled, Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(
        cls, *,
        msvc_instances,
    ):

        msvc_instances = sorted(
            msvc_instances, key=cmp_to_key(MSVCInstance.default_order)
        )

        msvs_channel_map = {
            vs_channel_def: {}
            for vs_channel_def in Config.MSVS_CHANNEL_DEFINITION_LIST
        }

        vs_edition_instances = {}
        vs_channel_instances = {}

        # channel key: (ANY, None)
        vs_anychannel_key = _VSKeys.msvs_channel_key(
            vs_channel_def=Config.MSVS_CHANNEL_ANY,
        )

        for msvc_instance in msvc_instances:

            debug(
                'msvc_instance: id_str=%s, msvc_version=%s, vc_dir=%s',
                repr(msvc_instance.id_str),
                repr(msvc_instance.msvc_version),
                repr(msvc_instance.vc_dir),
                extra=cls.debug_extra,
            )

            # edition key: (product, ANY, None, None)
            vs_edition_any_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvc_instance.vs_product_def,
                vs_channel_def=Config.MSVS_CHANNEL_ANY,
            )

            # edition key: (product, ANY, component, None)
            vs_edition_anychannel_component_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvc_instance.vs_product_def,
                vs_channel_def=Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvc_instance.vs_componentid_def,
            )

            # all editions keys
            vs_edition_keys = (
                vs_edition_any_key,
                msvc_instance.vs_edition_channel_key,
                vs_edition_anychannel_component_key,
                msvc_instance.vs_edition_channel_component_key,
                msvc_instance.vs_edition_channel_component_seqnbr_key,
            )

            # channel key: (ANY, component)
            vs_anychannel_component_key = _VSKeys.msvs_channel_key(
                vs_channel_def=Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvc_instance.vs_componentid_def,
            )

            # all channel keys
            vs_channel_keys = (
                vs_anychannel_key,
                msvc_instance.vs_channel_key,
                vs_anychannel_component_key,
                msvc_instance.vs_channel_component_key,
            )

            for vs_edition_key in vs_edition_keys:
                vs_edition_instances.setdefault(vs_edition_key, []).append(msvc_instance)

            for vs_channel_key in vs_channel_keys:
                vs_channel_instances.setdefault(vs_channel_key, []).append(msvc_instance)

            # msvc_version support

            if msvc_instance.msvc_version != msvc_instance.msvc_verstr:
                versions = [msvc_instance.msvc_verstr, msvc_instance.msvc_version]
            else:
                versions = [msvc_instance.msvc_verstr]

            vs_channel_defs = Config.MSVS_CHANNEL_MEMBERLISTS[msvc_instance.vs_channel_def]

            for vcver in versions:

                for vs_channel_def in vs_channel_defs:

                    msvc_version_map = msvs_channel_map[vs_channel_def]

                    msvc_instance_list = msvc_version_map.setdefault(vcver, [])
                    msvc_instance_list.append(msvc_instance)

        msvc_installed = cls(
            msvc_instances=msvc_instances,
            msvs_edition_instances_map=vs_edition_instances,
            msvs_channel_instances_map=vs_channel_instances,
            msvs_channel_map=msvs_channel_map,
        )

        if DEBUG_ENABLED:
            msvc_installed._debug_dump()

        return msvc_installed

    def _debug_dump(self) -> None:

        for vs_channel_key, msvc_instance_list in self.msvs_channel_instances_map.items():
            msvc_instances = [msvc_instance.id_str for msvc_instance in msvc_instance_list]
            debug(
                'msvs_channel_instances_map[%s]=%s',
                repr(vs_channel_key.serialize()),
                repr(msvc_instances),
                extra=self.debug_extra,
            )

        for vs_edition_key, msvc_instance_list in self.msvs_edition_instances_map.items():
            msvc_instances = [msvc_instance.id_str for msvc_instance in msvc_instance_list]
            debug(
                'msvs_edition_instances_map[%s]=%s',
                repr(vs_edition_key.serialize()),
                repr(msvc_instances),
                extra=self.debug_extra,
            )

        for vs_channel_def, msvc_version_map in self.msvs_channel_map.items():
            for vcver, msvc_instance_list in msvc_version_map.items():
                msvc_instances = [msvc_instance.id_str for msvc_instance in msvc_instance_list]
                debug(
                    'msvc_version_map[%s][%s]=%s',
                    repr(vs_channel_def.vs_channel_suffix),
                    repr(vcver),
                    repr(msvc_instances),
                    extra=self.debug_extra,
                )

    def _query_instances_internal(
        self, *,
        vs_product_def=None,
        vs_channel_def=None,
        vs_componentid_def=None,
        vs_sequence_nbr=None,
    ):

        if not vs_channel_def:
            vs_channel_def = _VSChannel.get_default_channel()

        if vs_product_def:

            query_key = _VSKeys.msvs_edition_key(
                vs_product_def=vs_product_def,
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
                vs_sequence_nbr=vs_sequence_nbr
            )

            msvc_instances = self.msvs_edition_instances_map.get(query_key, [])

        else:

            query_key = _VSKeys.msvs_channel_key(
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
            )

            msvc_instances = self.msvs_channel_instances_map.get(query_key, [])

        debug(
            'query_key=%s, n_msvc_instances=%s',
            repr(query_key.serialize()),
            repr(len(msvc_instances)),
            extra=self.debug_extra,
        )

        return msvc_instances, query_key


_MSVSManager = namedtuple('_MSVSManager', [
    'msvc_installed',
    'msvs_installed',
])

class MSVSManager(_MSVSManager, Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(cls, msvc_installed, msvs_installed):

        msvs_manager = cls(
            msvc_installed=msvc_installed,
            msvs_installed=msvs_installed,
        )

        debug(
            'n_msvc_instances=%d, n_msvs_instances=%d',
            len(msvc_installed.msvc_instances),
            len(msvs_installed.msvs_instances),
            extra=cls.debug_extra,
        )

        return msvs_manager

    def default_msvs_channel(self):
        vs_channel_def = _VSChannel.get_default_channel()
        return vs_channel_def

    def get_installed_msvc_instances(self):
        # TODO(JCB): channel?
        vs_channel_def = _VSChannel.get_default_channel()
        msvs_channel_map = self.msvc_installed.msvs_channel_map
        msvc_version_map = msvs_channel_map.get(vs_channel_def)
        installed_msvc_instances = [
            msvc_version_map[vc_version][0]
            for vc_version in msvc_version_map.keys()
        ]
        return installed_msvc_instances

    def get_installed_msvc_versions(self):
        # TODO(JCB): channel?
        vs_channel_def = _VSChannel.get_default_channel()
        msvs_channel_map = self.msvc_installed.msvs_channel_map
        msvc_version_map = msvs_channel_map.get(vs_channel_def)
        installed_msvc_versions = [
            vc_version
            for vc_version in msvc_version_map.keys()
        ]
        return installed_msvc_versions

    def query_msvs_instances(
        self, *,
        msvc_version,
    ):

        # TODO(JCB): temporary placeholder

        prefix, suffix = Util.get_msvc_version_prefix_suffix(msvc_version)

        vs_product_def = Config.MSVC_VERSION_INTERNAL[prefix]

        vs_channel_def = None

        if suffix == 'Exp':
            vs_componentid_def = Config.MSVS_COMPONENTID_EXPRESS
        else:
            vs_componentid_def = None

        msvs_instances, query_key = self.msvs_installed._query_instances_internal(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        return msvs_instances, query_key

    def query_msvc_instances(
        self, *,
        msvc_version,
    ):

        # TODO(JCB): temporary placeholder

        prefix, suffix = Util.get_msvc_version_prefix_suffix(msvc_version)

        vs_product_def = Config.MSVC_VERSION_INTERNAL[prefix]

        vs_channel_def = None

        if suffix == 'Exp':
            vs_componentid_def = Config.MSVS_COMPONENTID_EXPRESS
        else:
            vs_componentid_def = None

        msvc_instances, query_key = self.msvc_installed._query_instances_internal(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        return msvc_instances, query_key


class _VSDetectCommon(Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)

    VSDetectedBinaries = namedtuple("VSDetectedBinaries", [
        'bitfields',  # detect values
        'have_dev',  # develop ide binary
        'have_exp',  # express ide binary
        'have_exp_win',  # express windows ide binary
        'have_exp_web',  # express web ide binary
        'vs_exec',  # vs binary
    ])

    @classmethod
    def msvs_detect(cls, vs_dir, vs_cfg):

        vs_exec = None
        vs_script = None

        vs_binary_cfg = vs_cfg.vs_binary_cfg
        vs_batch_cfg = vs_cfg.vs_batch_cfg

        ide_path = os.path.join(vs_dir, vs_binary_cfg.pathcomp)

        bitfields = 0b_0000
        for ide_program in vs_binary_cfg.programs:
            prog = os.path.join(ide_path, ide_program.program)
            if not os.path.exists(prog):
                continue
            bitfields |= ide_program.bitfield
            if vs_exec:
                continue
            if not ide_program.bitfield & _VSConfig.EXECUTABLE_MASK:
                continue
            vs_exec = prog

        have_dev = bool(bitfields & _VSConfig.BITFIELD_DEVELOP)
        have_exp = bool(bitfields & _VSConfig.BITFIELD_EXPRESS)
        have_exp_win = bool(bitfields & _VSConfig.BITFIELD_EXPRESS_WIN)
        have_exp_web = bool(bitfields & _VSConfig.BITFIELD_EXPRESS_WEB)

        binaries_t = cls.VSDetectedBinaries(
            bitfields=bitfields,
            have_dev=have_dev,
            have_exp=have_exp,
            have_exp_win=have_exp_win,
            have_exp_web=have_exp_web,
            vs_exec=vs_exec,
        )

        script_file = os.path.join(vs_dir, vs_batch_cfg.pathcomp, vs_batch_cfg.script)
        if os.path.exists(script_file):
            vs_script = script_file

        debug(
            'vs_dir=%s, dev=%s, exp=%s, exp_win=%s, exp_web=%s, vs_exec=%s, vs_script=%s',
            repr(vs_dir),
            binaries_t.have_dev, binaries_t.have_exp,
            binaries_t.have_exp_win, binaries_t.have_exp_web,
            repr(binaries_t.vs_exec),
            repr(vs_script),
            extra=cls.debug_extra,
        )

        return binaries_t, vs_script


class _VSDetectVSWhere(Util.AutoInitialize):

    DETECT_CONFIG = _VSConfig.DETECT_VSWHERE

    # initialization

    debug_extra = None
    reset_funcs = []

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls.reset()

    @classmethod
    def reset(cls) -> None:

        cls.vswhere_executable_seen = set()
        cls.vswhere_executables = []

        cls.vs_dir_seen = set()

        cls.msvs_sequence_nbr = {}

        cls.msvs_instances = []
        cls.msvc_instances = []

    @classmethod
    def register_reset_func(cls, func) -> None:
        if func:
            cls.reset_funcs.append(func)

    @classmethod
    def call_reset_funcs(cls) -> None:
        for func in cls.reset_funcs:
            func()

    @classmethod
    def _filter_vswhere_paths(cls, vswhere_env):
        vswhere_executables = VSWhere.vswhere_get_executables(vswhere_env)
        vswhere_paths = [
            vswhere_exec.norm
            for vswhere_exec in vswhere_executables
            if vswhere_exec.norm not in cls.vswhere_executable_seen
        ]
        debug('vswhere_paths=%s', vswhere_paths, extra=cls.debug_extra)
        return vswhere_paths

    @classmethod
    def _vswhere_query_json_output(cls, vswhere_exe, vswhere_args):

        vswhere_json = None

        once = True
        while once:
            once = False
            # using break for single exit (unless exception)

            vswhere_cmd = [vswhere_exe] + vswhere_args + ['-format', 'json', '-utf8']
            debug("running: %s", vswhere_cmd, extra=cls.debug_extra)

            try:
                cp = subprocess.run(
                    vswhere_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
                )
            except OSError as e:
                errmsg = str(e)
                debug("%s: %s", type(e).__name__, errmsg, extra=cls.debug_extra)
                break
            except Exception as e:
                errmsg = str(e)
                debug("%s: %s", type(e).__name__, errmsg, extra=cls.debug_extra)
                raise

            if not cp.stdout:
                debug("no vswhere information returned", extra=cls.debug_extra)
                break

            vswhere_output = cp.stdout.decode('utf8', errors='replace')
            if not vswhere_output:
                debug("no vswhere information output", extra=cls.debug_extra)
                break

            try:
                vswhere_output_json = json.loads(vswhere_output)
            except json.decoder.JSONDecodeError:
                debug("json decode exception loading vswhere output", extra=cls.debug_extra)
                break

            vswhere_json = vswhere_output_json
            break

        debug(
            'vswhere_json=%s, vswhere_exe=%s',
            bool(vswhere_json), repr(vswhere_exe), extra=cls.debug_extra
        )

        return vswhere_json

    @classmethod
    def _msvc_resolve(cls, vc_dir, vs_product_def):

        detect_cfg = cls.DETECT_CONFIG[vs_product_def.vs_product]

        vs_cfg = detect_cfg.vs_cfg
        vs_dir = os.path.normpath(os.path.join(vc_dir, vs_cfg.root))

        binaries_t, vs_script = _VSDetectCommon.msvs_detect(vs_dir, vs_cfg)

        return binaries_t.vs_exec, vs_script

    @classmethod
    def _msvc_instance_toolsets(cls, msvc_instance):
        # TODO(JCB): load toolsets/tools
        rval = _msvc_instance_check_files_exist(msvc_instance)
        return rval

    @classmethod
    def detect(cls, vswhere_env):

        num_instances = len(cls.msvc_instances)
        num_new_instances = 0

        vswhere_paths = cls._filter_vswhere_paths(vswhere_env)
        if vswhere_paths:

            num_beg_instances = num_instances

            for vswhere_exe in vswhere_paths:

                if vswhere_exe in cls.vswhere_executable_seen:
                    continue

                cls.vswhere_executable_seen.add(vswhere_exe)
                cls.vswhere_executables.append(vswhere_exe)

                debug('vswhere_exe=%s', repr(vswhere_exe), extra=cls.debug_extra)

                vswhere_json = cls._vswhere_query_json_output(
                    vswhere_exe,
                    ['-all', '-products', '*', '-prerelease']
                )

                if not vswhere_json:
                    continue

                for instance in vswhere_json:

                    #print(json.dumps(instance, indent=4, sort_keys=True))

                    vs_dir = instance.get('installationPath')
                    if not vs_dir or not _VSUtil.path_exists(vs_dir):
                        continue

                    vs_norm = _VSUtil.normalize_path(vs_dir)
                    if vs_norm in cls.vs_dir_seen:
                        continue

                    vs_version = instance.get('installationVersion')
                    if not vs_version:
                        continue

                    product_id = instance.get('productId')
                    if not product_id:
                        continue

                    # consider msvs root evaluated at this point
                    cls.vs_dir_seen.add(vs_norm)

                    vc_dir = os.path.join(vs_dir, 'VC')
                    if not _VSUtil.path_exists(vc_dir):
                        continue

                    vs_major = vs_version.split('.')[0]
                    if vs_major not in Config.MSVS_VERSION_MAJOR_MAP:
                        debug('ignore vs_major: %s', vs_major, extra=cls.debug_extra)
                        continue

                    vs_product_def = Config.MSVS_VERSION_MAJOR_MAP[vs_major]

                    component_id = product_id.split('.')[-1]
                    vs_component_def = Config.VSWHERE_COMPONENT_INTERNAL.get(component_id)
                    if not vs_component_def:
                        debug('ignore component_id: %s', component_id, extra=cls.debug_extra)
                        continue

                    is_prerelease = True if instance.get('isPrerelease', False) else False
                    if is_prerelease:
                        vs_channel_def = Config.MSVS_CHANNEL_PREVIEW
                    else:
                        vs_channel_def = Config.MSVS_CHANNEL_RELEASE

                    vs_exec, vs_script = cls._msvc_resolve(vc_dir, vs_product_def)

                    vs_sequence_key = (vs_product_def, vs_channel_def, vs_component_def)

                    cls.msvs_sequence_nbr.setdefault(vs_sequence_key, 0)
                    cls.msvs_sequence_nbr[vs_sequence_key] += 1

                    vs_sequence_nbr = cls.msvs_sequence_nbr[vs_sequence_key]

                    msvs_base = MSVSBase.factory(
                        vs_product_def=vs_product_def,
                        vs_channel_def=vs_channel_def,
                        vs_component_def=vs_component_def,
                        vs_sequence_nbr=vs_sequence_nbr,
                        vs_dir=vs_dir,
                        vs_version=vs_version,
                    )

                    vc_version = vs_product_def.vc_buildtools_def.vc_version

                    if msvs_base.is_express:
                        vc_version += msvs_base.vs_component_suffix

                    vc_version_def = Util.msvc_version_components(vc_version)

                    msvc_instance = MSVCInstance.factory(
                        msvs_base=msvs_base,
                        vc_version_def=vc_version_def,
                        vc_feature_map=None,
                        vc_dir=vc_dir,
                    )

                    if not cls._msvc_instance_toolsets(msvc_instance):
                        # no compilers detected don't register objects
                        continue

                    if vs_exec:

                        # TODO(JCB): register iff compilers and executable?
                        msvs_instance = MSVSInstance.factory(
                            msvs_base=msvs_base,
                            vs_executable=vs_exec,
                            vs_script=vs_script,
                            vc_version_def=vc_version_def,
                        )

                        msvs_base.register_msvs_instance(msvs_instance)
                        cls.msvs_instances.append(msvs_instance)

                        debug(
                            'msvs_instance=%s',
                            repr(msvs_instance.id_str),
                            extra=cls.debug_extra,
                        )

                    msvs_base.register_msvc_instance(msvc_instance)
                    cls.msvc_instances.append(msvc_instance)

                    debug(
                        'msvc_instance=%s',
                        repr(msvc_instance.id_str),
                        extra=cls.debug_extra,
                    )

            num_instances = len(cls.msvc_instances)
            num_new_instances = num_instances - num_beg_instances

        if num_new_instances > 0:
            cls.call_reset_funcs()
            debug(
                'num_new_instances=%s, num_instances=%s',
                num_new_instances, num_instances, extra=cls.debug_extra
            )

        return num_new_instances


class _VSDetectRegistry(Util.AutoInitialize):

    DETECT_CONFIG = _VSConfig.DETECT_REGISTRY

    # initialization

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls.reset()

    @classmethod
    def reset(cls) -> None:

        cls.registry_once = False

        cls.vc_dir_seen = set()

        cls.msvs_sequence_nbr = {}

        cls.msvs_instances = []
        cls.msvc_instances = []

    # VS2015 buildtools batch file call detection
    #    vs2015 buildtools do not support sdk_version or UWP arguments

    _VS2015BT_PATH = r'..\Microsoft Visual C++ Build Tools\vcbuildtools.bat'

    _VS2015BT_REGEX_STR = ''.join([
        r'^\s*if\s+exist\s+',
        re.escape(fr'"%~dp0..\{_VS2015BT_PATH}"'),
        r'\s+goto\s+setup_buildsku\s*$',
    ])

    _VS2015BT_VCVARS_BUILDTOOLS = re.compile(_VS2015BT_REGEX_STR, re.IGNORECASE)
    _VS2015BT_VCVARS_STOP = re.compile(r'^\s*[:]Setup_VS\s*$', re.IGNORECASE)

    @classmethod
    def _vs_buildtools_2015_vcvars(cls, vcvars_file) -> bool:
        have_buildtools_vcvars = False
        with open(vcvars_file) as fh:
            for line in fh:
                if cls._VS2015BT_VCVARS_BUILDTOOLS.match(line):
                    have_buildtools_vcvars = True
                    break
                if cls._VS2015BT_VCVARS_STOP.match(line):
                    break
        return have_buildtools_vcvars

    @classmethod
    def _vs_buildtools_2015(cls, vs_dir, vc_dir) -> bool:

        is_buildtools = False

        do_once = True
        while do_once:
            do_once = False

            buildtools_file = os.path.join(vs_dir, cls._VS2015BT_PATH)
            have_buildtools = os.path.exists(buildtools_file)
            debug('have_buildtools=%s', have_buildtools, extra=cls.debug_extra)
            if not have_buildtools:
                break

            vcvars_file = os.path.join(vc_dir, 'vcvarsall.bat')
            have_vcvars = os.path.exists(vcvars_file)
            debug('have_vcvars=%s', have_vcvars, extra=cls.debug_extra)
            if not have_vcvars:
                break

            have_buildtools_vcvars = cls._vs_buildtools_2015_vcvars(vcvars_file)
            debug('have_buildtools_vcvars=%s', have_buildtools_vcvars, extra=cls.debug_extra)
            if not have_buildtools_vcvars:
                break

            is_buildtools = True

        debug('is_buildtools=%s', is_buildtools, extra=cls.debug_extra)
        return is_buildtools

    _VS2015EXP_VCVARS_LIBPATH = re.compile(
        ''.join([
            r'^\s*\@if\s+exist\s+\"\%VCINSTALLDIR\%LIB\\store\\(amd64|arm)"\s+',
            r'set (LIB|LIBPATH)=\%VCINSTALLDIR\%LIB\\store\\(amd64|arm);.*\%(LIB|LIBPATH)\%\s*$'
        ]),
        re.IGNORECASE
    )

    _VS2015EXP_VCVARS_STOP = re.compile(r'^\s*[:]GetVSCommonToolsDir\s*$', re.IGNORECASE)

    @classmethod
    def _vs_express_2015_vcvars(cls, vcvars_file) -> bool:
        n_libpath = 0
        with open(vcvars_file) as fh:
            for line in fh:
                if cls._VS2015EXP_VCVARS_LIBPATH.match(line):
                    n_libpath += 1
                elif cls._VS2015EXP_VCVARS_STOP.match(line):
                    break
        have_uwp_fix = bool(n_libpath >= 2)
        return have_uwp_fix

    @classmethod
    def _vs_express_2015(cls, vc_dir):

        have_uwp_amd64 = False
        have_uwp_arm = False

        vcvars_file = os.path.join(vc_dir, r'vcvarsall.bat')
        if os.path.exists(vcvars_file):

            vcvars_file = os.path.join(vc_dir, r'bin\x86_amd64\vcvarsx86_amd64.bat')
            if os.path.exists(vcvars_file):
                have_uwp_fix = cls._vs_express_2015_vcvars(vcvars_file)
                if have_uwp_fix:
                    have_uwp_amd64 = True

            vcvars_file = os.path.join(vc_dir, r'bin\x86_arm\vcvarsx86_arm.bat')
            if os.path.exists(vcvars_file):
                have_uwp_fix = cls._vs_express_2015_vcvars(vcvars_file)
                if have_uwp_fix:
                    have_uwp_arm = True

        debug('have_uwp_amd64=%s, have_uwp_arm=%s', have_uwp_amd64, have_uwp_arm, extra=cls.debug_extra)
        return have_uwp_amd64, have_uwp_arm

    # winsdk installed 2010 [7.1], 2008 [7.0, 6.1] folders

    _REGISTRY_WINSDK_VERSIONS = {'10.0', '9.0'}

    @classmethod
    def _msvc_dir_is_winsdk_only(cls, vc_dir, msvc_version) -> bool:

        # detect winsdk-only installations
        #
        #     registry keys:
        #         [prefix]\VisualStudio\SxS\VS7\10.0  <undefined>
        #         [prefix]\VisualStudio\SxS\VC7\10.0  product directory
        #         [prefix]\VisualStudio\SxS\VS7\9.0   <undefined>
        #         [prefix]\VisualStudio\SxS\VC7\9.0   product directory
        #
        #     winsdk notes:
        #         - winsdk installs do not define the common tools env var
        #         - the product dir is detected but the vcvars batch files will fail
        #         - regular installations populate the VS7 registry keys

        if msvc_version not in cls._REGISTRY_WINSDK_VERSIONS:

            is_sdk = False

            debug('is_sdk=%s, msvc_version=%s', is_sdk, repr(msvc_version), extra=cls.debug_extra)

        else:

            vc_suffix = Registry.vstudio_sxs_vc7(msvc_version)
            vc_qresults = [record[0] for record in Registry.microsoft_query_paths(vc_suffix)]
            vc_regdir = vc_qresults[0] if vc_qresults else None

            if vc_regdir != vc_dir:
                # registry vc path is not the current vc dir

                is_sdk = False

                debug(
                    'is_sdk=%s, msvc_version=%s, vc_dir=%s, vc_regdir=%s',
                    is_sdk, repr(msvc_version), repr(vc_dir), repr(vc_regdir), extra=cls.debug_extra
                )

            else:
                # registry vc dir is the current vc root

                vs_suffix = Registry.vstudio_sxs_vs7(msvc_version)
                vs_qresults = [record[0] for record in Registry.microsoft_query_paths(vs_suffix)]
                vs_dir = vs_qresults[0] if vs_qresults else None

                is_sdk = bool(not vs_dir and vc_dir)

                debug(
                    'is_sdk=%s, msvc_version=%s, vc_dir=%s, vs_dir=%s',
                    is_sdk, repr(msvc_version), repr(vc_dir), repr(vs_dir), extra=cls.debug_extra
                )

        return is_sdk

    @classmethod
    def _msvc_resolve(cls, vc_dir, vs_product_def, is_vcforpython, vs_version):

        detect_cfg = cls.DETECT_CONFIG[vs_product_def.vs_product]

        vc_feature_map = {}

        vs_cfg = detect_cfg.vs_cfg
        vs_dir = os.path.normpath(os.path.join(vc_dir, vs_cfg.root))

        binaries_t, vs_script = _VSDetectCommon.msvs_detect(vs_dir, vs_cfg)

        vs_product_numeric = vs_product_def.vs_product_numeric
        vc_version = vs_product_def.vc_buildtools_def.vc_version

        if binaries_t.have_dev:
            vs_component_def = Config.REGISTRY_COMPONENT_DEVELOP
        elif binaries_t.have_exp:
            vs_component_def = Config.REGISTRY_COMPONENT_EXPRESS
        elif vs_product_numeric == 2008 and is_vcforpython:
            vs_component_def = Config.REGISTRY_COMPONENT_PYTHON
        elif binaries_t.have_exp_win:
            vs_component_def = None
        elif binaries_t.have_exp_web:
            vs_component_def = None
        elif cls._msvc_dir_is_winsdk_only(vc_dir, vc_version):
            vs_component_def = None
        else:
            vs_component_def = Config.REGISTRY_COMPONENT_CMDLINE

        if vs_component_def and vs_product_numeric == 2015:

            # VS2015:
            #     remap DEVELOP => ENTERPRISE, PROFESSIONAL, COMMUNITY
            #     remap CMDLINE => BUILDTOOLS [conditional]
            #     process EXPRESS

            if vs_component_def == Config.REGISTRY_COMPONENT_DEVELOP:

                for reg_component, reg_component_def in [
                    ('community', Config.REGISTRY_COMPONENT_COMMUNITY),
                    ('professional', Config.REGISTRY_COMPONENT_PROFESSIONAL),
                    ('enterprise', Config.REGISTRY_COMPONENT_ENTERPRISE),
                ]:
                    suffix = Registry.devdiv_vs_servicing_component(vs_version, reg_component)
                    qresults = Registry.microsoft_query_keys(suffix, usrval=reg_component_def)
                    if not qresults:
                        continue
                    vs_component_def = qresults[0][-1]
                    break

            elif vs_component_def == Config.REGISTRY_COMPONENT_CMDLINE:

                if cls._vs_buildtools_2015(vs_dir, vc_dir):
                    vs_component_def = Config.REGISTRY_COMPONENT_BUILDTOOLS

            elif vs_component_def == Config.REGISTRY_COMPONENT_EXPRESS:

                have_uwp_amd64, have_uwp_arm = cls._vs_express_2015(vc_dir)

                uwp_target_is_supported = {
                    'x86': True,
                    'amd64': have_uwp_amd64,
                    'arm': have_uwp_arm,
                }

                vc_feature_map['uwp_target_is_supported'] = uwp_target_is_supported

        debug(
            'vs_product=%s, vs_component=%s, vc_dir=%s, vc_feature_map=%s',
            repr(vs_product_numeric),
            repr(vs_component_def.vs_componentid_def.vs_component_id) if vs_component_def else None,
            repr(vc_dir),
            repr(vc_feature_map),
            extra=cls.debug_extra
        )

        return vs_component_def, vs_dir, binaries_t.vs_exec, vs_script, vc_feature_map

    @classmethod
    def _msvc_instance_toolsets(cls, msvc_instance):
        # TODO(JCB): load toolsets/tools
        rval = _msvc_instance_check_files_exist(msvc_instance)
        return rval

    @classmethod
    def detect(cls):

        num_instances = len(cls.msvc_instances)
        num_new_instances = 0

        if not cls.registry_once:
            cls.registry_once = True

            num_beg_instances = num_instances

            is_win64 = common.is_win64()

            for vs_product, config in cls.DETECT_CONFIG.items():

                key_prefix = 'Software\\'
                for regkey in config.vc_cfg.regkeys:

                    if not regkey.hkroot or not regkey.key:
                        continue

                    if is_win64:
                        mskeys = [key_prefix + 'Wow6432Node\\' + regkey.key, key_prefix + regkey.key]
                    else:
                        mskeys = [key_prefix + regkey.key]

                    vc_dir = None
                    for mskey in mskeys:
                        debug('trying VC registry key %s', repr(mskey), extra=cls.debug_extra)
                        try:
                            vc_dir = common.read_reg(mskey, regkey.hkroot)
                        except OSError:
                            continue
                        if vc_dir:
                            break

                    if not vc_dir:
                        debug('no VC registry key %s', repr(regkey.key), extra=cls.debug_extra)
                        continue

                    if vc_dir in cls.vc_dir_seen:
                        continue
                    cls.vc_dir_seen.add(vc_dir)

                    if not os.path.exists(vc_dir):
                        debug(
                            'reg says vc dir is %s, but it does not exist. (ignoring)',
                            repr(vc_dir), extra=cls.debug_extra
                        )
                        continue

                    if regkey.is_vsroot:

                        vc_dir = os.path.join(vc_dir, 'VC')
                        debug('convert vs dir to vc dir: %s', repr(vc_dir), extra=cls.debug_extra)

                        if vc_dir in cls.vc_dir_seen:
                            continue
                        cls.vc_dir_seen.add(vc_dir)

                        if not os.path.exists(vc_dir):
                            debug('vc dir does not exist. (ignoring)', repr(vc_dir), extra=cls.debug_extra)
                            continue

                    vc_norm = _VSUtil.normalize_path(vc_dir)
                    if vc_norm in cls.vc_dir_seen:
                        continue
                    cls.vc_dir_seen.add(vc_norm)

                    vs_product_def = Config.MSVS_VERSION_INTERNAL[vs_product]

                    vs_component_def, vs_dir, vs_exec, vs_script, vc_feature_map = cls._msvc_resolve(
                        vc_norm,
                        vs_product_def,
                        regkey.is_vcforpython,
                        vs_product_def.vs_version
                    )

                    if not vs_component_def:
                        continue

                    vs_channel_def = Config.MSVS_CHANNEL_RELEASE

                    vs_sequence_key = (vs_product_def, vs_channel_def, vs_component_def)

                    cls.msvs_sequence_nbr.setdefault(vs_sequence_key, 0)
                    cls.msvs_sequence_nbr[vs_sequence_key] += 1

                    vs_sequence_nbr = cls.msvs_sequence_nbr[vs_sequence_key]

                    msvs_base = MSVSBase.factory(
                        vs_product_def=vs_product_def,
                        vs_channel_def=vs_channel_def,
                        vs_component_def=vs_component_def,
                        vs_sequence_nbr=vs_sequence_nbr,
                        vs_dir=vs_dir,
                        vs_version=vs_product_def.vs_version,
                    )

                    vc_version = vs_product_def.vc_buildtools_def.vc_version

                    if msvs_base.is_express:
                        vc_version += msvs_base.vs_component_suffix

                    vc_version_def = Util.msvc_version_components(vc_version)

                    msvc_instance = MSVCInstance.factory(
                        msvs_base=msvs_base,
                        vc_version_def=vc_version_def,
                        vc_feature_map=vc_feature_map,
                        vc_dir=vc_dir,
                    )

                    if not cls._msvc_instance_toolsets(msvc_instance):
                        # no compilers detected don't register objects
                        continue

                    if vs_exec:

                        # TODO(JCB): register iff compilers and executable?
                        msvs_instance = MSVSInstance.factory(
                            msvs_base=msvs_base,
                            vs_executable=vs_exec,
                            vs_script=vs_script,
                            vc_version_def=vc_version_def,
                        )

                        msvs_base.register_msvs_instance(msvs_instance)
                        cls.msvs_instances.append(msvs_instance)

                        debug(
                            'msvs_instance=%s',
                            repr(msvs_instance.id_str),
                            extra=cls.debug_extra,
                        )

                    msvs_base.register_msvc_instance(msvc_instance)
                    cls.msvc_instances.append(msvc_instance)

                    debug(
                        'msvc_instance=%s',
                        repr(msvc_instance.id_str),
                        extra=cls.debug_extra,
                    )

            num_instances = len(cls.msvc_instances)
            num_new_instances = num_instances - num_beg_instances

        return num_new_instances


class _VSDetect(Util.AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls) -> None:
        cls.debug_extra = debug_extra(cls)
        cls._reset()

    @classmethod
    def _reset(cls) -> None:
        # volatile: reconstructed when new instances detected
        cls.msvs_manager = None

    @classmethod
    def reset(cls) -> None:
        cls._reset()
        _VSDetectVSWhere.reset()
        _VSDetectRegistry.reset()

    @classmethod
    def detect(cls, vswhere_env):

        num_new_instances = 0
        num_new_instances += _VSDetectVSWhere.detect(vswhere_env)
        num_new_instances += _VSDetectRegistry.detect()

        if num_new_instances > 0 or cls.msvs_manager is None:

            msvc_instances = []
            msvc_instances.extend(_VSDetectVSWhere.msvc_instances)
            msvc_instances.extend(_VSDetectRegistry.msvc_instances)

            msvs_instances = []
            msvs_instances.extend(_VSDetectVSWhere.msvs_instances)
            msvs_instances.extend(_VSDetectRegistry.msvs_instances)

            msvc_installed = MSVCInstalled.factory(
                msvc_instances=msvc_instances,
            )

            msvs_installed = MSVSInstalled.factory(
                msvs_instances=msvs_instances,
            )

            cls.msvs_manager = MSVSManager.factory(
                msvc_installed=msvc_installed,
                msvs_installed=msvs_installed,
            )

        return cls.msvs_manager


def register_reset_func(func) -> None:
    _VSDetectVSWhere.register_reset_func(func)


def msvs_detect(vswhere_env=None):
    vs_manager = _VSDetect.detect(vswhere_env)
    return vs_manager

def msvs_detect_env(env=None):
    vswhere_env = Util.env_query(env, 'VSWHERE', subst=True)
    vs_manager = _VSDetect.detect(vswhere_env)
    return vs_manager


def reset() -> None:
    _VSUtil.reset()
    _VSChannel.reset()
    _VSDetect.reset()

def verify() -> None:

    def _compare_product_sets(set_config, set_local, label) -> None:
        diff = set_config - set_local
        if diff:
            keys = ', '.join([repr(s) for s in sorted(diff, reverse=True)])
            errmsg = f'{label} missing keys: {keys}'
            debug('MSVCInternalError: %s', errmsg)
            raise MSVCInternalError(errmsg)

    vswhere_config = Config.VSWHERE_SUPPORTED_PRODUCTS
    vswhere_local = set(_VSConfig.DETECT_VSWHERE.keys())
    _compare_product_sets(vswhere_config, vswhere_local, '_VSConfig.DETECT_VSWHERE')

    registry_config = Config.REGISTRY_SUPPORTED_PRODUCTS
    registry_local = set(_VSConfig.DETECT_REGISTRY.keys())
    _compare_product_sets(registry_config, registry_local, '_VSConfig.DETECT_REGISTRY')

