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
Subprocess context module loader.
"""

__all__ = []

import sys
import os
import importlib
import textwrap
import warnings

try:
    import msvcrt  # pylint: disable=unused-import
except ModuleNotFoundError:
    _MSWINDOWS = False
else:
    _MSWINDOWS = True


_VERBOSE = False


class SubprocessContextLoader:  # pylint: disable=too-few-public-methods
    """Import subprocess context module."""

    _subprocess_context_module_once = False
    _subprocess_context_module = None

    @classmethod
    def load(cls, verbose=False):
        """Load subprocess context module from relative path."""

        if cls._subprocess_context_module_once:
            return cls._subprocess_context_module

        cls._subprocess_context_module_once = True

        subprocess_context_modulename = 'subprocess_context'

        subprocess_context_relpaths = [
            '../../SCons/Platform',
        ]

        curdir = os.path.dirname(__file__)

        modulepath = None
        for reldir in subprocess_context_relpaths:
            checkdir = os.path.normpath(os.path.join(curdir, reldir))
            if not os.path.exists(checkdir):
                continue
            checkmodule = os.path.join(checkdir, subprocess_context_modulename)
            if not os.path.exists(checkmodule):
                continue
            modulepath = checkdir
            break

        if verbose:
            print(f"{__file__}: modulepath='{modulepath}'", file=sys.stderr)

        if not modulepath:
            return None

        if modulepath:
            sys.path.append(modulepath)
            try:
                cls._subprocess_context_module = importlib.import_module(
                    subprocess_context_modulename
                )
            except ImportError:
                pass
            sys.path.pop()

        if verbose:
            print(f"{__file__}: module='{cls._subprocess_context_module}'", file=sys.stderr)

        return cls._subprocess_context_module


if _MSWINDOWS:

    FORCE_COMSPEC_EVAR = 'SCONS_WIN32_COMSPEC_FORCE_TEST'

    def _windows_comspec_evaluate(verbose=False):

        comspec = os.environ.get('COMSPEC')

        if verbose:
            print(f"{__file__}: os.environ['COMSPEC']={repr(comspec)}", file=sys.stderr)

        if not comspec or not os.path.exists(comspec):
            return False, comspec

        _, tail = os.path.split(comspec)

        tail = tail.lower()

        if tail not in ('cmd.exe', 'command.com'):
            return False, comspec

        base, ext = os.path.splitext(tail)

        if base not in ('cmd', 'command'):
            return False, comspec

        if ext not in ('.com', '.exe', '.bat', '.cmd'):
            return False, comspec

        return True, comspec

    def _windows_osenviron_force_comspec():
        orig_val = os.environ.get(FORCE_COMSPEC_EVAR, '')
        val = orig_val.lower() if orig_val else ''
        if val and val in ('false', 'f', 'no', 'n', '0'):
            rval = False
        else:
            rval = True
        return rval, orig_val

    def _windows_subprocess_context(verbose=False):

        is_comspec, comspec = _windows_comspec_evaluate(verbose=verbose)

        if verbose:
            print(
                f"{__file__}: is_comspec={is_comspec}, COMSPEC={repr(comspec)}",
                file=sys.stderr
            )

        if is_comspec:
            return

        is_force, os_force = _windows_osenviron_force_comspec()

        if verbose:
            print(
                f"{__file__}: is_force={is_force}, os_force={repr(os_force)}",
                file=sys.stderr
            )

        subprocess_context = SubprocessContextLoader.load(verbose=verbose)

        msg = ''

        if not is_force:
            # not is_force, subprocess_context
            # not is_force, not subprocess_context
            msg = textwrap.dedent(
                f""" \
                Unsupported windows COMSPEC value, build may fail:
                   COMSPEC={comspec}
                   {FORCE_COMSPEC_EVAR}={os_force}\
                """
            )
        elif not subprocess_context:
            # is_force, not subprocess_context
            msg = textwrap.dedent(
                f""" \
                Unsupported windows COMSPEC value, build may fail:
                   COMSPEC={comspec}
                   {FORCE_COMSPEC_EVAR}={os_force}
                   subprocess_context module import failed.\
                """
            )
        else:
            # is_force, subprocess_context
            context_handler = subprocess_context.get_handler('msvcrt')
            context_handler.context_create()
            state = context_handler.state_create()
            if state:
                msg = textwrap.dedent(
                    f""" \
                    Unsupported windows COMSPEC value, build may fail:
                       COMSPEC={comspec}
                       {FORCE_COMSPEC_EVAR}={os_force}
                       A valid command interpreter was not found.\
                    """
                )
            if verbose:
                _comspec = os.environ.get('COMSPEC')
                print(f"{__file__}: os.environ['COMSPEC']={repr(_comspec)}", file=sys.stderr)

        if not msg:
            return

        class WindowsComspecWarning(RuntimeWarning):
            """Windows COMSPEC warning message."""

        warnings.simplefilter('once', WindowsComspecWarning)
        warnings.warn(msg, WindowsComspecWarning, stacklevel=4)

    _windows_subprocess_context(verbose=_VERBOSE)
