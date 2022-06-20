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
Microsoft Visual C/C++ not found policy.

Notes:
    * As implemented, the default is that a warning is issued.  This can
      be changed globally via the function set_msvc_notfound_policy and/or
      through the environment via the MSVC_NOTFOUND_POLICY variable.
"""

import SCons.Warnings

from ..common import (
    debug,
)

from . import Config

from .Exceptions import (
    MSVCVersionNotFound,
)

from . import Dispatcher
Dispatcher.register_modulename(__name__)


_MSVC_NOTFOUND_POLICY_DEF = Config.MSVC_NOTFOUND_POLICY_INTERNAL['warning']

def _msvc_notfound_policy_lookup(symbol):

    try:
        notfound_policy_def = Config.MSVC_NOTFOUND_POLICY_EXTERNAL[symbol]
    except KeyError:
        err_msg = "Value specified for MSVC_NOTFOUND_POLICY is not supported: {}.\n" \
                  "  Valid values are: {}".format(
                     repr(symbol),
                     ', '.join([repr(s) for s in Config.MSVC_NOTFOUND_POLICY_EXTERNAL.keys()])
                  )
        raise ValueError(err_msg)

    return notfound_policy_def

def set_msvc_notfound_policy(MSVC_NOTFOUND_POLICY=None):
    """ Set the default policy when MSVC is not found.

    Args:
        MSVC_NOTFOUND_POLICY:
           string representing the policy behavior
           when MSVC is not found or None

    Returns:
        The previous policy is returned when the MSVC_NOTFOUND_POLICY argument
        is not None. The active policy is returned when the MSVC_NOTFOUND_POLICY
        argument is None.

    """
    global _MSVC_NOTFOUND_POLICY_DEF

    prev_policy = _MSVC_NOTFOUND_POLICY_DEF.symbol

    policy = MSVC_NOTFOUND_POLICY
    if policy is not None:
        _MSVC_NOTFOUND_POLICY_DEF = _msvc_notfound_policy_lookup(policy)

    debug(
        'prev_policy=%s, set_policy=%s, policy.symbol=%s, policy.value=%s',
        repr(prev_policy), repr(policy),
        repr(_MSVC_NOTFOUND_POLICY_DEF.symbol), repr(_MSVC_NOTFOUND_POLICY_DEF.value)
    )

    return prev_policy

def get_msvc_notfound_policy():
    """Return the active policy when MSVC is not found."""
    debug(
        'policy.symbol=%s, policy.value=%s',
        repr(_MSVC_NOTFOUND_POLICY_DEF.symbol), repr(_MSVC_NOTFOUND_POLICY_DEF.value)
    )
    return _MSVC_NOTFOUND_POLICY_DEF.symbol

def policy_handler(env, msg):

    if env and 'MSVC_NOTFOUND_POLICY' in env:
        # environment setting
        notfound_policy_src = 'environment'
        policy = env['MSVC_NOTFOUND_POLICY']
        if policy is not None:
            # user policy request
            notfound_policy_def = _msvc_notfound_policy_lookup(policy)
        else:
            # active global setting
            notfound_policy_def = _MSVC_NOTFOUND_POLICY_DEF
    else:
        # active global setting
        notfound_policy_src = 'default'
        policy = None
        notfound_policy_def = _MSVC_NOTFOUND_POLICY_DEF

    debug(
        'source=%s, set_policy=%s, policy.symbol=%s, policy.value=%s',
        notfound_policy_src, repr(policy), repr(notfound_policy_def.symbol), repr(notfound_policy_def.value)
    )

    if notfound_policy_def.value is None:
        # ignore
        pass
    elif notfound_policy_def.value:
        raise MSVCVersionNotFound(msg)
    else:
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)

