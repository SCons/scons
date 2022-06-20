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

from . import Dispatcher
Dispatcher.register_modulename(__name__)


UNDEFINED = object()

BOOLEAN_SYMBOLS = {}
BOOLEAN_EXTERNAL = {}

for bool, symbol_list, symbol_case_list in [
    (False, (False, 0, '0', None, ''), ('False', 'No',  'F', 'N')),
    (True,  (True,  1, '1'),           ('True',  'Yes', 'T', 'Y')),
]:
    BOOLEAN_SYMBOLS[bool] = list(symbol_list)
    for symbol in symbol_case_list:
        BOOLEAN_SYMBOLS[bool].extend([symbol, symbol.lower(), symbol.upper()])

    for symbol in BOOLEAN_SYMBOLS[bool]:
        BOOLEAN_EXTERNAL[symbol] = bool

MSVC_RUNTIME_DEFINITION = namedtuple('MSVCRuntime', [
    'vc_runtime',
    'vc_runtime_numeric',
    'vc_runtime_alias_list',
    'vc_runtime_vsdef_list',
])

MSVC_RUNTIME_DEFINITION_LIST = []

MSVC_RUNTIME_INTERNAL = {}
MSVC_RUNTIME_EXTERNAL = {}

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
        vc_runtime_alias_list = vc_runtime_alias_list,
        vc_runtime_vsdef_list = [],
    )

    MSVC_RUNTIME_DEFINITION_LIST.append(vc_runtime_def)

    MSVC_RUNTIME_INTERNAL[vc_runtime] = vc_runtime_def
    MSVC_RUNTIME_EXTERNAL[vc_runtime] = vc_runtime_def

    for vc_runtime_alias in vc_runtime_alias_list:
        MSVC_RUNTIME_EXTERNAL[vc_runtime_alias] = vc_runtime_def

MSVC_BUILDTOOLS_DEFINITION = namedtuple('MSVCBuildtools', [
    'vc_buildtools',
    'vc_buildtools_numeric',
    'vc_version',
    'vc_version_numeric',
    'cl_version',
    'cl_version_numeric',
    'vc_runtime_def',
])

MSVC_BUILDTOOLS_DEFINITION_LIST = []

MSVC_BUILDTOOLS_INTERNAL = {}
MSVC_BUILDTOOLS_EXTERNAL = {}

VC_VERSION_MAP = {}

