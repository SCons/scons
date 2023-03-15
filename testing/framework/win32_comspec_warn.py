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
Issue unsupported Windows COMSPEC command interpreter warning if necessary.
"""

import sys
import os
import importlib
import warnings


if sys.platform == 'win32':

    _VERBOSE = False

    def _windows_comspec_warning_message(verbose=False):

        win32_comspec_modulename = 'win32_comspec'
        win32_comspec_filename = win32_comspec_modulename + '.py'

        win32_comspec_relpaths = [
            '../../SCons/compat',
        ]

        if verbose:
            _comspec = os.environ.get('COMSPEC')
            print(f"{__file__}: os.environ['COMSPEC']={_comspec}", file=sys.stderr)

        curdir = os.path.dirname(__file__)

        modulepath = None
        for reldir in win32_comspec_relpaths:
            checkdir = os.path.normpath(os.path.join(curdir, reldir))
            if not os.path.exists(checkdir):
                continue
            checkfile = os.path.join(checkdir, win32_comspec_filename)
            if not os.path.exists(checkfile):
                continue
            modulepath = checkdir
            break

        if verbose:
            print(f"{__file__}: modulepath='{modulepath}'", file=sys.stderr)

        if not modulepath:
            return None

        win32_comspec_module = None

        if modulepath:
            sys.path.append(modulepath)
            try:
                win32_comspec_module = importlib.import_module(win32_comspec_modulename)
            except ImportError:
                pass
            sys.path.pop()

        if verbose:
            print(f"{__file__}: module='{win32_comspec_module}'", file=sys.stderr)

        if not win32_comspec_module:
            return None

        if verbose:
            _comspec = os.environ.get('COMSPEC')
            print(f"{__file__}: os.environ['COMSPEC']={_comspec}", file=sys.stderr)

        message = win32_comspec_module.windows_comspec_warning_message()

        if verbose:
            print(f"{__file__}: message={message}", file=sys.stderr)

        return message

    _warnmsg = _windows_comspec_warning_message(verbose=_VERBOSE)
    if _warnmsg:

        class WindowsComspecWarning(RuntimeWarning):
            """Windows COMSPEC warning message."""

        warnings.simplefilter('once', WindowsComspecWarning)
        warnings.warn(_warnmsg, WindowsComspecWarning, stacklevel=2)
