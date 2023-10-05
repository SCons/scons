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
Version kind categorization for Microsoft Visual C/C++.
"""

import os
import re

from collections import (
    namedtuple,
)

from ..common import (
    debug,
)

from . import Config
from . import Registry
from . import Util

from . import Dispatcher
Dispatcher.register_modulename(__name__)


BITFIELD_KIND_DEVELOP     = 0b_1000
BITFIELD_KIND_EXPRESS     = 0b_0100
BITFIELD_KIND_EXPRESS_WIN = 0b_0010
BITFIELD_KIND_EXPRESS_WEB = 0b_0001

_BITFIELD_KIND_VSEXECUTABLE = (BITFIELD_KIND_DEVELOP, BITFIELD_KIND_EXPRESS)

VCBinary = namedtuple("VCBinary", [
    'program',
    'bitfield',
])

# IDE binaries

IDE_PROGRAM_DEVENV_COM = VCBinary(
    program='devenv.com',
    bitfield=BITFIELD_KIND_DEVELOP,
)

IDE_PROGRAM_MSDEV_COM = VCBinary(
    program='msdev.com',
    bitfield=BITFIELD_KIND_DEVELOP,
)

IDE_PROGRAM_WDEXPRESS_EXE = VCBinary(
    program='WDExpress.exe',
    bitfield=BITFIELD_KIND_EXPRESS,
)

IDE_PROGRAM_VCEXPRESS_EXE = VCBinary(
    program='VCExpress.exe',
    bitfield=BITFIELD_KIND_EXPRESS,
)

IDE_PROGRAM_VSWINEXPRESS_EXE = VCBinary(
    program='VSWinExpress.exe',
    bitfield=BITFIELD_KIND_EXPRESS_WIN,
)

IDE_PROGRAM_VWDEXPRESS_EXE = VCBinary(
    program='VWDExpress.exe',
    bitfield=BITFIELD_KIND_EXPRESS_WEB,
)

# detection configuration

VCDetectConfig = namedtuple("VCDetectConfig", [
    'root',  # relpath from pdir to vsroot
    'path',  # vsroot to ide dir
    'programs',  # ide binaries
])

# detected IDE binaries

VCDetectedBinaries = namedtuple("VCDetectedBinaries", [
    'bitfields',  # detect values
    'have_dev',  # develop ide binary
    'have_exp',  # express ide binary
    'have_exp_win',  # express windows ide binary
    'have_exp_web',  # express web ide binary
    'vs_exec',  # vs binary
])

def _msvc_dir_detect_binaries(vc_dir, detect):

    vs_exec = None

    vs_dir = os.path.join(vc_dir, detect.root)
    ide_path = os.path.join(vs_dir, detect.path)

    bitfields = 0b_0000
    for ide_program in detect.programs:
        prog = os.path.join(ide_path, ide_program.program)
        if not os.path.exists(prog):
            continue
        bitfields |= ide_program.bitfield
        if vs_exec:
            continue
        if ide_program.bitfield not in _BITFIELD_KIND_VSEXECUTABLE:
            continue
        vs_exec = prog

    have_dev = bool(bitfields & BITFIELD_KIND_DEVELOP)
    have_exp = bool(bitfields & BITFIELD_KIND_EXPRESS)
    have_exp_win = bool(bitfields & BITFIELD_KIND_EXPRESS_WIN)
    have_exp_web = bool(bitfields & BITFIELD_KIND_EXPRESS_WEB)

    binaries_t = VCDetectedBinaries(
        bitfields=bitfields,
        have_dev=have_dev,
        have_exp=have_exp,
        have_exp_win=have_exp_win,
        have_exp_web=have_exp_web,
        vs_exec=vs_exec,
    )

    debug(
        'vs_dir=%s, dev=%s, exp=%s, exp_win=%s, exp_web=%s, vs_exec=%s, vc_dir=%s',
        repr(vs_dir),
        binaries_t.have_dev, binaries_t.have_exp,
        binaries_t.have_exp_win, binaries_t.have_exp_web,
        repr(binaries_t.vs_exec),
        repr(vc_dir)
    )

    return vs_dir, binaries_t

def msvc_dir_vswhere(vc_dir, detect_t):

    _, binaries_t = _msvc_dir_detect_binaries(vc_dir, detect_t)

    return binaries_t.vs_exec

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

def _vs_buildtools_2015_vcvars(vcvars_file):
    have_buildtools_vcvars = False
    with open(vcvars_file) as fh:
        for line in fh:
            if _VS2015BT_VCVARS_BUILDTOOLS.match(line):
                have_buildtools_vcvars = True
                break
            if _VS2015BT_VCVARS_STOP.match(line):
                break
    return have_buildtools_vcvars

def _vs_buildtools_2015(vs_dir, vc_dir):

    is_buildtools = False

    do_once = True
    while do_once:
        do_once = False

        buildtools_file = os.path.join(vs_dir, _VS2015BT_PATH)
        have_buildtools = os.path.exists(buildtools_file)
        debug('have_buildtools=%s', have_buildtools)
        if not have_buildtools:
            break

        vcvars_file = os.path.join(vc_dir, 'vcvarsall.bat')
        have_vcvars = os.path.exists(vcvars_file)
        debug('have_vcvars=%s', have_vcvars)
        if not have_vcvars:
            break

        have_buildtools_vcvars = _vs_buildtools_2015_vcvars(vcvars_file)
        debug('have_buildtools_vcvars=%s', have_buildtools_vcvars)
        if not have_buildtools_vcvars:
            break

        is_buildtools = True

    debug('is_buildtools=%s', is_buildtools)
    return is_buildtools

_VS2015EXP_VCVARS_LIBPATH = re.compile(
    ''.join([
        r'^\s*\@if\s+exist\s+\"\%VCINSTALLDIR\%LIB\\store\\(amd64|arm)"\s+',
        r'set (LIB|LIBPATH)=\%VCINSTALLDIR\%LIB\\store\\(amd64|arm);.*\%(LIB|LIBPATH)\%\s*$'
    ]),
    re.IGNORECASE
)

_VS2015EXP_VCVARS_STOP = re.compile(r'^\s*[:]GetVSCommonToolsDir\s*$', re.IGNORECASE)

def _vs_express_2015_vcvars(vcvars_file):
    n_libpath = 0
    with open(vcvars_file) as fh:
        for line in fh:
            if _VS2015EXP_VCVARS_LIBPATH.match(line):
                n_libpath += 1
            elif _VS2015EXP_VCVARS_STOP.match(line):
                break
    have_uwp_fix = n_libpath >= 2
    return have_uwp_fix

def _vs_express_2015(vc_dir):

    have_uwp_amd64 = False
    have_uwp_arm = False

    vcvars_file = os.path.join(vc_dir, r'vcvarsall.bat')
    if os.path.exists(vcvars_file):

        vcvars_file = os.path.join(vc_dir, r'bin\x86_amd64\vcvarsx86_amd64.bat')
        if os.path.exists(vcvars_file):
            have_uwp_fix = _vs_express_2015_vcvars(vcvars_file)
            if have_uwp_fix:
                have_uwp_amd64 = True

        vcvars_file = os.path.join(vc_dir, r'bin\x86_arm\vcvarsx86_arm.bat')
        if os.path.exists(vcvars_file):
            have_uwp_fix = _vs_express_2015_vcvars(vcvars_file)
            if have_uwp_fix:
                have_uwp_arm = True

    debug('have_uwp_amd64=%s, have_uwp_arm=%s', have_uwp_amd64, have_uwp_arm)
    return have_uwp_amd64, have_uwp_arm

# winsdk installed 2010 [7.1], 2008 [7.0, 6.1] folders

_REGISTRY_WINSDK_VERSIONS = {'10.0', '9.0'}

def _msvc_dir_is_winsdk_only(vc_dir, msvc_version):

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

    if msvc_version not in _REGISTRY_WINSDK_VERSIONS:

        is_sdk = False

        debug('is_sdk=%s, msvc_version=%s', is_sdk, repr(msvc_version))

    else:

        vc_suffix = Registry.vstudio_sxs_vc7(msvc_version)
        vc_qresults = [record[0] for record in Registry.microsoft_query_paths(vc_suffix)]
        vc_regdir = vc_qresults[0] if vc_qresults else None

        if vc_regdir != vc_dir:
            # registry vc path is not the current vc dir

            is_sdk = False

            debug(
                'is_sdk=%s, msvc_version=%s, vc_dir=%s, vc_regdir=%s',
                is_sdk, repr(msvc_version), repr(vc_dir), repr(vc_regdir)
            )

        else:
            # registry vc dir is the current vc root

            vs_suffix = Registry.vstudio_sxs_vs7(msvc_version)
            vs_qresults = [record[0] for record in Registry.microsoft_query_paths(vs_suffix)]
            vs_dir = vs_qresults[0] if vs_qresults else None

            is_sdk = bool(not vs_dir and vc_dir)

            debug(
                'is_sdk=%s, msvc_version=%s, vc_dir=%s, vs_dir=%s',
                is_sdk, repr(msvc_version), repr(vc_dir), repr(vs_dir)
            )

    return is_sdk

def msvc_dir_registry(vc_dir, detect_t, msvc_version, is_vcforpython, vs_version):

    vc_feature_map = {}

    vs_dir, binaries_t = _msvc_dir_detect_binaries(vc_dir, detect_t)

    if binaries_t.have_dev:
        vs_component_def = Config.REGISTRY_COMPONENT_DEVELOP
    elif binaries_t.have_exp:
        vs_component_def = Config.REGISTRY_COMPONENT_EXPRESS
    elif msvc_version == '9.0' and is_vcforpython:
        vs_component_def = Config.REGISTRY_COMPONENT_PYTHON
    elif binaries_t.have_exp_win:
        vs_component_def = None
    elif binaries_t.have_exp_web:
        vs_component_def = None
    elif _msvc_dir_is_winsdk_only(vc_dir, msvc_version):
        vs_component_def = None
    else:
        vs_component_def = Config.REGISTRY_COMPONENT_CMDLINE

    if vs_component_def and msvc_version == '14.0':

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

            if _vs_buildtools_2015(vs_dir, vc_dir):
                vs_component_def = Config.REGISTRY_COMPONENT_BUILDTOOLS

        elif vs_component_def == Config.REGISTRY_COMPONENT_EXPRESS:

            have_uwp_amd64, have_uwp_arm = _vs_express_2015(vc_dir)

            uwp_target_is_supported = {
                'x86': True,
                'amd64': have_uwp_amd64,
                'arm': have_uwp_arm,
            }

            vc_feature_map['uwp_target_is_supported'] = uwp_target_is_supported

    debug(
        'msvc_version=%s, vs_component=%s, vc_dir=%s, vc_feature_map=%s',
        repr(msvc_version),
        repr(vs_component_def.vs_componentid_def.vs_component_id) if vs_component_def else None,
        repr(vc_dir),
        repr(vc_feature_map),
    )

    return vs_component_def, vs_dir, binaries_t.vs_exec, vc_feature_map