for vc_buildtools, vc_version, cl_version, vc_runtime in [
    ('v143', '14.3', '19.3', '140'),
    ('v142', '14.2', '19.2', '140'),
    ('v141', '14.1', '19.1', '140'),
    ('v140', '14.0', '19.0', '140'),
    ('v120', '12.0', '18.0', '120'),
    ('v110', '11.0', '17.0', '110'),
    ('v100', '10.0', '16.0', '100'),
    ('v90',   '9.0', '15.0',  '90'),
    ('v80',   '8.0', '14.0',  '80'),
    ('v71',   '7.1', '13.1',  '71'),
    ('v70',   '7.0', '13.0',  '70'),
    ('v60',   '6.0', '12.0',  '60'),
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

MSVS_VERSION_MAJOR_MAP = {}

CL_VERSION_MAP = {}

MSVC_SDK_VERSIONS = set()

VISUALSTUDIO_DEFINITION = namedtuple('VisualStudioDefinition', [
    'vs_product',
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

VISUALSTUDIO_DEFINITION_LIST = []

VS_PRODUCT_ALIAS = {
    '1998': ['6']
}

# vs_envvar: VisualStudioVersion defined in environment for MSVS 2012 and later
#            MSVS 2010 and earlier cl_version -> vs_def is a 1:1 mapping
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

    vs_version_major = vs_version.split('.')[0]

    vc_buildtools_def = MSVC_BUILDTOOLS_INTERNAL[vc_buildtools_all[0]]

    vs_def = VISUALSTUDIO_DEFINITION(
        vs_product = vs_product,
        vs_product_alias_list = [],
        vs_version = vs_version,
        vs_version_major = vs_version_major,
        vs_envvar = vs_envvar,
        vs_express = vs_express,
        vs_lookup = vs_lookup,
        vc_sdk_versions = vc_sdk,
        vc_ucrt_versions = vc_ucrt,
        vc_uwp = vc_uwp,
        vc_buildtools_def = vc_buildtools_def,
        vc_buildtools_all = vc_buildtools_all,
    )

    VISUALSTUDIO_DEFINITION_LIST.append(vs_def)

    vc_buildtools_def.vc_runtime_def.vc_runtime_vsdef_list.append(vs_def)

    MSVS_VERSION_INTERNAL[vs_product] = vs_def
    MSVS_VERSION_EXTERNAL[vs_product] = vs_def
    MSVS_VERSION_EXTERNAL[vs_version] = vs_def

    MSVC_VERSION_INTERNAL[vc_buildtools_def.vc_version] = vs_def
    MSVC_VERSION_EXTERNAL[vs_product] = vs_def
    MSVC_VERSION_EXTERNAL[vc_buildtools_def.vc_version] = vs_def
    MSVC_VERSION_EXTERNAL[vc_buildtools_def.vc_buildtools] = vs_def

    if vs_product in VS_PRODUCT_ALIAS:
        for vs_product_alias in VS_PRODUCT_ALIAS[vs_product]:
            vs_def.vs_product_alias_list.append(vs_product_alias)
            MSVS_VERSION_EXTERNAL[vs_product_alias] = vs_def
            MSVC_VERSION_EXTERNAL[vs_product_alias] = vs_def

    MSVS_VERSION_MAJOR_MAP[vs_version_major] = vs_def

    CL_VERSION_MAP[vc_buildtools_def.cl_version] = vs_def

    if not vc_sdk:
        continue

    MSVC_SDK_VERSIONS.update(vc_sdk)

# convert string version set to string version list ranked in descending order
MSVC_SDK_VERSIONS = [str(f) for f in sorted([float(s) for s in MSVC_SDK_VERSIONS], reverse=True)]

MSVS_VERSION_LEGACY = {}
MSVC_VERSION_LEGACY = {}

for vdict in (MSVS_VERSION_EXTERNAL, MSVC_VERSION_INTERNAL):
    for key, vs_def in vdict.items():
        if key not in MSVS_VERSION_LEGACY:
            MSVS_VERSION_LEGACY[key] = vs_def
            MSVC_VERSION_LEGACY[key] = vs_def

# MSVC_NOTFOUND_POLICY definition:
#     error:   raise exception
#     warning: issue warning and continue
#     ignore:  continue

MSVC_NOTFOUND_POLICY_DEFINITION = namedtuple('MSVCNotFoundPolicyDefinition', [
    'value',
    'symbol',
])

MSVC_NOTFOUND_DEFINITION_LIST = []

MSVC_NOTFOUND_POLICY_INTERNAL = {}
MSVC_NOTFOUND_POLICY_EXTERNAL = {}

for policy_value, policy_symbol_list in [
    (True,  ['Error',   'Exception']),
    (False, ['Warning', 'Warn']),
    (None,  ['Ignore',  'Suppress']),
]:

    policy_symbol = policy_symbol_list[0].lower()
    policy_def = MSVC_NOTFOUND_POLICY_DEFINITION(policy_value, policy_symbol)

    MSVC_NOTFOUND_DEFINITION_LIST.append(vs_def)

    MSVC_NOTFOUND_POLICY_INTERNAL[policy_symbol] = policy_def

    for policy_symbol in policy_symbol_list:
        MSVC_NOTFOUND_POLICY_EXTERNAL[policy_symbol.lower()] = policy_def
        MSVC_NOTFOUND_POLICY_EXTERNAL[policy_symbol] = policy_def
        MSVC_NOTFOUND_POLICY_EXTERNAL[policy_symbol.upper()] = policy_def

