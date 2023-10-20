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
Constants and initialized data structures for Microsoft Visual C/C++.
"""

from collections import (
    namedtuple,
)

from . import Util

from .Exceptions import (
    MSVCInternalError,
)

from . import Dispatcher
Dispatcher.register_modulename(__name__)

# MSVC 9.0 preferred query order:
#     True:  VCForPython, VisualStudio
#     False: VisualStudio, VCForPython
_VC90_Prefer_VCForPython = True

UNDEFINED = object()

BOOLEAN_SYMBOLS = {}
BOOLEAN_EXTERNAL = {}

for bool_val, symbol_list, symbol_case_list in [
    (False, (False, 0, '0', None, ''), ('False', 'No',  'F', 'N')),
    (True,  (True,  1, '1'),           ('True',  'Yes', 'T', 'Y')),
]:
    BOOLEAN_SYMBOLS[bool_val] = list(symbol_list)
    for symbol in symbol_case_list:
        BOOLEAN_SYMBOLS[bool_val].extend([symbol, symbol.lower(), symbol.upper()])

    for symbol in BOOLEAN_SYMBOLS[bool_val]:
        BOOLEAN_EXTERNAL[symbol] = bool_val

MSVC_PLATFORM_DEFINITION = namedtuple('MSVCPlatform', [
    'vc_platform',
    'is_uwp',
])

MSVC_PLATFORM_DEFINITION_LIST = []

MSVC_PLATFORM_INTERNAL = {}
MSVC_PLATFORM_EXTERNAL = {}

for vc_platform, is_uwp in [
    ('Desktop', False),
    ('UWP', True),
]:

    vc_platform_def = MSVC_PLATFORM_DEFINITION(
        vc_platform = vc_platform,
        is_uwp = is_uwp,
    )

    MSVC_PLATFORM_DEFINITION_LIST.append(vc_platform_def)

    MSVC_PLATFORM_INTERNAL[vc_platform] = vc_platform_def

    for symbol in [vc_platform, vc_platform.lower(), vc_platform.upper()]:
        MSVC_PLATFORM_EXTERNAL[symbol] = vc_platform_def

MSVC_RUNTIME_DEFINITION = namedtuple('MSVCRuntime', [
    'vc_runtime',
    'vc_runtime_numeric',
    'vc_runtime_alias_list',
])

MSVC_RUNTIME_DEFINITION_LIST = []

MSVC_RUNTIME_INTERNAL = {}
MSVC_RUNTIME_EXTERNAL = {}

MSVC_RUNTIME_VSPRODUCTDEF_LIST_MAP = {}

for vc_runtime, vc_runtime_numeric, vc_runtime_alias_list in [
    ('140', 140, ['ucrt']),
    ('120', 120, ['msvcr120']),
    ('110', 110, ['msvcr110']),
    ('100', 100, ['msvcr100']),
    ('90',   90, ['msvcr90']),
    ('80',   80, ['msvcr80']),
    ('71',   71, ['msvcr71']),
    ('70',   70, ['msvcr70']),
    ('60',   60, ['msvcrt']),
]:
    vc_runtime_def = MSVC_RUNTIME_DEFINITION(
        vc_runtime = vc_runtime,
        vc_runtime_numeric = vc_runtime_numeric,
        vc_runtime_alias_list = tuple(vc_runtime_alias_list),
    )

    MSVC_RUNTIME_DEFINITION_LIST.append(vc_runtime_def)

    MSVC_RUNTIME_INTERNAL[vc_runtime] = vc_runtime_def
    MSVC_RUNTIME_EXTERNAL[vc_runtime] = vc_runtime_def

    for vc_runtime_alias in vc_runtime_alias_list:
        MSVC_RUNTIME_EXTERNAL[vc_runtime_alias] = vc_runtime_def

    MSVC_RUNTIME_VSPRODUCTDEF_LIST_MAP[vc_runtime_def] = []

MSVC_BUILDTOOLS_DEFINITION = namedtuple('MSVCBuildTools', [
    'vc_buildtools',
    'vc_buildtools_numeric',
    'vc_version',
    'vc_version_numeric',
    'cl_version',
    'cl_version_numeric',
    'vc_runtime_def',
    'vc_istoolset',
])

MSVC_BUILDTOOLS_DEFINITION_LIST = []

MSVC_BUILDTOOLS_INTERNAL = {}
MSVC_BUILDTOOLS_EXTERNAL = {}

VC_VERSION_MAP = {}

for vc_buildtools, vc_version, cl_version, vc_runtime, vc_istoolset in [
    ('v143', '14.3', '19.3', '140', True),
    ('v142', '14.2', '19.2', '140', True),
    ('v141', '14.1', '19.1', '140', True),
    ('v140', '14.0', '19.0', '140', True),
    ('v120', '12.0', '18.0', '120', False),
    ('v110', '11.0', '17.0', '110', False),
    ('v100', '10.0', '16.0', '100', False),
    ('v90',   '9.0', '15.0',  '90', False),
    ('v80',   '8.0', '14.0',  '80', False),
    ('v71',   '7.1', '13.1',  '71', False),
    ('v70',   '7.0', '13.0',  '70', False),
    ('v60',   '6.0', '12.0',  '60', False),
]:

    vc_runtime_def = MSVC_RUNTIME_INTERNAL[vc_runtime]

    vc_buildtools_def = MSVC_BUILDTOOLS_DEFINITION(
        vc_buildtools = vc_buildtools,
        vc_buildtools_numeric = int(vc_buildtools[1:]),
        vc_version = vc_version,
        vc_version_numeric = float(vc_version),
        cl_version = cl_version,
        cl_version_numeric = float(cl_version),
        vc_runtime_def = vc_runtime_def,
        vc_istoolset = vc_istoolset,
    )

    MSVC_BUILDTOOLS_DEFINITION_LIST.append(vc_buildtools_def)

    MSVC_BUILDTOOLS_INTERNAL[vc_buildtools] = vc_buildtools_def
    MSVC_BUILDTOOLS_EXTERNAL[vc_buildtools] = vc_buildtools_def
    MSVC_BUILDTOOLS_EXTERNAL[vc_version] = vc_buildtools_def

    VC_VERSION_MAP[vc_version] = vc_buildtools_def

MSVS_VERSION_INTERNAL = {}
MSVS_VERSION_EXTERNAL = {}

MSVC_VERSION_INTERNAL = {}
MSVC_VERSION_EXTERNAL = {}
MSVC_VERSION_SUFFIX = {}

MSVS_VERSION_MAJOR_MAP = {}

CL_VERSION_MAP = {}

MSVC_SDK_VERSIONS = set()

# vswhere:
#    map vs major version to vc version (no suffix)
#    build set of supported vc versions (including suffix)
VSWHERE_VSMAJOR_TO_VCVERSION = {}

VSWHERE_SUPPORTED_VCVER = set()
VSWHERE_SUPPORTED_PRODUCTS = set()

REGISTRY_SUPPORTED_VCVER = set()
REGISTRY_SUPPORTED_PRODUCTS = set()

MSVS_PRODUCT_DEFINITION = namedtuple('MSVSProductDefinition', [
    'vs_product',
    'vs_product_numeric',
    'vs_product_alias_list',
    'vs_version',
    'vs_version_major',
    'vs_envvar',
    'vs_express',
    'vs_lookup',
    'vc_sdk_versions',
    'vc_ucrt_versions',
    'vc_uwp',
    'vc_buildtools_def',
    'vc_buildtools_all',
])

MSVS_PRODUCT_DEFINITION_LIST = []

VS_PRODUCT_ALIAS = {
    '1998': ['6']
}

# vs_envvar: VisualStudioVersion defined in environment for MSVS 2012 and later
#            MSVS 2010 and earlier cl_version -> vs_product_def is a 1:1 mapping
# SDK attached to product or buildtools?
for vs_product, vs_version, vs_envvar, vs_express, vs_lookup, vc_sdk, vc_ucrt, vc_uwp, vc_buildtools_all in [
    ('2022', '17.0', True,  False, 'vswhere' , ['10.0', '8.1'], ['10'],   'uwp', ['v143', 'v142', 'v141', 'v140']),
    ('2019', '16.0', True,  False, 'vswhere' , ['10.0', '8.1'], ['10'],   'uwp', ['v142', 'v141', 'v140']),
    ('2017', '15.0', True,  True,  'vswhere' , ['10.0', '8.1'], ['10'],   'uwp', ['v141', 'v140']),
    ('2015', '14.0', True,  True,  'registry', ['10.0', '8.1'], ['10'], 'store', ['v140']),
    ('2013', '12.0', True,  True,  'registry',            None,   None,    None, ['v120']),
    ('2012', '11.0', True,  True,  'registry',            None,   None,    None, ['v110']),
    ('2010', '10.0', False, True,  'registry',            None,   None,    None, ['v100']),
    ('2008',  '9.0', False, True,  'registry',            None,   None,    None, ['v90']),
    ('2005',  '8.0', False, True,  'registry',            None,   None,    None, ['v80']),
    ('2003',  '7.1', False, False, 'registry',            None,   None,    None, ['v71']),
    ('2002',  '7.0', False, False, 'registry',            None,   None,    None, ['v70']),
    ('1998',  '6.0', False, False, 'registry',            None,   None,    None, ['v60']),
]:

    vs_product_numeric = int(vs_product)

    vs_version_major = vs_version.split('.')[0]

    vc_buildtools_def = MSVC_BUILDTOOLS_INTERNAL[vc_buildtools_all[0]]

    if vs_product not in VS_PRODUCT_ALIAS:
        vs_product_alias_list = []
    else:
        vs_product_alias_list = [
            vs_product_alias
            for vs_product_alias in VS_PRODUCT_ALIAS[vs_product]
            if vs_product_alias
        ]

    vs_product_def = MSVS_PRODUCT_DEFINITION(
        vs_product = vs_product,
        vs_product_numeric = vs_product_numeric,
        vs_product_alias_list = tuple(vs_product_alias_list),
        vs_version = vs_version,
        vs_version_major = vs_version_major,
        vs_envvar = vs_envvar,
        vs_express = vs_express,
        vs_lookup = vs_lookup,
        vc_sdk_versions = tuple(vc_sdk) if vc_sdk else vc_sdk,
        vc_ucrt_versions = tuple(vc_ucrt) if vc_ucrt else vc_ucrt,
        vc_uwp = vc_uwp,
        vc_buildtools_def = vc_buildtools_def,
        vc_buildtools_all = tuple(vc_buildtools_all),
    )

    MSVS_PRODUCT_DEFINITION_LIST.append(vs_product_def)

    MSVC_RUNTIME_VSPRODUCTDEF_LIST_MAP[vc_buildtools_def.vc_runtime_def].append(vs_product_def)

    vc_version = vc_buildtools_def.vc_version

    MSVS_VERSION_INTERNAL[vs_product] = vs_product_def
    MSVS_VERSION_EXTERNAL[vs_product] = vs_product_def
    MSVS_VERSION_EXTERNAL[vs_version] = vs_product_def

    MSVC_VERSION_INTERNAL[vc_version] = vs_product_def
    MSVC_VERSION_EXTERNAL[vs_product] = vs_product_def
    MSVC_VERSION_EXTERNAL[vc_version] = vs_product_def
    MSVC_VERSION_EXTERNAL[vc_buildtools_def.vc_buildtools] = vs_product_def

    for vs_product_alias in vs_product_alias_list:
        MSVS_VERSION_EXTERNAL[vs_product_alias] = vs_product_def
        MSVC_VERSION_EXTERNAL[vs_product_alias] = vs_product_def

    MSVC_VERSION_SUFFIX[vc_version] = vs_product_def
    if vs_express:
        MSVC_VERSION_SUFFIX[vc_version + 'Exp'] = vs_product_def

    MSVS_VERSION_MAJOR_MAP[vs_version_major] = vs_product_def

    CL_VERSION_MAP[vc_buildtools_def.cl_version] = vs_product_def

    if vc_sdk:
        MSVC_SDK_VERSIONS.update(vc_sdk)

    if vs_lookup == 'vswhere':
        VSWHERE_VSMAJOR_TO_VCVERSION[vs_version_major] = vc_version
        VSWHERE_SUPPORTED_VCVER.add(vc_version)
        if vs_express:
            VSWHERE_SUPPORTED_VCVER.add(vc_version + 'Exp')
        VSWHERE_SUPPORTED_PRODUCTS.add(vs_product)
    elif vs_lookup == 'registry':
        REGISTRY_SUPPORTED_VCVER.add(vc_version)
        if vs_express:
            REGISTRY_SUPPORTED_VCVER.add(vc_version + 'Exp')
        REGISTRY_SUPPORTED_PRODUCTS.add(vs_product)

MSVS_VERSION_SYMBOLS = list(MSVC_VERSION_EXTERNAL.keys())
MSVC_VERSIONS = list(MSVC_VERSION_SUFFIX.keys())

# MSVS Channel: Release, Preview, Any

MSVS_CHANNEL_DEFINITION = namedtuple('MSVSChannel', [
    'vs_channel_id',
    'vs_channel_rank',
    'vs_channel_suffix',
    'vs_channel_symbols',
])

MSVS_CHANNEL_DEFINITION_LIST = []

MSVS_CHANNEL_INTERNAL = {}
MSVS_CHANNEL_EXTERNAL = {}
MSVS_CHANNEL_SYMBOLS = []

for vs_channel_rank, vs_channel_suffix, vs_channel_symbols in (
    (1, 'Rel', ['Release']),
    (2, 'Pre', ['Preview']),
    (3, 'Any', ['Any'])
):

    vs_channel_id = vs_channel_symbols[0]

    if vs_channel_suffix not in vs_channel_symbols:
        vs_channel_symbols = vs_channel_symbols + [vs_channel_suffix]

    vs_channel_def = MSVS_CHANNEL_DEFINITION(
        vs_channel_id=vs_channel_id,
        vs_channel_rank=vs_channel_rank,
        vs_channel_suffix=vs_channel_suffix,
        vs_channel_symbols=tuple(vs_channel_symbols),
    )

    MSVS_CHANNEL_DEFINITION_LIST.append(vs_channel_def)

    MSVS_CHANNEL_INTERNAL[vs_channel_id] = vs_channel_def
    MSVS_CHANNEL_INTERNAL[vs_channel_rank] = vs_channel_def
    MSVS_CHANNEL_INTERNAL[vs_channel_suffix] = vs_channel_def

    for symbol in vs_channel_symbols:
        MSVS_CHANNEL_SYMBOLS.append(symbol)
        for sym in [symbol, symbol.lower(), symbol.upper()]:
            MSVS_CHANNEL_EXTERNAL[sym] = vs_channel_def

MSVS_CHANNEL_RELEASE = MSVS_CHANNEL_INTERNAL['Release']
MSVS_CHANNEL_PREVIEW = MSVS_CHANNEL_INTERNAL['Preview']
MSVS_CHANNEL_ANY = MSVS_CHANNEL_INTERNAL['Any']

MSVS_CHANNEL_MEMBERLISTS = {
    MSVS_CHANNEL_RELEASE: [MSVS_CHANNEL_RELEASE, MSVS_CHANNEL_ANY],
    MSVS_CHANNEL_PREVIEW: [MSVS_CHANNEL_PREVIEW, MSVS_CHANNEL_ANY],
}

# VS Component Id

MSVS_COMPONENTID_DEFINITION = namedtuple('MSVSComponentId', [
    'vs_component_id',
    'vs_component_suffix',
    'vs_component_isexpress',
    'vs_component_symbols',
])

MSVS_COMPONENTID_DEFINITION_LIST = []

MSVS_COMPONENTID_INTERNAL = {}
MSVS_COMPONENTID_EXTERNAL = {}
MSVS_COMPONENTID_SYMBOLS = []

for vs_component_isexpress, vs_component_suffix, vs_component_symbols in (
    (False, 'Ent', ['Enterprise']),
    (False, 'Pro', ['Professional']),
    (False, 'Com', ['Community']),
    (False, 'Dev', ['Develop']),
    (False, 'Py', ['Python', 'VCForPython']),
    (False, 'Cmd', ['CmdLine', 'CommandLine']),
    (False, 'BT', ['BuildTools']),
    (True, 'Exp', ['Express', 'WDExpress']),
):

    vs_component_id = vs_component_symbols[0]

    if vs_component_suffix not in vs_component_symbols:
        vs_component_symbols = vs_component_symbols + [vs_component_suffix]

    vs_componentid_def = MSVS_COMPONENTID_DEFINITION(
        vs_component_id=vs_component_id,
        vs_component_suffix=vs_component_suffix,
        vs_component_isexpress=vs_component_isexpress,
        vs_component_symbols=tuple(vs_component_symbols),
    )

    MSVS_COMPONENTID_DEFINITION_LIST.append(vs_componentid_def)

    MSVS_COMPONENTID_INTERNAL[vs_component_id] = vs_componentid_def
    MSVS_COMPONENTID_EXTERNAL[vs_component_id] = vs_componentid_def

    for symbol in vs_component_symbols:
        MSVS_COMPONENTID_SYMBOLS.append(symbol)
        for sym in [symbol, symbol.lower(), symbol.upper()]:
            MSVS_COMPONENTID_EXTERNAL[sym] = vs_componentid_def

MSVS_COMPONENTID_ENTERPRISE = MSVS_COMPONENTID_INTERNAL['Enterprise']
MSVS_COMPONENTID_PROFESSIONAL = MSVS_COMPONENTID_INTERNAL['Professional']
MSVS_COMPONENTID_COMMUNITY = MSVS_COMPONENTID_INTERNAL['Community']
MSVS_COMPONENTID_DEVELOP = MSVS_COMPONENTID_INTERNAL['Develop']
MSVS_COMPONENTID_PYTHON = MSVS_COMPONENTID_INTERNAL['Python']
MSVS_COMPONENTID_CMDLINE = MSVS_COMPONENTID_INTERNAL['CmdLine']
MSVS_COMPONENTID_BUILDTOOLS = MSVS_COMPONENTID_INTERNAL['BuildTools']
MSVS_COMPONENTID_EXPRESS = MSVS_COMPONENTID_INTERNAL['Express']

# VS Component Id

MSVS_COMPONENT_DEFINITION = namedtuple('MSVSComponent', [
    'vs_componentid_def',
    'vs_lookup',
    'vs_component_rank',
])

MSVS_COMPONENT_DEFINITION_LIST = []

MSVS_COMPONENT_INTERNAL = {}

VSWHERE_COMPONENT_INTERNAL = {}
VSWHERE_COMPONENT_SYMBOLS = []

REGISTRY_COMPONENT_INTERNAL = {}
REGISTRY_COMPONENT_SYMBOLS = []

if _VC90_Prefer_VCForPython:
    _REG_VPY = 140
    _REG_DEV = 130
else:
    _REG_VPY = 130
    _REG_DEV = 140

for vs_lookup, vs_component_rank, vs_componentid in (

    ('vswhere', 240, 'Enterprise'),
    ('vswhere', 230, 'Professional'),
    ('vswhere', 220, 'Community'),
    ('vswhere', 210, 'BuildTools'),
    ('vswhere', 200, 'Express'),

    ('registry', 170, 'Enterprise'),
    ('registry', 160, 'Professional'),
    ('registry', 150, 'Community'),
    ('registry', _REG_DEV, 'Develop'),
    ('registry', _REG_VPY, 'Python'),
    ('registry', 120, 'CmdLine'),
    ('registry', 110, 'BuildTools'),
    ('registry', 100, 'Express'),

):

    vs_componentid_def = MSVS_COMPONENTID_INTERNAL[vs_componentid]

    vs_component_def = MSVS_COMPONENT_DEFINITION(
        vs_componentid_def=vs_componentid_def,
        vs_lookup=vs_lookup,
        vs_component_rank=vs_component_rank,
    )

    MSVS_COMPONENT_DEFINITION_LIST.append(vs_component_def)

    if vs_lookup == 'vswhere':
        for symbol in vs_componentid_def.vs_component_symbols:
            MSVS_COMPONENT_INTERNAL[(vs_lookup, symbol)] = vs_component_def
            VSWHERE_COMPONENT_INTERNAL[symbol] = vs_component_def
            VSWHERE_COMPONENT_SYMBOLS.append(symbol)
    elif vs_lookup == 'registry':
        for symbol in vs_componentid_def.vs_component_symbols:
            MSVS_COMPONENT_INTERNAL[(vs_lookup, symbol)] = vs_component_def
            REGISTRY_COMPONENT_INTERNAL[symbol] = vs_component_def
            REGISTRY_COMPONENT_SYMBOLS.append(symbol)

VSWHERE_COMPONENT_ENTERPRISE = VSWHERE_COMPONENT_INTERNAL['Ent']
VSWHERE_COMPONENT_PROFESSIONAL = VSWHERE_COMPONENT_INTERNAL['Pro']
VSWHERE_COMPONENT_COMMUNITY = VSWHERE_COMPONENT_INTERNAL['Com']
VSWHERE_COMPONENT_BUILDTOOLS = VSWHERE_COMPONENT_INTERNAL['BT']
VSWHERE_COMPONENT_EXPRESS = VSWHERE_COMPONENT_INTERNAL['Exp']

REGISTRY_COMPONENT_ENTERPRISE = REGISTRY_COMPONENT_INTERNAL['Ent']
REGISTRY_COMPONENT_PROFESSIONAL = REGISTRY_COMPONENT_INTERNAL['Pro']
REGISTRY_COMPONENT_COMMUNITY = REGISTRY_COMPONENT_INTERNAL['Com']
REGISTRY_COMPONENT_DEVELOP = REGISTRY_COMPONENT_INTERNAL['Dev']
REGISTRY_COMPONENT_PYTHON = REGISTRY_COMPONENT_INTERNAL['Py']
REGISTRY_COMPONENT_CMDLINE = REGISTRY_COMPONENT_INTERNAL['Cmd']
REGISTRY_COMPONENT_BUILDTOOLS = REGISTRY_COMPONENT_INTERNAL['BT']
REGISTRY_COMPONENT_EXPRESS = REGISTRY_COMPONENT_INTERNAL['Exp']

# EXPERIMENTAL: msvc version/toolset search lists
#
# VS2017 example:
#
#     defaults['14.1']    = ['14.1', '14.1Exp']
#     defaults['14.1Exp'] = ['14.1Exp']
#
#     search['14.1']    = ['14.3', '14.2', '14.1', '14.1Exp']
#     search['14.1Exp'] = ['14.1Exp']

MSVC_VERSION_TOOLSET_DEFAULTS_MAP = {}
MSVC_VERSION_TOOLSET_SEARCH_MAP = {}

# Pass 1: Build defaults lists and setup express versions
for vs_product_def in MSVS_PRODUCT_DEFINITION_LIST:
    if not vs_product_def.vc_buildtools_def.vc_istoolset:
        continue
    version_key = vs_product_def.vc_buildtools_def.vc_version
    MSVC_VERSION_TOOLSET_DEFAULTS_MAP[version_key] = [version_key]
    MSVC_VERSION_TOOLSET_SEARCH_MAP[version_key] = []
    if vs_product_def.vs_express:
        express_key = version_key + 'Exp'
        MSVC_VERSION_TOOLSET_DEFAULTS_MAP[version_key].append(express_key)
        MSVC_VERSION_TOOLSET_DEFAULTS_MAP[express_key] = [express_key]
        MSVC_VERSION_TOOLSET_SEARCH_MAP[express_key] = [express_key]

# Pass 2: Extend search lists (decreasing version order)
for vs_product_def in MSVS_PRODUCT_DEFINITION_LIST:
    if not vs_product_def.vc_buildtools_def.vc_istoolset:
        continue
    version_key = vs_product_def.vc_buildtools_def.vc_version
    for vc_buildtools in vs_product_def.vc_buildtools_all:
        toolset_buildtools_def = MSVC_BUILDTOOLS_INTERNAL[vc_buildtools]
        toolset_vs_product_def = MSVC_VERSION_INTERNAL[toolset_buildtools_def.vc_version]
        buildtools_key = toolset_buildtools_def.vc_version
        MSVC_VERSION_TOOLSET_SEARCH_MAP[buildtools_key].extend(MSVC_VERSION_TOOLSET_DEFAULTS_MAP[version_key])

# convert string version set to string version list ranked in descending order
MSVC_SDK_VERSIONS = [str(f) for f in sorted([float(s) for s in MSVC_SDK_VERSIONS], reverse=True)]

# internal consistency check (should be last) 

def verify():
    from .. import vc
    for msvc_version in vc._VCVER:
        if msvc_version not in MSVC_VERSION_SUFFIX:
            err_msg = f'msvc_version {msvc_version!r} not in MSVC_VERSION_SUFFIX'
            raise MSVCInternalError(err_msg)
        vc_version = Util.get_msvc_version_prefix(msvc_version)
        if vc_version not in MSVC_VERSION_INTERNAL:
            err_msg = f'vc_version {vc_version!r} not in MSVC_VERSION_INTERNAL'
            raise MSVCInternalError(err_msg)

