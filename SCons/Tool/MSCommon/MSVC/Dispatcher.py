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
Internal method dispatcher for Microsoft Visual C/C++.
"""

import sys

from ..common import (
    debug,
)

_refs = []

def register_class(ref):
    _refs.append(ref)

def register_modulename(modname):
    module = sys.modules[modname]
    _refs.append(module)

def reset():
    debug('')
    for ref in _refs:
        for method in ['reset', '_reset']:
            if not hasattr(ref, method) or not callable(getattr(ref, method, None)):
                continue
            debug('call %s.%s()', ref.__name__, method)
            func = getattr(ref, method)
            func()

def verify():
    debug('')
    for ref in _refs:
        for method in ['verify', '_verify']:
            if not hasattr(ref, method) or not callable(getattr(ref, method, None)):
                continue
            debug('call %s.%s()', ref.__name__, method)
            func = getattr(ref, method)
            func()

