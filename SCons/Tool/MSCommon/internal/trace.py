"""
Trace output for working with the Microsoft tool chain.
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

import sys

from .config import _MSCONFIG

class _TRACEFLAGS:

    # bitflags for selectively enabling trace output
    TRACE_DISPLAY_FUNCTION_ARGLIST   = 0b0001 # 1
    TRACE_DISPLAY_FUNCTION_LOCATION  = 0b0010 # 2
    TRACE_DISPLAY_RETURN_VALUES      = 0b0100 # 4
    TRACE_DISPLAY_ALLFRAMES_ONEBELOW = 0b1000 # 8

    # default trace output (numeric)
    TRACE_DISPLAY_DEFAULT = TRACE_DISPLAY_FUNCTION_ARGLIST | \
                            TRACE_DISPLAY_FUNCTION_LOCATION | \
                            TRACE_DISPLAY_RETURN_VALUES

    # bitflag symbols available in the SCONS_MSCOMMON_TRACEFLAGS environment variable.
    # Short names without the "TRACE_DISPLAY_" prefix are available as well.
    TRACE_DISPLAY_SYMBOLS = {
        "TRACE_DISPLAY_FUNCTION_ARGLIST"   : TRACE_DISPLAY_FUNCTION_ARGLIST,
        "TRACE_DISPLAY_FUNCTION_LOCATION"  : TRACE_DISPLAY_FUNCTION_LOCATION,
        "TRACE_DISPLAY_RETURN_VALUES"      : TRACE_DISPLAY_RETURN_VALUES,
        "TRACE_DISPLAY_ALLFRAMES_ONEBELOW" : TRACE_DISPLAY_ALLFRAMES_ONEBELOW,
    }

    # If specified, the environment variable SCONS_MSCOMMON_TRACEFLAGS string
    # is evaluated.
    #
    # Python number formats (e.g., binary, hexadecimal, decimal) are supported
    # as well as two forms of the bit field variable names (i.e., long names and
    # short names). As the string is evaluated, bitwise operators and regular
    # numeric operators may be used.  The value may be a quoted string.
    #
    # If SCONS_MSCOMMON_TRACEFLAGS is not specified, the TRACE_DISPLAY_DEFAULT
    # numeric value above is used.
    #
    # Typical usage specifications:
    #
    #    display arg lists, file locations, return values, and all frames one below:
    #       "15", "0b1111", "0xF", "1+2+4+8", "1|2|4|8", "1<<0|1<<1|1<<2|1<<3",
    #       "FUNCTION_ARGLIST|FUNCTION_LOCATION|RETURN_VALUES|ALLFRAMES_ONEBELOW",
    #       "TRACE_DISPLAY_FUNCTION_ARGLIST|TRACE_DISPLAY_FUNCTION_LOCATION|TRACE_DISPLAY_RETURN_VALUES|TRACE_DISPLAY_ALLFRAMES_ONEBELOW"
    #
    #    display arg lists, file locations, and return values [default]:
    #       "7", "0b0111', "0x7", "1+2+4", "1|2|4", "1<<0|1<<1|1<<2",
    #       "FUNCTION_ARGLIST|FUNCTION_LOCATION|RETURN_VALUES",
    #       "TRACE_DISPLAY_FUNCTION_ARGLIST|TRACE_DISPLAY_FUNCTION_LOCATION|TRACE_DISPLAY_RETURN_VALUES"
    #
    #    display arg lists, and return values:
    #       "5", "0b0101", "0x5", "1+4", "1|4", "1<<0|1<<2",
    #       "FUNCTION_ARGLIST|RETURN_VALUES",
    #       "TRACE_DISPLAY_FUNCTION_ARGLIST|TRACE_DISPLAY_RETURN_VALUES"
    #
    #    display arg lists, and file locations:
    #       "3", "0b0011", "0x3", "1+2", "1|2", "1<<0|1<<1",
    #       "FUNCTION_ARGLIST|FUNCTION_LOCATION",
    #       "TRACE_DISPLAY_FUNCTION_ARGLIST|TRACE_DISPLAY_FUNCTION_LOCATION"
    #
    # Examples (all produce the same output):
    #
    #    set SCONS_MSCOMMON_TRACEFLAGS=15
    #    set SCONS_MSCOMMON_TRACEFLAGS=0b1111
    #    set SCONS_MSCOMMON_TRACEFLAGS=0xF
    #    set SCONS_MSCOMMON_TRACEFLAGS="1+2+4+8"
    #    set SCONS_MSCOMMON_TRACEFLAGS="1|2|4|8"
    #    set SCONS_MSCOMMON_TRACEFLAGS="1<<0|1<<1|1<<2|1<<3"
    #    set SCONS_MSCOMMON_TRACEFLAGS="FUNCTION_ARGLIST|FUNCTION_LOCATION|RETURN_VALUES|ALLFRAMES_ONEBELOW"
    #    set "SCONS_MSCOMMON_TRACEFLAGS=TRACE_DISPLAY_FUNCTION_ARGLIST|TRACE_DISPLAY_FUNCTION_LOCATION|TRACE_DISPLAY_RETURN_VALUES|TRACE_DISPLAY_ALLFRAMES_ONEBELOW"
    #

    _TRACEFLAGS = None

    @classmethod
    def get_trace_display_traceflags(cls):
        # evaluate environment variable once
        if cls._TRACEFLAGS is not None:
            return cls._TRACEFLAGS
        # environment variable not defined
        if _MSCONFIG.TRACE_TRACEFLAGS is None:
            cls._TRACEFLAGS = cls.TRACE_DISPLAY_DEFAULT
            return cls._TRACEFLAGS
        envstr = _MSCONFIG.TRACE_TRACEFLAGS
        # iteratively strip all balanced outer quotes
        while 1:
            if envstr.startswith('"') and envstr.endswith('"'):
                # strip "..."
                envstr = envstr.strip('"')
            elif envstr.startswith("'") and envstr.endswith("'"):
                # strip '...'
                envstr = envstr.strip("'")
            elif envstr.startswith('"""') and envstr.endswith('"""'):
                # strip """..."""
                envstr = envstr.strip('"""')
            else:
                # no balanced outer quotes
                break
            # if environment variable is empty use default
            if not envstr:
                cls._TRACEFLAGS = cls.TRACE_DISPLAY_DEFAULT
                return cls._TRACEFLAGS
        # attempt simple conversion for numeric strings
        try:
            cls._TRACEFLAGS = int(envstr, 0)
            return cls._TRACEFLAGS
        except ValueError:
            pass
        # prepare symbols: long names and short names
        symbols = {}
        prefix = "TRACE_DISPLAY_"
        for key, value in cls.TRACE_DISPLAY_SYMBOLS.items():
            symbols[key] = value
            if key.startswith(prefix):
                symbols[key[len(prefix):]] = value
        # compile the environment string
        try:
            code = compile(envstr, "<string>", "eval")
        except SyntaxError:
            raise ValueError('Trace display compilation failed: %s' % cls.TRACEFLAGS_ENV)
        # verify the environment string contains only known symbols
        for co_name in code.co_names:
            if co_name not in symbols:
                # NameError
                raise ValueError("Trace display symbol undefined: %s" % co_name)
        # evaluate the environment string
        try:
            cls._TRACEFLAGS = eval(code, {"__builtins__": {}}, symbols)
        except (TypeError, ZeroDivisionError):
            raise ValueError('Trace display evaluation failed: %s' % cls.TRACEFLAGS_ENV)
        return cls._TRACEFLAGS

