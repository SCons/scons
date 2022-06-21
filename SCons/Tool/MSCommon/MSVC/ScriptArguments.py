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
Batch file argument functions for Microsoft Visual C/C++.
"""

import os
import re
import enum

from collections import (
    namedtuple,
)

from ..common import (
    CONFIG_CACHE,
    debug,
)

from . import Util
from . import Config
from . import WinSDK

from .Exceptions import (
    MSVCInternalError,
    MSVCArgumentError,
)

from . import Dispatcher
Dispatcher.register_modulename(__name__)


# Force default SDK and toolset arguments in cache
_SCONS_CACHE_MSVC_FORCE_DEFAULTS = False
if CONFIG_CACHE:
    # SCONS_CACHE_MSVC_FORCE_DEFAULTS is internal and not documented.
    if os.environ.get('SCONS_CACHE_MSVC_FORCE_DEFAULTS') in Config.BOOLEAN_SYMBOLS[True]:
        _SCONS_CACHE_MSVC_FORCE_DEFAULTS = True

# Script argument: boolean True
_ARGUMENT_BOOLEAN_TRUE_LEGACY = (True, '1') # MSVC_UWP_APP
_ARGUMENT_BOOLEAN_TRUE = (True,)

# TODO: verify SDK 10 version folder names 10.0.XXXXX.0 {1,3} last?
re_sdk_version_100 = re.compile(r'^10[.][0-9][.][0-9]{5}[.][0-9]{1}$')
re_sdk_version_81 = re.compile(r'^8[.]1$')

re_sdk_dispatch_map = {
    '10.0': re_sdk_version_100,
    '8.1': re_sdk_version_81,
}

def _verify_re_sdk_dispatch_map():
    debug('')
    for sdk_version in Config.MSVC_SDK_VERSIONS:
        if sdk_version in re_sdk_dispatch_map:
            continue
        err_msg = 'sdk version {} not in re_sdk_dispatch_map'.format(sdk_version)
        raise MSVCInternalError(err_msg)
    return None

# capture msvc version
re_toolset_version = re.compile(r'^(?P<version>[1-9][0-9]?[.][0-9])[0-9.]*$', re.IGNORECASE)

re_toolset_full = re.compile(r'''^(?:
    (?:[1-9][0-9][.][0-9]{1,2})|           # XX.Y    - XX.YY
    (?:[1-9][0-9][.][0-9]{2}[.][0-9]{1,5}) # XX.YY.Z - XX.YY.ZZZZZ
)$''', re.VERBOSE)

re_toolset_140 = re.compile(r'''^(?:
    (?:14[.]0{1,2})|       # 14.0    - 14.00
    (?:14[.]0{2}[.]0{1,5}) # 14.00.0 - 14.00.00000
)$''', re.VERBOSE)

# valid SxS formats will be matched with re_toolset_full: match 3 '.' format
re_toolset_sxs = re.compile(r'^[1-9][0-9][.][0-9]{2}[.][0-9]{2}[.][0-9]{1,2}$')

# MSVC_SCRIPT_ARGS
re_vcvars_uwp = re.compile(r'(?:(?<!\S)|^)(?P<uwp>(?:uwp|store))(?:(?!\S)|$)',re.IGNORECASE)
re_vcvars_sdk = re.compile(r'(?:(?<!\S)|^)(?P<sdk>(?:[1-9][0-9]*[.]\S*))(?:(?!\S)|$)',re.IGNORECASE)
re_vcvars_toolset = re.compile(r'(?:(?<!\S)|^)(?P<toolset_arg>(?:[-]{1,2}|[/])vcvars_ver[=](?P<toolset>\S*))(?:(?!\S)|$)', re.IGNORECASE)
re_vcvars_spectre = re.compile(r'(?:(?<!\S)|^)(?P<spectre_arg>(?:[-]{1,2}|[/])vcvars_spectre_libs[=](?P<spectre>\S*))(?:(?!\S)|$)',re.IGNORECASE)

# Force default sdk argument
_MSVC_FORCE_DEFAULT_SDK = False

# Force default toolset argument
_MSVC_FORCE_DEFAULT_TOOLSET = False

def _msvc_force_default_sdk(force=True):
    global _MSVC_FORCE_DEFAULT_SDK
    _MSVC_FORCE_DEFAULT_SDK = force
    debug('_MSVC_FORCE_DEFAULT_SDK=%s', repr(force))

def _msvc_force_default_toolset(force=True):
    global _MSVC_FORCE_DEFAULT_TOOLSET
    _MSVC_FORCE_DEFAULT_TOOLSET = force
    debug('_MSVC_FORCE_DEFAULT_TOOLSET=%s', repr(force))

if _SCONS_CACHE_MSVC_FORCE_DEFAULTS:
    _msvc_force_default_sdk(True)
    _msvc_force_default_toolset(True)

# MSVC batch file arguments:
#
#     VS2022: UWP, SDK, TOOLSET, SPECTRE
#     VS2019: UWP, SDK, TOOLSET, SPECTRE
#     VS2017: UWP, SDK, TOOLSET, SPECTRE
#     VS2015: UWP, SDK
#
#     MSVC_SCRIPT_ARGS:     VS2015+
#
#     MSVC_UWP_APP:         VS2015+
#     MSVC_SDK_VERSION:     VS2015+
#     MSVC_TOOLSET_VERSION: VS2017+
#     MSVC_SPECTRE_LIBS:    VS2017+

@enum.unique
class SortOrder(enum.IntEnum):
    ARCH = 0     # arch
    UWP = 1      # MSVC_UWP_APP
    SDK = 2      # MSVC_SDK_VERSION
    TOOLSET = 3  # MSVC_TOOLSET_VERSION
    SPECTRE = 4  # MSVC_SPECTRE_LIBS
    USER = 5     # MSVC_SCRIPT_ARGS

VS2019 = Config.MSVS_VERSION_INTERNAL['2019']
VS2017 = Config.MSVS_VERSION_INTERNAL['2017']
VS2015 = Config.MSVS_VERSION_INTERNAL['2015']

MSVC_VERSION_ARGS_DEFINITION = namedtuple('MSVCVersionArgsDefinition', [
    'version', # fully qualified msvc version (e.g., '14.1Exp')
    'vs_def',
])

def _msvc_version(version):

    verstr = Util.get_version_prefix(version)
    vs_def = Config.MSVC_VERSION_INTERNAL[verstr]

    version_args = MSVC_VERSION_ARGS_DEFINITION(
        version = version,
        vs_def = vs_def,
    )

    return version_args

def _msvc_script_argument_uwp(env, msvc, arglist):

    uwp_app = env['MSVC_UWP_APP']
    debug('MSVC_VERSION=%s, MSVC_UWP_APP=%s', repr(msvc.version), repr(uwp_app))

    if not uwp_app:
        return None

    if uwp_app not in _ARGUMENT_BOOLEAN_TRUE_LEGACY:
        return None

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2015.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: msvc version constraint: %s < %s VS2015',
            repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
            repr(VS2015.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_UWP_APP ({}) constraint violation: MSVC_VERSION {} < {} VS2015".format(
            repr(uwp_app), repr(msvc.version), repr(VS2015.vc_buildtools_def.vc_version)
        )
        raise MSVCArgumentError(err_msg)

    # VS2017+ rewrites uwp => store for 14.0 toolset
    uwp_arg = msvc.vs_def.vc_uwp

    # store/uwp may not be fully installed
    argpair = (SortOrder.UWP, uwp_arg)
    arglist.append(argpair)

    return uwp_arg

def _user_script_argument_uwp(env, uwp, user_argstr):

    matches = [m for m in re_vcvars_uwp.finditer(user_argstr)]
    if not matches:
        return None

    if len(matches) > 1:
        debug('multiple uwp declarations: MSVC_SCRIPT_ARGS=%s', repr(user_argstr))
        err_msg = "multiple uwp declarations: MSVC_SCRIPT_ARGS={}".format(repr(user_argstr))
        raise MSVCArgumentError(err_msg)

    if not uwp:
        return None

    env_argstr = env.get('MSVC_UWP_APP','')
    debug('multiple uwp declarations: MSVC_UWP_APP=%s, MSVC_SCRIPT_ARGS=%s', repr(env_argstr), repr(user_argstr))

    err_msg = "multiple uwp declarations: MSVC_UWP_APP={} and MSVC_SCRIPT_ARGS={}".format(
        repr(env_argstr), repr(user_argstr)
    )

    raise MSVCArgumentError(err_msg)

def _msvc_script_argument_sdk_constraints(msvc, sdk_version):

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2015.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: msvc_version constraint: %s < %s VS2015',
            repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
            repr(VS2015.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_SDK_VERSION ({}) constraint violation: MSVC_VERSION {} < {} VS2015".format(
            repr(sdk_version), repr(msvc.version), repr(VS2015.vc_buildtools_def.vc_version)
        )
        return err_msg

    for msvc_sdk_version in msvc.vs_def.vc_sdk_versions:
        re_sdk_version = re_sdk_dispatch_map[msvc_sdk_version]
        if re_sdk_version.match(sdk_version):
            debug('valid: sdk_version=%s', repr(sdk_version))
            return None

    debug('invalid: method exit: sdk_version=%s', repr(sdk_version))
    err_msg = "MSVC_SDK_VERSION ({}) is not supported".format(repr(sdk_version))
    return err_msg

def _msvc_script_argument_sdk(env, msvc, platform_type, arglist):

    sdk_version = env['MSVC_SDK_VERSION']
    debug(
        'MSVC_VERSION=%s, MSVC_SDK_VERSION=%s, platform_type=%s',
        repr(msvc.version), repr(sdk_version), repr(platform_type)
    )

    if not sdk_version:
        return None

    err_msg = _msvc_script_argument_sdk_constraints(msvc, sdk_version)
    if err_msg:
        raise MSVCArgumentError(err_msg)

    sdk_list = WinSDK.get_sdk_version_list(msvc.vs_def.vc_sdk_versions, platform_type)

    if sdk_version not in sdk_list:
        err_msg = "MSVC_SDK_VERSION {} not found for platform type {}".format(
            repr(sdk_version), repr(platform_type)
        )
        raise MSVCArgumentError(err_msg)

    argpair = (SortOrder.SDK, sdk_version)
    arglist.append(argpair)

    return sdk_version

def _msvc_script_default_sdk(env, msvc, platform_type, arglist):

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2015.vc_buildtools_def.vc_version_numeric:
        return None

    sdk_list = WinSDK.get_sdk_version_list(msvc.vs_def.vc_sdk_versions, platform_type)
    if not len(sdk_list):
        return None

    sdk_default = sdk_list[0]

    debug(
        'MSVC_VERSION=%s, sdk_default=%s, platform_type=%s',
        repr(msvc.version), repr(sdk_default), repr(platform_type)
    )

    argpair = (SortOrder.SDK, sdk_default)
    arglist.append(argpair)

    return sdk_default

def _user_script_argument_sdk(env, sdk_version, user_argstr):

    matches = [m for m in re_vcvars_sdk.finditer(user_argstr)]
    if not matches:
        return None

    if len(matches) > 1:
        debug('multiple sdk version declarations: MSVC_SCRIPT_ARGS=%s', repr(user_argstr))
        err_msg = "multiple sdk version declarations: MSVC_SCRIPT_ARGS={}".format(repr(user_argstr))
        raise MSVCArgumentError(err_msg)

    if not sdk_version:
        user_sdk = matches[0].group('sdk')
        return user_sdk

    env_argstr = env.get('MSVC_SDK_VERSION','')
    debug('multiple sdk version declarations: MSVC_SDK_VERSION=%s, MSVC_SCRIPT_ARGS=%s', repr(env_argstr), repr(user_argstr))

    err_msg = "multiple sdk version declarations: MSVC_SDK_VERSION={} and MSVC_SCRIPT_ARGS={}".format(
        repr(env_argstr), repr(user_argstr)
    )

    raise MSVCArgumentError(err_msg)

def _msvc_read_toolset_file(msvc, filename):
    toolset_version = None
    try:
        with open(filename) as f:
            toolset_version = f.readlines()[0].strip()
        debug(
            'msvc_version=%s, filename=%s, toolset_version=%s',
            repr(msvc.version), repr(filename), repr(toolset_version)
        )
    except OSError:
        debug('OSError: msvc_version=%s, filename=%s', repr(msvc.version), repr(filename))
    except IndexError:
        debug('IndexError: msvc_version=%s, filename=%s', repr(msvc.version), repr(filename))
    return toolset_version

def _msvc_read_toolset_folders(msvc, vc_dir):

    toolsets_sxs = {}
    toolsets_full = []

    build_dir = os.path.join(vc_dir, "Auxiliary", "Build")
    sxs_toolsets = [f.name for f in os.scandir(build_dir) if f.is_dir()]
    for sxs_toolset in sxs_toolsets:
        filename = 'Microsoft.VCToolsVersion.{}.txt'.format(sxs_toolset)
        filepath = os.path.join(build_dir, sxs_toolset, filename)
        debug('sxs toolset: check file=%s', repr(filepath))
        if os.path.exists(filepath):
            toolset_version = _msvc_read_toolset_file(msvc, filepath)
            if not toolset_version:
                continue
            toolsets_sxs[sxs_toolset] = toolset_version
            debug(
                'sxs toolset: msvc_version=%s, sxs_version=%s, toolset_version=%s',
                repr(msvc.version), repr(sxs_toolset), toolset_version
            )

    toolset_dir = os.path.join(vc_dir, "Tools", "MSVC")
    toolsets = [f.name for f in os.scandir(toolset_dir) if f.is_dir()]
    for toolset_version in toolsets:
        binpath = os.path.join(toolset_dir, toolset_version, "bin")
        debug('toolset: check binpath=%s', repr(binpath))
        if os.path.exists(binpath):
            toolsets_full.append(toolset_version)
            debug(
                'toolset: msvc_version=%s, toolset_version=%s',
                repr(msvc.version), repr(toolset_version)
            )

    toolsets_full.sort(reverse=True)
    debug('msvc_version=%s, toolsets=%s', repr(msvc.version), repr(toolsets_full))

    return toolsets_sxs, toolsets_full

def _msvc_read_toolset_default(msvc, vc_dir):

    build_dir = os.path.join(vc_dir, "Auxiliary", "Build")

    # VS2019+
    filename = "Microsoft.VCToolsVersion.{}.default.txt".format(msvc.vs_def.vc_buildtools_def.vc_buildtools)
    filepath = os.path.join(build_dir, filename)

    debug('default toolset: check file=%s', repr(filepath))
    if os.path.exists(filepath):
        toolset_buildtools = _msvc_read_toolset_file(msvc, filepath)
        if toolset_buildtools:
            return toolset_buildtools

    # VS2017+
    filename = "Microsoft.VCToolsVersion.default.txt"
    filepath = os.path.join(build_dir, filename)

    debug('default toolset: check file=%s', repr(filepath))
    if os.path.exists(filepath):
        toolset_default = _msvc_read_toolset_file(msvc, filepath)
        if toolset_default:
            return toolset_default

    return None

_toolset_version_cache = {}
_toolset_default_cache = {}

def _reset_toolset_cache():
    global _toolset_version_cache
    global _toolset_default_cache
    debug('reset: toolset cache')
    _toolset_version_cache = {}
    _toolset_default_cache = {}

def _msvc_version_toolsets(msvc, vc_dir):

    if msvc.version in _toolset_version_cache:
        toolsets_sxs, toolsets_full = _toolset_version_cache[msvc.version]
    else:
        toolsets_sxs, toolsets_full = _msvc_read_toolset_folders(msvc, vc_dir)
        _toolset_version_cache[msvc.version] = toolsets_sxs, toolsets_full

    return toolsets_sxs, toolsets_full

def _msvc_default_toolset(msvc, vc_dir):

    if msvc.version in _toolset_default_cache:
        toolset_default = _toolset_default_cache[msvc.version]
    else:
        toolset_default = _msvc_read_toolset_default(msvc, vc_dir)
        _toolset_default_cache[msvc.version] = toolset_default

    return toolset_default

def _msvc_version_toolset_vcvars(msvc, vc_dir, toolset_version):

    if toolset_version == '14.0':
        return toolset_version

    toolsets_sxs, toolsets_full = _msvc_version_toolsets(msvc, vc_dir)

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric == VS2019.vc_buildtools_def.vc_version_numeric:
        # necessary to detect toolset not found
        if toolset_version == '14.28.16.8':
            new_toolset_version = '14.28'
            # VS2019\Common7\Tools\vsdevcmd\ext\vcvars.bat AzDO Bug#1293526
            #     special handling of the 16.8 SxS toolset, use VC\Auxiliary\Build\14.28 directory and SxS files
            #     if SxS version 14.28 not present/installed, fallback selection of toolset VC\Tools\MSVC\14.28.nnnnn.
            debug(
                'rewrite toolset_version=%s => toolset_version=%s',
                repr(toolset_version), repr(new_toolset_version)
            )
            toolset_version = new_toolset_version

    if toolset_version in toolsets_sxs:
        toolset_vcvars = toolsets_sxs[toolset_version]
        return toolset_vcvars

    for toolset_full in toolsets_full:
        if toolset_full.startswith(toolset_version):
            toolset_vcvars = toolset_full
            return toolset_vcvars

    return None

def _msvc_script_argument_toolset_constraints(msvc, toolset_version):

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2017.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: msvc version constraint: %s < %s VS2017',
            repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
            repr(VS2017.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: MSVC_VERSION {} < {} VS2017".format(
            repr(toolset_version), repr(msvc.version), repr(VS2017.vc_buildtools_def.vc_version)
        )
        return err_msg

    m = re_toolset_version.match(toolset_version)
    if not m:
        debug('invalid: re_toolset_version: toolset_version=%s', repr(toolset_version))
        err_msg = 'MSVC_TOOLSET_VERSION {} format is not supported'.format(
            repr(toolset_version)
        )
        return err_msg

    toolset_ver = m.group('version')
    toolset_vernum = float(toolset_ver)

    if toolset_vernum < VS2015.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: toolset version constraint: %s < %s VS2015',
            repr(toolset_vernum), repr(VS2015.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} < {} VS2015".format(
            repr(toolset_version), repr(toolset_ver), repr(VS2015.vc_buildtools_def.vc_version)
        )
        return err_msg

    if toolset_vernum > msvc.vs_def.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: toolset version constraint: toolset %s > %s msvc',
            repr(toolset_vernum), repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} > {} MSVC_VERSION".format(
            repr(toolset_version), repr(toolset_ver), repr(msvc.version)
        )
        return err_msg

    if toolset_vernum == VS2015.vc_buildtools_def.vc_version_numeric:
        # tooset = 14.0
        if re_toolset_full.match(toolset_version):
            if not re_toolset_140.match(toolset_version):
                debug(
                    'invalid: toolset version 14.0 constraint: %s != 14.0',
                    repr(toolset_version)
                )
                err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} != '14.0'".format(
                    repr(toolset_version), repr(toolset_version)
                )
                return err_msg
            return None

    if re_toolset_full.match(toolset_version):
        debug('valid: re_toolset_full: toolset_version=%s', repr(toolset_version))
        return None

    if re_toolset_sxs.match(toolset_version):
        debug('valid: re_toolset_sxs: toolset_version=%s', repr(toolset_version))
        return None

    debug('invalid: method exit: toolset_version=%s', repr(toolset_version))
    err_msg = "MSVC_TOOLSET_VERSION ({}) format is not supported".format(repr(toolset_version))
    return err_msg

def _msvc_script_argument_toolset(env, msvc, vc_dir, arglist):

    toolset_version = env['MSVC_TOOLSET_VERSION']
    debug('MSVC_VERSION=%s, MSVC_TOOLSET_VERSION=%s', repr(msvc.version), repr(toolset_version))

    if not toolset_version:
        return None

    err_msg = _msvc_script_argument_toolset_constraints(msvc, toolset_version)
    if err_msg:
        raise MSVCArgumentError(err_msg)

    if toolset_version.startswith('14.0') and len(toolset_version) > len('14.0'):
        new_toolset_version = '14.0'
        debug(
            'rewrite toolset_version=%s => toolset_version=%s',
            repr(toolset_version), repr(new_toolset_version)
        )
        toolset_version = new_toolset_version

    toolset_vcvars = _msvc_version_toolset_vcvars(msvc, vc_dir, toolset_version)
    debug(
        'toolset: toolset_version=%s, toolset_vcvars=%s',
        repr(toolset_version), repr(toolset_vcvars)
    )

    if not toolset_vcvars:
        err_msg = "MSVC_TOOLSET_VERSION {} not found for MSVC_VERSION {}".format(
            repr(toolset_version), repr(msvc.version)
        )
        raise MSVCArgumentError(err_msg)

    argpair = (SortOrder.TOOLSET, '-vcvars_ver={}'.format(toolset_vcvars))
    arglist.append(argpair)

    return toolset_vcvars

def _msvc_script_default_toolset(env, msvc, vc_dir, arglist):

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2017.vc_buildtools_def.vc_version_numeric:
        return None

    toolset_default = _msvc_default_toolset(msvc, vc_dir)
    if not toolset_default:
        return None

    debug('MSVC_VERSION=%s, toolset_default=%s', repr(msvc.version), repr(toolset_default))

    argpair = (SortOrder.TOOLSET, '-vcvars_ver={}'.format(toolset_default))
    arglist.append(argpair)

    return toolset_default

def _user_script_argument_toolset(env, toolset_version, user_argstr):

    matches = [m for m in re_vcvars_toolset.finditer(user_argstr)]
    if not matches:
        return None

    if len(matches) > 1:
        debug('multiple toolset version declarations: MSVC_SCRIPT_ARGS=%s', repr(user_argstr))
        err_msg = "multiple toolset version declarations: MSVC_SCRIPT_ARGS={}".format(repr(user_argstr))
        raise MSVCArgumentError(err_msg)

    if not toolset_version:
        user_toolset = matches[0].group('toolset')
        return user_toolset

    env_argstr = env.get('MSVC_TOOLSET_VERSION','')
    debug('multiple toolset version declarations: MSVC_TOOLSET_VERSION=%s, MSVC_SCRIPT_ARGS=%s', repr(env_argstr), repr(user_argstr))

    err_msg = "multiple toolset version declarations: MSVC_TOOLSET_VERSION={} and MSVC_SCRIPT_ARGS={}".format(
        repr(env_argstr), repr(user_argstr)
    )

    raise MSVCArgumentError(err_msg)

def _msvc_script_argument_spectre(env, msvc, arglist):

    spectre_libs = env['MSVC_SPECTRE_LIBS']
    debug('MSVC_VERSION=%s, MSVC_SPECTRE_LIBS=%s', repr(msvc.version), repr(spectre_libs))

    if not spectre_libs:
        return None

    if spectre_libs not in _ARGUMENT_BOOLEAN_TRUE:
        return None

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2017.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: msvc version constraint: %s < %s VS2017',
            repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
            repr(VS2017.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_SPECTRE_LIBS ({}) constraint violation: MSVC_VERSION {} < {} VS2017".format(
            repr(spectre_libs), repr(msvc.version), repr(VS2017.vc_buildtools_def.vc_version)
        )
        raise MSVCArgumentError(err_msg)

    spectre_arg = 'spectre'

    # spectre libs may not be installed
    argpair = (SortOrder.SPECTRE, '-vcvars_spectre_libs={}'.format(spectre_arg))
    arglist.append(argpair)

    return spectre_arg

def _msvc_script_argument_user(env, msvc, arglist):

    # subst None -> empty string
    script_args = env.subst('$MSVC_SCRIPT_ARGS')
    debug('MSVC_VERSION=%s, MSVC_SCRIPT_ARGS=%s', repr(msvc.version), repr(script_args))

    if not script_args:
        return None

    if msvc.vs_def.vc_buildtools_def.vc_version_numeric < VS2015.vc_buildtools_def.vc_version_numeric:
        debug(
            'invalid: msvc version constraint: %s < %s VS2015',
            repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
            repr(VS2015.vc_buildtools_def.vc_version_numeric)
        )
        err_msg = "MSVC_SCRIPT_ARGS ({}) constraint violation: MSVC_VERSION {} < {} VS2015".format(
            repr(script_args), repr(msvc.version), repr(VS2015.vc_buildtools_def.vc_version)
        )
        raise MSVCArgumentError(err_msg)

    # user arguments are not validated
    argpair = (SortOrder.USER, script_args)
    arglist.append(argpair)

    return script_args

def _user_script_argument_spectre(env, spectre, user_argstr):

    matches = [m for m in re_vcvars_spectre.finditer(user_argstr)]
    if not matches:
        return None

    if len(matches) > 1:
        debug('multiple spectre declarations: MSVC_SCRIPT_ARGS=%s', repr(user_argstr))
        err_msg = "multiple spectre declarations: MSVC_SCRIPT_ARGS={}".format(repr(user_argstr))
        raise MSVCArgumentError(err_msg)

    if not spectre:
        return None

    env_argstr = env.get('MSVC_SPECTRE_LIBS','')
    debug('multiple spectre declarations: MSVC_SPECTRE_LIBS=%s, MSVC_SCRIPT_ARGS=%s', repr(env_argstr), repr(user_argstr))

    err_msg = "multiple spectre declarations: MSVC_SPECTRE_LIBS={} and MSVC_SCRIPT_ARGS={}".format(
        repr(env_argstr), repr(user_argstr)
    )

    raise MSVCArgumentError(err_msg)

def msvc_script_arguments(env, version, vc_dir, arg):

    arglist = []

    msvc = _msvc_version(version)

    if arg:
        argpair = (SortOrder.ARCH, arg)
        arglist.append(argpair)

    if 'MSVC_SCRIPT_ARGS' in env:
        user_argstr = _msvc_script_argument_user(env, msvc, arglist)
    else:
        user_argstr = None

    if 'MSVC_UWP_APP' in env:
        uwp = _msvc_script_argument_uwp(env, msvc, arglist)
    else:
        uwp = None

    if user_argstr:
        _user_script_argument_uwp(env, uwp, user_argstr)

    platform_type = 'uwp' if uwp else 'desktop'

    if 'MSVC_SDK_VERSION' in env:
        sdk_version = _msvc_script_argument_sdk(env, msvc, platform_type, arglist)
    else:
        sdk_version = None

    if user_argstr:
        user_sdk = _user_script_argument_sdk(env, sdk_version, user_argstr)
    else:
        user_sdk = None

    if _MSVC_FORCE_DEFAULT_SDK:
        if not sdk_version and not user_sdk:
            sdk_version = _msvc_script_default_sdk(env, msvc, platform_type, arglist)

    if 'MSVC_TOOLSET_VERSION' in env:
        toolset_version = _msvc_script_argument_toolset(env, msvc, vc_dir, arglist)
    else:
        toolset_version = None

    if user_argstr:
        user_toolset = _user_script_argument_toolset(env, toolset_version, user_argstr)
    else:
        user_toolset = None

    if _MSVC_FORCE_DEFAULT_TOOLSET:
        if not toolset_version and not user_toolset:
            toolset_version = _msvc_script_default_toolset(env, msvc, vc_dir, arglist)

    if 'MSVC_SPECTRE_LIBS' in env:
        spectre = _msvc_script_argument_spectre(env, msvc, arglist)
    else:
        spectre = None

    if user_argstr:
        _user_script_argument_spectre(env, spectre, user_argstr)

    if arglist:
        arglist.sort()
        argstr = ' '.join([argpair[-1] for argpair in arglist]).strip()
    else:
        argstr = ''

    debug('arguments: %s', repr(argstr))
    return argstr

def reset():
    debug('')
    _reset_toolset_cache()

def verify():
    debug('')
    _verify_re_sdk_dispatch_map()

