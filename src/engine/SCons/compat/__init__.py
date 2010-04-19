#
# __COPYRIGHT__
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
#

__doc__ = """
SCons compatibility package for old Python versions

This subpackage holds modules that provide backwards-compatible
implementations of various things that we'd like to use in SCons but which
only show up in later versions of Python than the early, old version(s)
we still support.

Other code will not generally reference things in this package through
the SCons.compat namespace.  The modules included here add things to
the builtins namespace or the global module list so that the rest
of our code can use the objects and names imported here regardless of
Python version.

Simply enough, things that go in the builtins name space come from
our _scons_builtins module.

The rest of the things here will be in individual compatibility modules
that are either: 1) suitably modified copies of the future modules that
we want to use; or 2) backwards compatible re-implementations of the
specific portions of a future module's API that we want to use.

GENERAL WARNINGS:  Implementations of functions in the SCons.compat
modules are *NOT* guaranteed to be fully compliant with these functions in
later versions of Python.  We are only concerned with adding functionality
that we actually use in SCons, so be wary if you lift this code for
other uses.  (That said, making these more nearly the same as later,
official versions is still a desirable goal, we just don't need to be
obsessive about it.)

We name the compatibility modules with an initial '_scons_' (for example,
_scons_subprocess.py is our compatibility module for subprocess) so
that we can still try to import the real module name and fall back to
our compatibility module if we get an ImportError.  The import_as()
function defined below loads the module as the "real" name (without the
'_scons'), after which all of the "import {module}" statements in the
rest of our code will find our pre-loaded compatibility module.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

def import_as(module, name):
    """
    Imports the specified module (from our local directory) as the
    specified name, returning the loaded module object.
    """
    import imp
    import os.path
    dir = os.path.split(__file__)[0]
    file, filename, suffix_mode_type = imp.find_module(module, [dir])
    return imp.load_module(name, file, filename, suffix_mode_type)


try:
    import builtins
except ImportError:
    # Use the "imp" module to protect the import from fixers.
    import imp
    import sys
    _builtin = imp.load_module('__builtin__',
                               *imp.find_module('__builtin__'))
    sys.modules['builtins'] = _builtin
    del _builtin

import _scons_builtins


try:
    import hashlib
except ImportError:
    # Pre-2.5 Python has no hashlib module.
    try:
        import_as('_scons_hashlib', 'hashlib')
    except ImportError:
        # If we failed importing our compatibility module, it probably
        # means this version of Python has no md5 module.  Don't do
        # anything and let the higher layer discover this fact, so it
        # can fall back to using timestamp.
        pass

try:
    set
except NameError:
    # Pre-2.4 Python has no native set type
    import_as('_scons_sets', 'sets')
    import builtins, sets
    builtins.set = sets.Set


try:
    import collections
except ImportError:
    # Pre-2.4 Python has no collections module.
    import_as('_scons_collections', 'collections')
else:
    # Use the "imp" module to protect the imports below from fixers.
    import imp
    try:
        collections.UserDict
    except AttributeError:
        _UserDict = imp.load_module('UserDict', *imp.find_module('UserDict'))
        collections.UserDict = _UserDict.UserDict
        del _UserDict
    try:
        collections.UserList
    except AttributeError:
        _UserList = imp.load_module('UserList', *imp.find_module('UserList'))
        collections.UserList = _UserList.UserList
        del _UserList
    try:
        collections.UserString
    except AttributeError:
        _UserString = imp.load_module('UserString',
                                      *imp.find_module('UserString'))
        collections.UserString = _UserString.UserString
        del _UserString


try:
    import dbm
except ImportError:
    dbm = import_as('_scons_dbm', 'dbm')
try:
    dbm.whichdb
except AttributeError:
    # Pre-3.0 Python has no dbm.whichdb function.
    import whichdb
    dbm.whichdb = whichdb.whichdb
    del whichdb


try:
    import io
except ImportError:
    # Pre-2.6 Python has no io module.
    import_as('_scons_io', 'io')


import os
try:
    os.devnull
except AttributeError:
    # Pre-2.4 Python has no os.devnull attribute
    import sys
    _names = sys.builtin_module_names
    if 'posix' in _names:
        os.devnull = '/dev/null'
    elif 'nt' in _names:
        os.devnull = 'nul'
    os.path.devnull = os.devnull
try:
    os.path.lexists
except AttributeError:
    # Pre-2.4 Python has no os.path.lexists function
    def lexists(path):
        return os.path.exists(path) or os.path.islink(path)
    os.path.lexists = lexists


# When we're using the '-3' option during regression tests, importing
# cPickle gives a warning no matter how it's done, so always use the
# real profile module, whether it's fast or not.
if os.environ.get('SCONS_HORRIBLE_REGRESSION_TEST_HACK') is None:
    # Not a regression test with '-3', so try to use faster version.
    try:
        # Use the "imp" module to protect the import from fixers.
        import imp
        _cPickle = imp.load_module('cPickle', *imp.find_module('cPickle'))
    except ImportError, e:
        # The "cPickle" module has already been eliminated in favor of
        # having "import pickle" import the fast version when available.
        pass
    else:
        import sys
        sys.modules['pickle'] = _cPickle
        del _cPickle


try:
    # Use the "imp" module to protect the import from fixers.
    import imp
    _cProfile = imp.load_module('cProfile', *imp.find_module('cProfile'))
except ImportError:
    # The "cProfile" module has already been eliminated in favor of
    # having "import profile" import the fast version when available.
    pass
else:
    import sys
    sys.modules['profile'] = _cProfile
    del _cProfile


try:
    import platform
except ImportError:
    # Pre-2.3 Python has no platform module.
    import_as('_scons_platform', 'platform')


try:
    import queue
except ImportError:
    # Before Python 3.0, the 'queue' module was named 'Queue'.
    import imp
    file, filename, suffix_mode_type = imp.find_module('Queue')
    imp.load_module('queue', file, filename, suffix_mode_type)


import shlex
try:
    shlex.split
except AttributeError:
    # Pre-2.3 Python has no shlex.split() function.
    #
    # The full white-space splitting semantics of shlex.split() are
    # complicated to reproduce by hand, so just use a compatibility
    # version of the shlex module cribbed from Python 2.5 with some
    # minor modifications for older Python versions.
    del shlex
    import_as('_scons_shlex', 'shlex')


import shutil
try:
    shutil.move
except AttributeError:
    # Pre-2.3 Python has no shutil.move() function.
    #
    # Cribbed from Python 2.5.
    import os

    def move(src, dst):
        """Recursively move a file or directory to another location.

        If the destination is on our current filesystem, then simply use
        rename.  Otherwise, copy src to the dst and then remove src.
        A lot more could be done here...  A look at a mv.c shows a lot of
        the issues this implementation glosses over.

        """
        try:
            os.rename(src, dst)
        except OSError:
            if os.path.isdir(src):
                if shutil.destinsrc(src, dst):
                    raise Error("Cannot move a directory '%s' into itself '%s'." % (src, dst))
                shutil.copytree(src, dst, symlinks=True)
                shutil.rmtree(src)
            else:
                shutil.copy2(src,dst)
                os.unlink(src)
    shutil.move = move
    del move

    def destinsrc(src, dst):
        src = os.path.abspath(src)
        return os.path.abspath(dst)[:len(src)] == src
    shutil.destinsrc = destinsrc
    del destinsrc


try:
    import subprocess
except ImportError:
    # Pre-2.4 Python has no subprocess module.
    import_as('_scons_subprocess', 'subprocess')

import sys
try:
    sys.intern
except AttributeError:
    # Pre-2.6 Python has no sys.intern() function.
    import builtins
    try:
        sys.intern = builtins.intern
    except AttributeError:
        # Pre-2.x Python has no builtin intern() function.
        def intern(x):
           return x
        sys.intern = intern
        del intern
try:
    sys.maxsize
except AttributeError:
    # Pre-2.6 Python has no sys.maxsize attribute
    # Wrapping sys in () is silly, but protects it from 2to3 renames fixer
    sys.maxsize = (sys).maxint


import tempfile
try:
    tempfile.mkstemp
except AttributeError:
    # Pre-2.3 Python has no tempfile.mkstemp function, so try to simulate it.
    # adapted from the mkstemp implementation in python 3.
    import os
    import errno
    def mkstemp(*args, **kw):
        text = False
        # TODO (1.5)
        #if 'text' in kw :
        if 'text' in kw.keys() :
            text = kw['text']
            del kw['text']
        elif len( args ) == 4 :
            text = args[3]
            args = args[:3]
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
        if not text and hasattr( os, 'O_BINARY' ) :
            flags = flags | os.O_BINARY
        while True:
            try :
                name = tempfile.mktemp(*args, **kw)
                fd = os.open( name, flags, 0600 )
                return (fd, os.path.abspath(name))
            except OSError, e:
                if e.errno == errno.EEXIST:
                    continue
                raise

    tempfile.mkstemp = mkstemp
    del mkstemp


if os.environ.get('SCONS_HORRIBLE_REGRESSION_TEST_HACK') is not None:
    # We can't apply the 'callable' fixer until the floor is 2.6, but the
    # '-3' option to Python 2.6 and 2.7 generates almost ten thousand
    # warnings.  This hack allows us to run regression tests with the '-3'
    # option by replacing the callable() built-in function with a hack
    # that performs the same function but doesn't generate the warning.
    # Note that this hack is ONLY intended to be used for regression
    # testing, and should NEVER be used for real runs.
    from types import ClassType
    def callable(obj):
        if hasattr(obj, '__call__'): return True
        if isinstance(obj, (ClassType, type)): return True
        return False
    import builtins
    builtins.callable = callable
    del callable


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
