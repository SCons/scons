"""
Output management for working with the Microsoft tool chain.
"""
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
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import glob

_HAVE_DEBUG = True
_HAVE_TRACE = True

class _MSCONFIG:

    # SCONS_MSCOMMON_DEBUG is internal-use so undocumented:
    # set to '-' to print to console, else set to filename to log to
    DEBUG_LOGFILE = os.environ.get('SCONS_MSCOMMON_DEBUG')

    # SCONS_MSCOMMON_TRACE is internal-use so undocumented:
    # set to '-' to print to stderr, else set to filename to log to
    TRACE_LOGFILE = os.environ.get('SCONS_MSCOMMON_TRACE')

    # SCONS_MSCOMMON_TRACEFLAGS is internal-use so undocumented
    # refer to the internal trace source file for details
    TRACE_TRACEFLAGS = os.environ.get('SCONS_MSCOMMON_TRACEFLAGS')

    # debug configuration
    DEBUG_ENABLED = True if _HAVE_DEBUG and DEBUG_LOGFILE else False
    DEBUG_STDOUT  = True if _HAVE_DEBUG and DEBUG_ENABLED and DEBUG_LOGFILE == "-" else False
    DEBUG_LOGGING = True if _HAVE_DEBUG and DEBUG_ENABLED and not DEBUG_STDOUT else False

    # trace configuration
    TRACE_ENABLED = True if _HAVE_TRACE and TRACE_LOGFILE else False
    TRACE_STDERR  = True if _HAVE_TRACE and TRACE_ENABLED and TRACE_LOGFILE == "-" else False
    TRACE_LOGGING = True if _HAVE_TRACE and TRACE_ENABLED and not TRACE_STDERR else False

    # Rewrite filename *ONLY* when the rootname ends in "-#":
    #    root, ext = splitext(filename) -> root[:-1] + NNNN + ext
    #    example: myfile-#.txt -> myfile-0001.txt
    #    next consecutive number from largest number in target folder or 1
    #    allows individual debug/trace file names for each launch of scons

    # Sync:
    #    debug sync=False: number for next debug file
    #    trace sync=True:  number set to debug number
    #    trace sync=False: number for next trace file

    FILENAME_SERIALNBR = '-#'
    FILENAME_NBRFORMAT = '%04d'

    _last_n = None

    @classmethod
    def _get_next_serialnbr(cls, fileglob):
        matches = glob.glob(fileglob)
        if not matches:
            return 1
        matches = sorted(matches)
        root, ext = os.path.splitext(matches[-1])
        n = int(root.split(cls.FILENAME_SERIALNBR[0])[-1])
        return n + 1

    @classmethod
    def _get_filename(cls, root, n, ext):
        filename = ''.join([root, cls.FILENAME_NBRFORMAT % n, ext])
        return filename

    @classmethod
    def rewrite_filename(cls, filename, sync=False):
        if not filename:
            return filename
        root, ext = os.path.splitext(filename)
        if not root or root[-len(cls.FILENAME_SERIALNBR):] != cls.FILENAME_SERIALNBR:
            return filename
        root = root[:-1]
        if sync and cls._last_n is not None:
            n = cls._last_n
        else:
            fileglob = root + '*' + ext
            n = cls._get_next_serialnbr(fileglob)
            if not sync:
                cls._last_n = n
        filename = cls._get_filename(root, n, ext)
        return filename

    @classmethod
    def get_relative_filename(cls, filename, module_list):
        if not filename:
            return filename
        for module in module_list:
            try:
                ind = filename.rindex(module)
                return filename[ind:]
            except ValueError:
                pass
        return filename

    @classmethod
    def get_relative_module(cls, filename, module_list):
        if not filename:
            return filename
        if filename[0] == '<':
            return filename
        relname = cls.get_relative_filename(filename, module_list)
        try:
            ind = relname.rindex('.')
            modname = relname[:ind]
        except ValueError:
            modname =  relname
        modname = modname.replace('\\', '/')
        return modname

    @classmethod
    def get_module(cls, filename):
        if not filename:
            return filename
        if filename[0] == '<':
            return filename
        try:
            ind = filename.rindex('.')
            modname = filename[:ind]
        except ValueError:
            modname =  filename
        modname = modname.replace('\\', '/')
        return modname

