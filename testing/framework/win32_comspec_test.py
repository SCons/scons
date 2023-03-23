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
Windows COMSPEC command interpreter module loader.
"""

import sys

__all__ = []


if sys.platform == 'win32':

    import os

    _SCONS_WIN32_COMSPEC_FORCE_TEST_EVAR = 'SCONS_WIN32_COMSPEC_FORCE_TEST'

    _VERBOSE = False

    def _windows_comspec_evaluate(verbose=False):

        comspec = os.environ.get('COMSPEC')

        if verbose:
            print(f"{__file__}: os.environ['COMSPEC']={comspec}", file=sys.stderr)

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
        orig_val = os.environ.get(_SCONS_WIN32_COMSPEC_FORCE_TEST_EVAR, '')
        val = orig_val.lower() if orig_val else ''
        if val and val in ('false', 'f', 'no', 'n', '0'):
            rval = False
        else:
            rval = True
        return rval, orig_val

    def _windows_comspec_loader(verbose=False):

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

        import importlib  # pylint: disable=import-outside-toplevel

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

        if verbose:
            _comspec = os.environ.get('COMSPEC')
            print(f"{__file__}: os.environ['COMSPEC']={_comspec}", file=sys.stderr)

        return win32_comspec_module

    def _windows_comspec_setup(verbose=False):

        is_comspec, comspec = _windows_comspec_evaluate(verbose=verbose)

        if verbose:
            print(
                f"{__file__}: is_comspec={is_comspec}, COMSPEC={comspec}",
                file=sys.stderr
            )

        if is_comspec:
            return

        import textwrap  # pylint: disable=import-outside-toplevel

        is_force, os_force = _windows_osenviron_force_comspec()

        if verbose:
            print(
                f"{__file__}: is_force={is_force}, os_force={os_force}",
                file=sys.stderr
            )

        win32_comspec = _windows_comspec_loader(verbose=verbose)

        if verbose:
            print(f"{__file__}: win32_comspec={win32_comspec}", file=sys.stderr)

        msg = ''

        if not is_force:
            # not is_force, win32_comspec
            # not is_force, not win32_comspec
            msg = textwrap.dedent(
                f""" \
                Unsupported windows COMSPEC value, build may fail:
                   COMSPEC={comspec}
                   {_SCONS_WIN32_COMSPEC_FORCE_TEST_EVAR}={os_force}\
                """
            )
        elif not win32_comspec:
            # is_force, not win32_comspec
            msg = textwrap.dedent(
                f""" \
                Unsupported windows COMSPEC value, build may fail:
                   COMSPEC={comspec}
                   {_SCONS_WIN32_COMSPEC_FORCE_TEST_EVAR}={os_force}
                   win32_comspec module import failed.\
                """
            )
        else:
            # is_force, win32_comspec
            win32_comspec.windows_comspec_context_create()
            state = win32_comspec.windows_comspec_state_create()
            if state:
                msg = textwrap.dedent(
                    f""" \
                    Unsupported windows COMSPEC value, build may fail:
                       COMSPEC={comspec}
                       {_SCONS_WIN32_COMSPEC_FORCE_TEST_EVAR}={os_force}
                       A valid command interpreter was not found.\
                    """
                )
            if verbose:
                _comspec = os.environ.get('COMSPEC')
                print(f"{__file__}: os.environ['COMSPEC']={_comspec}", file=sys.stderr)

        if not msg:
            return

        import warnings  # pylint: disable=import-outside-toplevel

        class WindowsComspecWarning(RuntimeWarning):
            """Windows COMSPEC warning message."""

        warnings.simplefilter('once', WindowsComspecWarning)
        warnings.warn(msg, WindowsComspecWarning, stacklevel=4)

    _windows_comspec_setup(verbose=_VERBOSE)
