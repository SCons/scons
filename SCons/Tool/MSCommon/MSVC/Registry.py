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
Windows registry functions for Microsoft Visual C/C++.
"""

import os

from SCons.Util import (
    HKEY_LOCAL_MACHINE,
    HKEY_CURRENT_USER,
)

from .. common import (
    debug,
    read_reg,
)

from . import Util

from . import Dispatcher
Dispatcher.register_modulename(__name__)


def read_value(hkey, subkey_valname):
    try:
        rval = read_reg(subkey_valname, hkroot=hkey)
    except OSError:
        debug('OSError: hkey=%s, subkey=%s', repr(hkey), repr(subkey_valname))
        return None
    except IndexError:
        debug('IndexError: hkey=%s, subkey=%s', repr(hkey), repr(subkey_valname))
        return None
    debug('hkey=%s, subkey=%s, rval=%s', repr(hkey), repr(subkey_valname), repr(rval))
    return rval

def registry_query_path(key, val, suffix):
    extval = val + '\\' + suffix if suffix else val
    qpath = read_value(key, extval)
    if qpath and os.path.exists(qpath):
        qpath = Util.process_path(qpath)
    else:
        qpath = None
    return (qpath, key, val, extval)

REG_SOFTWARE_MICROSOFT = [
    (HKEY_LOCAL_MACHINE, r'Software\Wow6432Node\Microsoft'),
    (HKEY_CURRENT_USER,  r'Software\Wow6432Node\Microsoft'), # SDK queries
    (HKEY_LOCAL_MACHINE, r'Software\Microsoft'),
    (HKEY_CURRENT_USER,  r'Software\Microsoft'),
]

def microsoft_query_paths(suffix, usrval=None):
    paths = []
    records = []
    for key, val in REG_SOFTWARE_MICROSOFT:
        extval = val + '\\' + suffix if suffix else val
        qpath = read_value(key, extval)
        if qpath and os.path.exists(qpath):
            qpath = Util.process_path(qpath)
            if qpath not in paths:
                paths.append(qpath)
                records.append((qpath, key, val, extval, usrval))
    return records

def microsoft_query_keys(suffix, usrval=None):
    records = []
    for key, val in REG_SOFTWARE_MICROSOFT:
        extval = val + '\\' + suffix if suffix else val
        rval = read_value(key, extval)
        if rval:
            records.append((key, val, extval, usrval))
    return records

def microsoft_sdks(version):
    return '\\'.join([r'Microsoft SDKs\Windows', 'v' + version, r'InstallationFolder'])

def sdk_query_paths(version):
    q = microsoft_sdks(version)
    return microsoft_query_paths(q)

def windows_kits(version):
    return r'Windows Kits\Installed Roots\KitsRoot' + version

def windows_kit_query_paths(version):
    q = windows_kits(version)
    return microsoft_query_paths(q)

def vstudio_sxs_vc7(version):
    return '\\'.join([r'VisualStudio\SxS\VC7', version])