class _TRACE:

    modulelist = (
        # python library and below: correct iff scons does not have a lib folder
        'lib',
        # scons modules
        'SCons', 'test', 'scons'
    )

    # trace display specification
    TRACEFLAGS = _TRACEFLAGS.get_trace_display_traceflags()

    # display function argument lists w/select values
    DISPLAY_FUNCTION_ARGLIST = True if TRACEFLAGS & _TRACEFLAGS.TRACE_DISPLAY_FUNCTION_ARGLIST else False

    # display function locations: file and line number
    DISPLAY_FUNCTION_LOCATION = True if TRACEFLAGS & _TRACEFLAGS.TRACE_DISPLAY_FUNCTION_LOCATION else False

    # display function return values
    DISPLAY_RETURN_VALUES = True if TRACEFLAGS & _TRACEFLAGS.TRACE_DISPLAY_RETURN_VALUES else False

    # display all frames one below the current module(s)
    DISPLAY_ALLFRAMES_ONEBELOW = True if TRACEFLAGS & _TRACEFLAGS.TRACE_DISPLAY_ALLFRAMES_ONEBELOW else False

    # number of frames above the current module
    FRAME_CALLER_FRAMES = 5

    # function argument values of interest
    FRAME_ARGUMENT_VALUES = (
        'version',
        'msvc_version',
        'name',
        'key',
        'path',
        'value',
        'host_arch',
        'target_arch',
        'vc_specific_version',
        'vc_product',
        'search_version',
        'rollback',
    )

    # when enabled, ignore these module/function returns
    RETURN_IGNORELIST_ENABLED = True
    RETURN_IGNORELIST_FUNCTIONS = [
        # functions known to return None
        ('lib/_weakrefset', '_remove'),
        ('lib/codecs', '__init__'),
        ('lib/subprocess', 'Close'),
        ('lib/subprocess', '__del__'),
        ('lib/logging/__init__', 'debug'),
        ('SCons/Environment', '__setitem__'),
        ('SCons/Environment', 'PrependENVPath'),
        ('SCons/Tool/MSCommon/sdk', '__init__'),
        ('SCons/Tool/MSCommon/vs', '__init__'),
        ('SCons/Tool/MSCommon/vc', '__init__'),
        ('SCons/Tool/MSCommon/internal/debug', 'debug'),
        ('SCons/Tool/MSCommon/internal/trace', 'trace'),
        ('SCons/Tool/MSCommon/common', 'debug'),
        ('SCons/Tool/MSCommon/common', 'add_env'),
        ('SCons/Tool/MSCommon/common', 'write_script_env_cache'),
    ]

    # ignore internal debug calls
    DEBUG_IGNORELIST_ENABLED = True
    DEBUG_IGNORELIST_FUNCTIONS = []

    if not _MSCONFIG.DEBUG_LOGGING:
        DEBUG_IGNORELIST_FUNCTIONS += [
            # ignore internal debug calls when not using the logging module
            ('SCons/Tool/MSCommon/internal/debug', 'debug'),
            ('SCons/Tool/MSCommon/common', 'debug'),
        ]
    else:
        DEBUG_IGNORELIST_FUNCTIONS += [
            # ignore internal debug filter calls when using the logging module
            ('SCons/Tool/MSCommon/internal/config', 'get_relative_filename'),
            ('SCons/Tool/MSCommon/internal/debug', 'filter'),
        ]

    DEBUG_ALLOWLIST_ENABLED = _MSCONFIG.DEBUG_LOGGING
    DEBUG_ALLOWLIST_FUNCTIONS = [
        # keep external debug calls when using the logging module
        ('lib/logging/__init__', 'debug'),
    ]

    # function call indentation
    FRAME_INDENT_NSPACES = 2
    FRAME_INDENT_LITERAL = " " * FRAME_INDENT_NSPACES

    # start of new call chain
    FRAME_ENTRY_DEPTH = 0
    FRAME_ENTRY_LOCATION = []
    FRAME_ENTRY_SLOT = -1

    # chain length of previous display
    FRAME_LAST_CHAINLENGTH = 0

    # root module of this script (e.g, MSCommon)
    ROOT_MODULE = __name__.split('.')[-3]

    # trace events of interest
    if DISPLAY_RETURN_VALUES:
        FRAME_TRACE_EVENTS = ('call', 'return')
    else:
        FRAME_TRACE_EVENTS = ('call', )

    # trace file processing
    if _MSCONFIG.TRACE_STDERR:
        TRACE_FH = sys.stderr
    elif _MSCONFIG.TRACE_LOGGING:
        try:
            TRACE_FH = open(_MSCONFIG.rewrite_filename(_MSCONFIG.TRACE_LOGFILE, sync=_MSCONFIG.DEBUG_LOGGING), 'w')
        except IOError as e:
            TRACE_FH = None
            raise e
    else:
        TRACE_FH = None

    @classmethod
    def get_frame_arglist(cls, frame):
        args = "("
        for i in range(frame.f_code.co_argcount):
            if i: args += ', '
            name = frame.f_code.co_varnames[i]
            args += name
            if name in cls.FRAME_ARGUMENT_VALUES:
                args += "=%s" % repr(frame.f_locals[name])
        args += ")"
        return args

    @classmethod
    def print_message(cls, message):
        print(message, file=cls.TRACE_FH, flush=True)

    @classmethod
    def display_frame(cls, frame, indent, divider=False):
        current_func = frame.f_code.co_name
        if cls.DISPLAY_FUNCTION_LOCATION:
            current_file = _MSCONFIG.get_relative_filename(frame.f_code.co_filename, cls.modulelist)
            if frame.f_back:
                from_file = _MSCONFIG.get_relative_filename(frame.f_back.f_code.co_filename, cls.modulelist)
                from_line = frame.f_back.f_lineno
                if frame.f_back.f_code.co_filename == frame.f_code.co_filename:
                    from_where = " from %d" % from_line
                else:
                    from_where = " from %s:%d" % (from_file, from_line)
            else:
                from_where = ""
            location = " <%s:%d%s>" % (current_file, frame.f_lineno, from_where)
        else:
            location = ""

        if cls.DISPLAY_FUNCTION_ARGLIST:
            arglist = cls.get_frame_arglist(frame)
        else:
            arglist = ""

        outstr = "%s%s%s%s" % (indent, current_func, arglist, location)
        cls.print_message(outstr)

        if divider and cls.FRAME_CALLER_FRAMES > 1:
            divstr = "%s%s" % (indent, "-" * len(outstr))
            cls.print_message(divstr)

    @classmethod
    def display_frame_return(cls, frame, arg, indent):
        current_func = frame.f_code.co_name
        if cls.DISPLAY_FUNCTION_LOCATION:
            current_file = frame.f_code.co_filename.split('\\')[-1]
            location = "(%s:%d) " % (current_file, frame.f_lineno)
        else:
            location = " "
        outstr = "%sreturn %s%s-> %s" % (indent, current_func, location, arg)
        cls.print_message(outstr)

    @classmethod
    def get_relmodule_caller_callee(cls, frame):
        # default caller, callee values
        rval = (None, None)
        if not frame:
            return '', rval, rval
        # relative module name
        relmodule = _MSCONFIG.get_relative_module(frame.f_code.co_filename, cls.modulelist)
        # callee parent and leaf modules
        modname = _MSCONFIG.get_module(frame.f_code.co_filename)
        callee = modname.split('/')[-2:]
        if len(callee) < 2:
            callee = [None] + callee
        # check for caller
        if not frame.f_back:
            return relmodule, rval, callee
        # caller parent and leaf modules
        modname = _MSCONFIG.get_module(frame.f_back.f_code.co_filename)
        caller = modname.split('/')[-2:]
        if len(caller) < 2:
            caller = [None] + caller
        return relmodule, caller, callee

    @classmethod
    def is_allowed(cls, event, relmodule, function):
        pair = (relmodule, function)
        if cls.DISPLAY_ALLFRAMES_ONEBELOW:
            return True
        if event == 'call':
            if cls.DEBUG_ALLOWLIST_ENABLED and pair in cls.DEBUG_ALLOWLIST_FUNCTIONS:
                return True
        return False

    @classmethod
    def is_ignored(cls, event, relmodule, function):
        pair = (relmodule, function)
        if event == 'return':
            if cls.RETURN_IGNORELIST_ENABLED and pair in cls.RETURN_IGNORELIST_FUNCTIONS:
                return True
        else:
            if cls.DEBUG_IGNORELIST_ENABLED and pair in cls.DEBUG_IGNORELIST_FUNCTIONS:
                return True
            if cls.DISPLAY_ALLFRAMES_ONEBELOW:
                return False
            if function[0] == "<":
                # ignore native python calls (e.g., list comprehension)
                return True
        return False

    @classmethod
    def trace_current_module(cls, frame, event, arg):

        rval = cls.trace_current_module

        if event not in cls.FRAME_TRACE_EVENTS:
            return rval

        relmodule, (caller_parent, _), (callee_parent, _) = cls.get_relmodule_caller_callee(frame)

        # ignore events that are more than one frame below root module
        if callee_parent != cls.ROOT_MODULE:

            # at most one frame deep
            if caller_parent != cls.ROOT_MODULE:
                return rval

            # ignore frames that are not explicitly listed
            if not cls.is_allowed(event, relmodule, frame.f_code.co_name):
                return rval

        # ignore frames that are explicitly listed
        if cls.is_ignored(event, relmodule, frame.f_code.co_name):
            return None

        # walk the stack frames above the current call
        # save the slot for the top-most module entry point
        # construct a frame chain: root -> current frame

        entry_slot = None
        frame_chain = []
        f = frame
        while f:
            if cls.ROOT_MODULE in f.f_code.co_filename:
                entry_slot = len(frame_chain)
            frame_chain.insert(0, f)
            f = f.f_back

        # calculate the starting slot: up to n frames above the entry point
        top = entry_slot + cls.FRAME_CALLER_FRAMES
        if top >= len(frame_chain):
            top = len(frame_chain) - 1

        # adjust the frame chain: starting slot -> current frame
        offset = len(frame_chain) - top - 1
        frame_chain = frame_chain[offset:]

        # entry location is the filename and line number of the first frame
        entry_location = [(f.f_code.co_filename, f.f_lineno) for f in frame_chain[:1]]

        if not cls.FRAME_ENTRY_LOCATION:
            start_new_chain = True
        else:
            start_new_chain = entry_location != cls.FRAME_ENTRY_LOCATION

        if start_new_chain:

            # new call chain: write all of the frames

            if cls.FRAME_ENTRY_LOCATION:
                cls.print_message("")

            divider_index = cls.FRAME_CALLER_FRAMES - 1

            indent = ''
            for i, f in enumerate(frame_chain):
                if i:
                    indent += cls.FRAME_INDENT_LITERAL
                cls.display_frame(f, indent, divider=(i==divider_index))

            # save the entry point location information
            cls.FRAME_ENTRY_SLOT = entry_slot
            cls.FRAME_ENTRY_LOCATION = entry_location
            cls.FRAME_ENTRY_DEPTH = len(frame_chain) - 1

        else:

            # existing call chain

            gap = len(frame_chain) - cls.FRAME_LAST_CHAINLENGTH
            if gap > 1:
                # positive gap greater than one: fill in missing frames
                n_indent = cls.FRAME_ENTRY_DEPTH
                n_indent += entry_slot - cls.FRAME_ENTRY_SLOT - gap
                n_indent += 1
                indent = cls.FRAME_INDENT_LITERAL * n_indent
                for f in frame_chain[1:gap]:
                    cls.display_frame(f, indent)
                    indent += cls.FRAME_INDENT_LITERAL

            # display current frame
            n_indent = cls.FRAME_ENTRY_DEPTH
            n_indent += entry_slot - cls.FRAME_ENTRY_SLOT
            indent = cls.FRAME_INDENT_LITERAL * n_indent

            if event == 'return':
                indent += cls.FRAME_INDENT_LITERAL
                cls.display_frame_return(frame, repr(arg), indent)
            else:
                cls.display_frame(frame, indent)

        cls.FRAME_LAST_CHAINLENGTH = len(frame_chain)

        return rval

    @classmethod
    def trace(cls):
        sys.settrace(cls.trace_current_module)

if _MSCONFIG.TRACE_ENABLED:
    _TRACE.trace()

