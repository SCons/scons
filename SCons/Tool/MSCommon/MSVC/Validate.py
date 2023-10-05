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
Version validation for Microsoft Visual C/C++.
"""

from ..common import debug

from .Exceptions import (
    MSVCVersionUnsupported,
    MSVCArgumentError,
)

from . import Config
from . import Util


from . import Dispatcher
Dispatcher.register_modulename(__name__)


def validate_msvc_version(vc_version, label):

    vc_version_def = None

    if not vc_version:
        return vc_version_def

    vc_version_def = Util.msvc_version_components(vc_version)
    if not vc_version_def:

        if not Util.is_version_valid(vc_version):
            err_msg = f'Unsupported {label} format: {vc_version!r}'
            debug(err_msg)
            raise MSVCArgumentError(err_msg)

        if vc_version not in Config.MSVC_VERSIONS:
            symbols = Config.MSVC_VERSIONS
            err_msg = f'Unrecognized {label} {vc_version!r}\n  Valid msvc versions are: {symbols}'
            debug(err_msg)
            raise MSVCVersionUnsupported(err_msg)

    return vc_version_def

def validate_msvs_product(vs_product, label):

    vs_product_def = None
    
    if not vs_product:
        return vs_product_def

    vs_product_def = Config.MSVS_VERSION_EXTERNAL.get(vs_product)
    if not vs_product_def:
        symbols = ', '.join(Config.MSVS_VERSION_SYMBOLS)
        err_msg = f'Unrecognized {label} {vs_product!r}\n  Valid msvs products are: {symbols}'
        debug(err_msg)
        raise MSVCArgumentError(err_msg)

    return vs_product_def

def validate_msvs_component(vs_component, label):

    vs_componentid_def = None

    if not vs_component:
        return vs_componentid_def

    vs_componentid_def = Config.MSVS_COMPONENTID_EXTERNAL.get(vs_componentid_def)
    if not vs_componentid_def:
        symbols = ', '.join(Config.MSVS_COMPONENTID_SYMBOLS)
        err_msg = f'Unrecognized {label} {vs_component!r}\n  Valid msvs components are: {symbols}'
        debug(err_msg)
        raise MSVCArgumentError(err_msg)

    return vs_componentid_def

def validate_msvs_channel(vs_channel, label):

    vs_channel_def = None

    if not vs_channel:
        return vs_channel_def

    vs_channel_def = Config.MSVS_CHANNEL_EXTERNAL.get(vs_channel)
    if not vs_channel_def:
        symbols = ', '.join(Config.MSVS_CHANNEL_SYMBOLS)
        err_msg = f'Unrecognized {label} {vs_channel!r}\n  Valid msvs channels are: {symbols}'
        debug(err_msg)
        raise MSVCArgumentError(err_msg)

    return vs_channel_def

