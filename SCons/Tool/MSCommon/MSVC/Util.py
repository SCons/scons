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
Helper functions for Microsoft Visual C/C++.
"""

import os
import re

def listdir_dirs(p):
    """Get a list of qualified subdirectory paths from a windows path.

    Args:
        p: str
            windows path

    Returns:
        List[str]: list of qualified subdirectory paths

    """
    dirs = []
    for dir_name in os.listdir(p):
        dir_path = os.path.join(p, dir_name)
        if os.path.isdir(dir_path):
            dirs.append((dir_name, dir_path))
    return dirs

def process_path(p):
    """Normalize a windows path.

    Args:
        p: str
            windows path

    Returns:
        str: normalized windows path

    """
    if p:
        p = os.path.normpath(p)
        p = os.path.realpath(p)
        p = os.path.normcase(p)
    return p

re_version_prefix = re.compile(r'^(?P<version>[0-9.]+).*')

def get_version_prefix(version):
    """Get the version number prefix from a string.

    Args:
        version: str
            version string

    Returns:
        str: the version number prefix

    """
    m = re_version_prefix.match(version)
    if m:
        rval = m.group('version')
    else:
        rval = ''
    return rval

re_msvc_version_prefix = re.compile(r'^(?P<version>[1-9][0-9]?[.][0-9]).*')

def get_msvc_version_prefix(version):
    """Get the msvc version number prefix from a string.

    Args:
        version: str
            version string

    Returns:
        str: the msvc version number prefix

    """
    m = re_msvc_version_prefix.match(version)
    if m:
        rval = m.group('version')
    else:
        rval = ''
    return rval

