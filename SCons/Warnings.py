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

"""The warnings framework for SCons.

Warnings are simple classes, as in Python; inheritance is the interesting
characteristic.

All warnings start life out disabled, meaning no message will be emitted;
scons main() then calls enableWarningClass to add the WarningOnByDefault
and DeprecatedWarning classes to an override table.  That table can be
augmented by command-line --warn and --werror arguments, and by calls
to SetOption, to enable/disable specific (or all) warnings, and to
enable/disable treating warnings as errors.

When the warn function is called, it decides, based on the override table,
whether or not to print a message (or raise an error) for that warning.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
from collections import namedtuple

import SCons.Errors

class SConsWarning(SCons.Errors.UserError):
    pass

class WarningOnByDefault(SConsWarning):
    pass


# NOTE: If you add a new warning class here, also add to --warn in the man page.
#
# Not all warnings are defined here, some are defined in the module of use.
# Such warnings cannot be controlled by the --warn/--werror options,
# unless they monkeypatch themselves into this module's namespace:
# the process_warn_strings() function below looks up the warning in
# our globals() dictionary.

class TargetNotBuiltWarning(SConsWarning):  # Should go to OnByDefault
    pass

class CacheVersionWarning(WarningOnByDefault):
    pass

class CacheWriteErrorWarning(SConsWarning):
    pass

class CorruptSConsignWarning(WarningOnByDefault):
    pass

class DependencyWarning(SConsWarning):
    pass

class DevelopmentVersionWarning(WarningOnByDefault):
    pass

class DuplicateEnvironmentWarning(WarningOnByDefault):
    pass

class FutureReservedVariableWarning(WarningOnByDefault):
    pass

class LinkWarning(WarningOnByDefault):
    pass

class MisleadingKeywordsWarning(WarningOnByDefault):
    pass

class MissingSConscriptWarning(WarningOnByDefault):
    pass

class NoObjectCountWarning(WarningOnByDefault):
    pass

class NoParallelSupportWarning(WarningOnByDefault):
    pass

class ReservedVariableWarning(WarningOnByDefault):
    pass

class StackSizeWarning(WarningOnByDefault):
    pass

class VisualCMissingWarning(WarningOnByDefault):
    pass

# Used when MSVC_VERSION and MSVS_VERSION do not point to the
# same version (MSVS_VERSION is deprecated)
class VisualVersionMismatch(WarningOnByDefault):
    pass

class VisualStudioMissingWarning(SConsWarning):
    pass

class FortranCxxMixWarning(LinkWarning):
    pass


# Deprecation warnings
class FutureDeprecatedWarning(SConsWarning):
    pass

class DeprecatedWarning(SConsWarning):
    pass

class MandatoryDeprecatedWarning(DeprecatedWarning):
    pass

# Special case; base always stays DeprecatedWarning
class PythonVersionWarning(DeprecatedWarning):
    pass

class DeprecatedSourceCodeWarning(FutureDeprecatedWarning):
    pass

class TaskmasterNeedsExecuteWarning(DeprecatedWarning):
    pass

class DeprecatedOptionsWarning(MandatoryDeprecatedWarning):
    pass

class DeprecatedDebugOptionsWarning(MandatoryDeprecatedWarning):
    pass

class DeprecatedMissingSConscriptWarning(DeprecatedWarning):
    pass


# A table of requests to override warning defaults.
# This is a list of Warntype tuples consisting of a class object and a value.
# A False value means disabled, True means enabled,
Warntype = namedtuple("Warntype", 'cls, warn, error', defaults=(False, False))
_enabled = []

# If true, raise any warning as an exception
_warningAsException = False

# If not None, a function to call with the warning
_warningOut = None

def _has_warn(clazz):
    """Look backwards to see if a warning was set that applies to clazz."""
    for w in _enabled:
        if issubclass(clazz, w.cls):
            if w.warn:
                return True
            break
    return False

def _has_exc(clazz):
    """Look backwards to see if a werror was set that applies to clazz."""
    for w in _enabled:
        if issubclass(clazz, w.cls):
            if w.error:
                return True
            break
    return False

# Tracking two different outcomes on a warning introduces complexity.
# Matching is done using a find-from-left search, so each new request
# is inserted at the beginning so it takes priority.  In order to
# remember what was already in effect for a class, we include that
# information in the new entry, so, e.g. if the request is to suppress
# exceptions for Foo, we add the most-recent-found status of warnings
# for Foo into that entry. Otherwise, even if warnings were previously
# enabled, turning off exceptions would also turn off warnings.

def enableWarningClass(clazz):
    """Enables all warnings of clazz or subclass of clazz."""
    _enabled.insert(0, Warntype(clazz, warn=True, error=_has_exc(clazz)))

def suppressWarningClass(clazz):
    """Suppresses all warnings of clazz or subclass of clazz."""
    _enabled.insert(0, Warntype(clazz, warn=False, error=_has_exc(clazz)))

def enableWarningClassException(clazz):
    """Marks warning of type clazz or subclass of clazz to raise exception."""
    _enabled.insert(0, Warntype(clazz, error=True, warn=_has_warn(clazz)))

def suppressWarningClassException(clazz):
    """Marks warning of clazz or subclass of clazz to not raise exception."""
    _enabled.insert(0, Warntype(clazz, error=False, warn=_has_warn(clazz)))

def warningAsException(flag=True):
    """Set global _warningAsExeption flag.

    Args:
        flag: value to set warnings-as-exceptions to [default: True]

    Returns:
        The previous value.
    """
    global _warningAsException
    old = _warningAsException
    _warningAsException = flag
    return old

def warn(clazz, *args):
    """Issue a warning, respecting enable/disable/exception requests.

    Check if warnings for this class are enabled.
    If warnings are treated as exceptions, raise exception.
    Use the global warning-emitter _warningOut, which allows selecting
    different ways of presenting a traceback (see Script/Main.py)
    """
    if len(args) == 1:
        # if called with a single arg (aka str), don't pass a tuple,
        # it makes the resulting msg look ugly.
        warning = clazz(args[0])
    else:
        warning = clazz(args)
    for w in _enabled:
        if isinstance(warning, w.cls):
            if w.error or _warningAsException:
                raise warning
            if w.warn and _warningOut:
                _warningOut(warning)
            break

def process_warn_strings(arguments, flavor="warn"):
    """Process requests to change state of warnings.

    The requests are strings passed via the --warn option or the
    SetOption('warn') function, unless the flavor is "werror",
    in which case the corresponding --werror / SetOption('werror')
    is the source.

    An argument to this option should be of the form "class-name"
    or "no-class-name".  The class name is munged and has
    the suffix "Warning" added in order to get one of the classes
    defined in this module, which will be used to call the
    enable/disable functions.

    For example, "--warn=deprecated" will enable the DeprecatedWarning
    class.  "--warn=no-dependency" will disable the DependencyWarning class.

    As a special case, --warn=all and --warn=no-all will enable or
    disable (respectively) the base class of all SCons warnings.

    """

    def _classmunge(s):
        """Convert a warning argument to SConsCase.

        Returns CamelCase, except "Scons" is changed to "SCons".
        Dashes are stripped.
        """
        s = s.replace("-", " ").title().replace(" ", "")
        return s.replace("Scons", "SCons")

    for arg in arguments:
        enable = True
        if arg.startswith("no-"):
            enable = False
            arg = arg[len("no-") :]
        if arg == 'all':
            class_name = "SConsWarning"
        else:
            class_name = _classmunge(arg) + 'Warning'
        try:
            clazz = globals()[class_name]
        except KeyError:
            sys.stderr.write("No warning type: '%s'\n" % arg)
        else:
            if flavor == "warn":
                if enable:
                    enableWarningClass(clazz)
                elif issubclass(clazz, MandatoryDeprecatedWarning):
                    fmt = "Can not disable mandatory warning: '%s'\n"
                    sys.stderr.write(fmt % arg)
                else:
                    suppressWarningClass(clazz)
            elif flavor == "error":
                if enable:
                    enableWarningClassException(clazz)
                else:
                    suppressWarningClassException(clazz)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
