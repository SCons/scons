"""SCons.Script

This file implements the main() function used by the scons script.

Architecturally, this *is* the scons script, and will likely only be
called from the external "scons" wrapper.  Consequently, anything here
should not be, or be considered, part of the build engine.  If it's
something that we expect other software to want to use, it should go in
some other module.  If it's specific to the "scons" script invocation,
it goes here.

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

import time
start_time = time.time()

import os
import os.path
import random
import string
import sys
import traceback

# Strip the script directory from sys.path() so on case-insensitive
# (WIN32) systems Python doesn't think that the "scons" script is the
# "SCons" package.  Replace it with our own version directory so, if
# if they're there, we pick up the right version of the build engine
# modules.
#sys.path = [os.path.join(sys.prefix,
#                         'lib',
#                         'scons-%d' % SCons.__version__)] + sys.path[1:]

import SCons.Defaults
import SCons.Environment
import SCons.Errors
import SCons.Job
import SCons.Node
import SCons.Node.FS
from SCons.Optik import OptionParser, SUPPRESS_HELP, OptionValueError
import SCons.Script.SConscript
import SCons.Sig
import SCons.Taskmaster
from SCons.Util import display
import SCons.Warnings

#
# Task control.
#
class BuildTask(SCons.Taskmaster.Task):
    """An SCons build task."""
    def display(self, message):
        display('scons: ' + message)

    def execute(self):
        target = self.targets[0]
        if target.get_state() == SCons.Node.up_to_date:
            if self.top and target.has_builder():
                display("scons: `%s' is up to date." % str(target))
        elif target.has_builder() and not hasattr(target.builder, 'status'):
            if print_time:
                start_time = time.time()
            SCons.Taskmaster.Task.execute(self)
            if print_time:
                finish_time = time.time()
                global command_time
                command_time = command_time+finish_time-start_time
                print "Command execution time: %f seconds"%(finish_time-start_time)

    def do_failed(self, status=2):
        global exit_status
        if ignore_errors:
            SCons.Taskmaster.Task.executed(self)
        elif keep_going_on_error:
            SCons.Taskmaster.Task.fail_continue(self)
            exit_status = status
        else:
            SCons.Taskmaster.Task.fail_stop(self)
            exit_status = status
            
    def executed(self):
        t = self.targets[0]
        if self.top and not t.has_builder() and not t.side_effect:
            if not t.exists():
                sys.stderr.write("scons: *** Do not know how to make target `%s'." % t)
                if not keep_going_on_error:
                    sys.stderr.write("  Stop.")
                sys.stderr.write("\n")
                self.do_failed()
            else:
                print "scons: Nothing to be done for `%s'." % t
                SCons.Taskmaster.Task.executed(self)
        else:
            SCons.Taskmaster.Task.executed(self)

        # print the tree here instead of in execute() because
        # this method is serialized, but execute isn't:
        if print_tree and self.top:
            print
            print SCons.Util.render_tree(self.targets[0], get_all_children)
        if print_dtree and self.top:
            print
            print SCons.Util.render_tree(self.targets[0], get_derived_children)
        if print_includes and self.top:
            t = self.targets[0]
            tree = t.render_include_tree()
            if tree:
                print
                print tree

    def failed(self):
        e = sys.exc_value
        status = 2
        if sys.exc_type == SCons.Errors.BuildError:
            sys.stderr.write("scons: *** [%s] %s\n" % (e.node, e.errstr))
            if e.errstr == 'Exception':
                traceback.print_exception(e.args[0], e.args[1], e.args[2])
        elif sys.exc_type == SCons.Errors.UserError:
            # We aren't being called out of a user frame, so
            # don't try to walk the stack, just print the error.
            sys.stderr.write("\nscons: *** %s\n" % e)
        elif sys.exc_type == SCons.Errors.StopError:
            s = str(e)
            if not keep_going_on_error:
                s = s + '  Stop.'
            sys.stderr.write("scons: *** %s\n" % s)
        elif sys.exc_type == SCons.Errors.ExplicitExit:
            status = e.status
            sys.stderr.write("scons: *** [%s] Explicit exit, status %s\n" % (e.node, e.status))
        else:
            if e is None:
                e = sys.exc_type
            sys.stderr.write("scons: *** %s\n" % e)

        self.do_failed(status)

class CleanTask(SCons.Taskmaster.Task):
    """An SCons clean task."""
    def show(self):
        if (self.targets[0].has_builder() or self.targets[0].side_effect) \
           and not os.path.isdir(str(self.targets[0])):
            display("Removed " + str(self.targets[0]))
        if SCons.Script.SConscript.clean_targets.has_key(self.targets[0]):
            files = SCons.Script.SConscript.clean_targets[self.targets[0]]
            for f in files:
                SCons.Util.fs_delete(str(f), 0)

    def remove(self):
        if self.targets[0].has_builder() or self.targets[0].side_effect:
            for t in self.targets:
                try:
                    removed = t.remove()
                except OSError, e:
                    print "scons: Could not remove '%s':" % str(t), e.strerror
                else:
                    if removed:
                        display("Removed " + str(t))
        if SCons.Script.SConscript.clean_targets.has_key(self.targets[0]):
            files = SCons.Script.SConscript.clean_targets[self.targets[0]]
            for f in files:
                SCons.Util.fs_delete(str(f))

    execute = remove

    def prepare(self):
        pass

class QuestionTask(SCons.Taskmaster.Task):
    """An SCons task for the -q (question) option."""
    def prepare(self):
        pass
    
    def execute(self):
        if self.targets[0].get_state() != SCons.Node.up_to_date:
            global exit_status
            exit_status = 1
            self.tm.stop()

    def executed(self):
        pass

# Global variables

keep_going_on_error = 0
print_tree = 0
print_dtree = 0
print_time = 0
print_includes = 0
ignore_errors = 0
sconscript_time = 0
command_time = 0
exit_status = 0 # exit status, assume success by default
profiling = 0
repositories = []
sig_module = SCons.Sig.default_module
num_jobs = 1 # this is modifed by SConscript.SetJobs()

# Exceptions for this module
class PrintHelp(Exception):
    pass

# utility functions

def get_all_children(node): return node.all_children(None)

def get_derived_children(node):
    children = node.all_children(None)
    return filter(lambda x: x.has_builder(), children)

def _scons_syntax_error(e):
    """Handle syntax errors. Print out a message and show where the error
    occurred.
    """
    etype, value, tb = sys.exc_info()
    lines = traceback.format_exception_only(etype, value)
    for line in lines:
        sys.stderr.write(line+'\n')
    sys.exit(2)

def find_deepest_user_frame(tb):
    """
    Find the deepest stack frame that is not part of SCons.

    Input is a "pre-processed" stack trace in the form
    returned by traceback.extract_tb() or traceback.extract_stack()
    """
    
    tb.reverse()

    # find the deepest traceback frame that is not part
    # of SCons:
    for frame in tb:
        filename = frame[0]
        if string.find(filename, os.sep+'SCons'+os.sep) == -1:
            return frame
    return tb[0]

def _scons_user_error(e):
    """Handle user errors. Print out a message and a description of the
    error, along with the line number and routine where it occured. 
    The file and line number will be the deepest stack frame that is
    not part of SCons itself.
    """
    etype, value, tb = sys.exc_info()
    filename, lineno, routine, dummy = find_deepest_user_frame(traceback.extract_tb(tb))
    sys.stderr.write("\nscons: *** %s\n" % value)
    sys.stderr.write('File "%s", line %d, in %s\n' % (filename, lineno, routine))
    sys.exit(2)

def _scons_user_warning(e):
    """Handle user warnings. Print out a message and a description of
    the warning, along with the line number and routine where it occured.
    The file and line number will be the deepest stack frame that is
    not part of SCons itself.
    """
    etype, value, tb = sys.exc_info()
    filename, lineno, routine, dummy = find_deepest_user_frame(traceback.extract_tb(tb))
    sys.stderr.write("\nscons: warning: %s\n" % e)
    sys.stderr.write('File "%s", line %d, in %s\n' % (filename, lineno, routine))

def _scons_internal_warning(e):
    """Slightly different from _scons_user_warning in that we use the
    *current call stack* rather than sys.exc_info() to get our stack trace.
    This is used by the warnings framework to print warnings."""
    filename, lineno, routine, dummy = find_deepest_user_frame(traceback.extract_stack())
    sys.stderr.write("\nscons: warning: %s\n" % e)
    sys.stderr.write('File "%s", line %d, in %s\n' % (filename, lineno, routine))

def _scons_other_errors():
    """Handle all errors but user errors. Print out a message telling
    the user what to do in this case and print a normal trace.
    """
    print 'other errors'
    traceback.print_exc()
    sys.exit(2)

def _varargs(option, parser):
    value = None
    if parser.rargs:
        arg = parser.rargs[0]
        if arg[0] != "-":
            value = arg
            del parser.rargs[0]
    return value

def _setup_warn(arg):
    """The --warn option.  An argument to this option
    should be of the form <warning-class> or no-<warning-class>.
    The warning class is munged in order to get an actual class
    name from the SCons.Warnings module to enable or disable.
    The supplied <warning-class> is split on hyphens, each element
    is captialized, then smushed back together.  Then the string
    "SCons.Warnings." is added to the front and "Warning" is added
    to the back to get the fully qualified class name.

    For example, --warn=deprecated will enable the
    SCons.Warnings.DeprecatedWarning class.

    --warn=no-dependency will disable the
    SCons.Warnings.DependencyWarning class.

    As a special case, --warn=all and --warn=no-all
    will enable or disable (respectively) the base
    class of all warnings, which is SCons.Warning.Warning."""

    elems = string.split(string.lower(arg), '-')
    enable = 1
    if elems[0] == 'no':
        enable = 0
        del elems[0]

    if len(elems) == 1 and elems[0] == 'all':
        class_name = "Warning"
    else:
        class_name = string.join(map(string.capitalize, elems), '') + \
                     "Warning"
    try:
        clazz = getattr(SCons.Warnings, class_name)
    except AttributeError:
        sys.stderr.write("No warning type: '%s'\n" % arg)
    else:
        if enable:
            SCons.Warnings.enableWarningClass(clazz)
        else:
            SCons.Warnings.suppressWarningClass(clazz)

def _SConstruct_exists(dirname=''):
    """This function checks that an SConstruct file exists in a directory.
    If so, it returns the path of the file. By default, it checks the
    current directory.
    """
    global repositories
    for file in ['SConstruct', 'Sconstruct', 'sconstruct']:
        sfile = os.path.join(dirname, file)
        if os.path.isfile(sfile):
            return sfile
        if not os.path.isabs(sfile):
            for rep in repositories:
                if os.path.isfile(os.path.join(rep, sfile)):
                    return sfile
    return None

def _set_globals(options):
    global repositories, keep_going_on_error, print_tree, print_dtree
    global print_time, ignore_errors, print_includes

    if options.repository:
        repositories.extend(options.repository)
    keep_going_on_error = options.keep_going
    try:
        if options.debug:
            if options.debug == "tree":
                print_tree = 1
            elif options.debug == "dtree":
                print_dtree = 1
            elif options.debug == "time":
                print_time = 1
            elif options.debug == "includes":
                print_includes = 1
    except AttributeError:
        pass
    ignore_errors = options.ignore_errors

def _create_path(plist):
    path = '.'
    for d in plist:
        if os.path.isabs(d):
            path = d
        else:
            path = path + '/' + d
    return path


class OptParser(OptionParser):
    def __init__(self):
        import __main__
        import SCons
        parts = ["SCons by Steven Knight et al.:\n"]
        try:
            parts.append("\tscript: v%s.%s, %s, by %s on %s\n" % (__main__.__version__,
                                                                  __main__.__build__,
                                                                  __main__.__date__,
                                                                  __main__.__developer__,
                                                                  __main__.__buildsys__))
        except:
            # On win32 there is no scons.py, so there is no __main__.__version__,
            # hence there is no script version.
            pass 
        parts.append("\tengine: v%s.%s, %s, by %s on %s\n" % (SCons.__version__,
                                                              SCons.__build__,
                                                              SCons.__date__,
                                                              SCons.__developer__,
                                                              SCons.__buildsys__))
        parts.append("__COPYRIGHT__")
        OptionParser.__init__(self, version=string.join(parts, ''),
                              usage="usage: scons [OPTION] [TARGET] ...")

        # options ignored for compatibility
        def opt_ignore(option, opt, value, parser):
            sys.stderr.write("Warning:  ignoring %s option\n" % opt)
        self.add_option("-b", "-m", "-S", "-t", "--no-keep-going", "--stop",
                        "--touch", action="callback", callback=opt_ignore,
                        help="Ignored for compatibility.")

        self.add_option('-c', '--clean', '--remove', action="store_true",
                        dest="clean",
                        help="Remove specified targets and dependencies.")

        self.add_option('-C', '--directory', type="string", action = "append",
                        help="Change to DIRECTORY before doing anything.")

        self.add_option('--cache-disable', '--no-cache',
                        action="store_true", dest='cache_disable', default=0,
                        help="Do not retrieve built targets from CacheDir.")

        self.add_option('--cache-force', '--cache-populate',
                        action="store_true", dest='cache_force', default=0,
                        help="Copy already-built targets into the CacheDir.")

        self.add_option('--cache-show',
                        action="store_true", dest='cache_show', default=0,
                        help="Print build actions for files from CacheDir.")

        def opt_not_yet(option, opt, value, parser):
            sys.stderr.write("Warning:  the %s option is not yet implemented\n" % opt)
            sys.exit(0)
        self.add_option('-d', action="callback",
                        callback=opt_not_yet,
                        help = "Print file dependency information.")
        
        self.add_option('-D', action="store_const", const=2, dest="climb_up",
                        help="Search up directory tree for SConstruct, "
                             "build all Default() targets.")

        def opt_debug(option, opt, value, parser):
            if value == "pdb":
                if os.name == 'java':
                    python = os.path.join(sys.prefix, 'jython')
                else:
                    python = sys.executable
                args = [ python, "pdb.py" ] + \
                       filter(lambda x: x != "--debug=pdb", sys.argv)
                if sys.platform == 'win32':
                    args[1] = os.path.join(sys.prefix, "lib", "pdb.py")
                    sys.exit(os.spawnve(os.P_WAIT, args[0], args, os.environ))
                else:
                    args[1] = os.path.join(sys.prefix,
                                           "lib",
                                           "python" + sys.version[0:3],
                                           "pdb.py")
                os.execvpe(args[0], args, os.environ)
            elif value in ["tree", "dtree", "time", "includes"]:
                setattr(parser.values, 'debug', value)
            else:
                raise OptionValueError("Warning:  %s is not a valid debug type" % value)
        self.add_option('--debug', action="callback", type="string",
                        callback=opt_debug, nargs=1, dest="debug",
                        help="Print various types of debugging information.")

        self.add_option('-f', '--file', '--makefile', '--sconstruct',
                        action="append", nargs=1,
                        help="Read FILE as the top-level SConstruct file.")

        self.add_option('-h', '--help', action="store_true", default=0,
                        dest="help_msg",
                        help="Print defined help message, or this one.")

        self.add_option("-H", "--help-options",
                        action="help",
                        help="Print this message and exit.")

        self.add_option('-i', '--ignore-errors', action="store_true",
                        default=0, dest='ignore_errors',
                        help="Ignore errors from build actions.")

        self.add_option('-I', '--include-dir', action="append",
                        dest='include_dir', metavar="DIRECTORY",
                        help="Search DIRECTORY for imported Python modules.")

        self.add_option('--implicit-cache', action="store_true",
                        dest='implicit_cache',
                        help="Cache implicit dependencies")

        self.add_option('--implicit-deps-changed', action="store_true",
                        default=0, dest='implicit_deps_changed',
                        help="Ignore the cached implicit deps.")
        self.add_option('--implicit-deps-unchanged', action="store_true",
                        default=0, dest='implicit_deps_unchanged',
                        help="Ignore changes in implicit deps.")

        def opt_j(option, opt, value, parser):
            value = int(value)
            setattr(parser.values, 'num_jobs', value)
        self.add_option('-j', '--jobs', action="callback", type="int",
                        callback=opt_j, metavar="N",
                        help="Allow N jobs at once.")

        self.add_option('-k', '--keep-going', action="store_true", default=0,
                        dest='keep_going',
                        help="Keep going when a target can't be made.")

        self.add_option('--max-drift', type="int", action="store",
                        dest='max_drift',
                        help="Set the maximum system clock drift to be"
                             " MAX_DRIFT seconds.")

        self.add_option('-n', '--no-exec', '--just-print', '--dry-run',
                        '--recon', action="store_true", dest='noexec',
                        default=0, help="Don't build; just print commands.")

        def opt_profile(option, opt, value, parser):
            global profiling
            if not profiling:
                profiling = 1
                import profile
                profile.run('SCons.Script.main()', value)
                sys.exit(exit_status)
        self.add_option('--profile', nargs=1, action="callback",
                        callback=opt_profile, type="string", dest="profile",
                        help="Profile SCons and put results in PROFILE.")

        self.add_option('-q', '--question', action="store_true", default=0,
                        help="Don't build; exit status says if up to date.")

        self.add_option('-Q', dest='no_progress', action="store_true",
                        default=0,
                        help="Don't print SCons progress messages.")

        self.add_option('--random', dest="random", action="store_true",
                        default=0, help="Build dependencies in random order.")

        self.add_option('-s', '--silent', '--quiet', action="store_true",
                        default=0, help="Don't print commands.")

        self.add_option('-u', '--up', '--search-up', action="store_const",
                        dest="climb_up", default=0, const=1,
                        help="Search up directory tree for SConstruct, "
                             "build targets at or below current directory.")
        self.add_option('-U', action="store_const", dest="climb_up",
                        default=0, const=3,
                        help="Search up directory tree for SConstruct, "
                             "build Default() targets from local SConscript.")

        self.add_option("-v", "--version",
                        action="version",
                        help="Print the SCons version number and exit.")

        self.add_option('--warn', '--warning', nargs=1, action="store",
                        metavar="WARNING-SPEC",
                        help="Enable or disable warnings.")

        self.add_option('-Y', '--repository', nargs=1, action="append",
                        help="Search REPOSITORY for source and target files.")

        self.add_option('-e', '--environment-overrides', action="callback",
                        callback=opt_not_yet,
                        # help="Environment variables override makefiles."
                        help=SUPPRESS_HELP)
        self.add_option('-l', '--load-average', '--max-load', action="callback",
                        callback=opt_not_yet, type="int", dest="load_average",
                        # action="store",
                        # help="Don't start multiple jobs unless load is below "
                        #      "LOAD-AVERAGE."
                        # type="int",
                        help=SUPPRESS_HELP)
        self.add_option('--list-derived', action="callback",
                        callback=opt_not_yet,
                        # help="Don't build; list files that would be built."
                        help=SUPPRESS_HELP)
        self.add_option('--list-actions', action="callback",
                        callback=opt_not_yet,
                        # help="Don't build; list files and build actions."
                        help=SUPPRESS_HELP)
        self.add_option('--list-where', action="callback",
                        callback=opt_not_yet,
                        # help="Don't build; list files and where defined."
                        help=SUPPRESS_HELP)
        self.add_option('-o', '--old-file', '--assume-old', action="callback",
                        callback=opt_not_yet, type="string", dest="old_file",
                        # help = "Consider FILE to be old; don't rebuild it."
                        help=SUPPRESS_HELP)
        self.add_option('--override', action="callback", dest="override",
                        callback=opt_not_yet, type="string",
                        # help="Override variables as specified in FILE."
                        help=SUPPRESS_HELP)
        self.add_option('-p', action="callback",
                        callback=opt_not_yet,
                        # help="Print internal environments/objects."
                        help=SUPPRESS_HELP)
        self.add_option('-r', '-R', '--no-builtin-rules',
                        '--no-builtin-variables', action="callback",
                        callback=opt_not_yet,
                        # help="Clear default environments and variables."
                        help=SUPPRESS_HELP)
        self.add_option('-w', '--print-directory', action="callback",
                        callback=opt_not_yet,
                        # help="Print the current directory."
                        help=SUPPRESS_HELP)
        self.add_option('--no-print-directory', action="callback",
                        callback=opt_not_yet,
                        # help="Turn off -w, even if it was turned on implicitly."
                        help=SUPPRESS_HELP)
        self.add_option('--write-filenames', action="callback",
                        callback=opt_not_yet, type="string", dest="write_filenames",
                        # help="Write all filenames examined into FILE."
                        help=SUPPRESS_HELP)
        self.add_option('-W', '--what-if', '--new-file', '--assume-new',
                        dest="new_file",
                        action="callback", callback=opt_not_yet, type="string",
                        # help="Consider FILE to be changed."
                        help=SUPPRESS_HELP)
        self.add_option('--warn-undefined-variables', action="callback",
                        callback=opt_not_yet,
                        # help="Warn when an undefined variable is referenced."
                        help=SUPPRESS_HELP)

    def parse_args(self, args=None, values=None):
        opt, arglist = OptionParser.parse_args(self, args, values)
        if opt.implicit_deps_changed or opt.implicit_deps_unchanged:
            opt.implicit_cache = 1
        return opt, arglist

class SConscriptSettableOptions:
    """This class wraps an OptParser instance and provides
    uniform access to options that can be either set on the command
    line or from a SConscript file. A value specified on the command
    line always overrides a value set in a SConscript file.
    Not all command line options are SConscript settable, and the ones
    that are must be explicitly added to settable dictionary and optionally
    validated and coerced in the set() method."""
    
    def __init__(self, options):
        self.options = options

        # This dictionary stores the defaults for all the SConscript
        # settable options, as well as indicating which options
        # are SConscript settable. 
        self.settable = {'num_jobs':1,
                         'max_drift':SCons.Sig.default_max_drift,
                         'implicit_cache':0,
                         'clean':0}

    def get(self, name):
        if not self.settable.has_key(name):
            raise SCons.Error.UserError, "This option is not settable from a SConscript file: %s"%name
        if hasattr(self.options, name) and getattr(self.options, name) is not None:
            return getattr(self.options, name)
        else:
            return self.settable[name]

    def set(self, name, value):
        if not self.settable.has_key(name):
            raise SCons.Error.UserError, "This option is not settable from a SConscript file: %s"%name

        if name == 'num_jobs':
            try:
                value = int(value)
                if value < 1:
                    raise ValueError
            except ValueError, x:
                raise SCons.Errors.UserError, "A positive integer is required: %s"%repr(value)
        elif name == 'max_drift':
            try:
                value = int(value)
            except ValueError, x:
                raise SCons.Errors.UserError, "An integer is required: %s"%repr(value)
            
        self.settable[name] = value
    

def _main():
    targets = []

    # Enable deprecated warnings by default.
    SCons.Warnings._warningOut = _scons_internal_warning
    SCons.Warnings.enableWarningClass(SCons.Warnings.DeprecatedWarning)
    SCons.Warnings.enableWarningClass(SCons.Warnings.CorruptSConsignWarning)

    all_args = sys.argv[1:]
    try:
        all_args = string.split(os.environ['SCONSFLAGS']) + all_args
    except KeyError:
            # it's OK if there's no SCONSFLAGS
            pass
    parser = OptParser()
    global options, ssoptions
    options, args = parser.parse_args(all_args)
    ssoptions = SConscriptSettableOptions(options)

    if options.help_msg:
        def raisePrintHelp(text):
            raise PrintHelp, text
        SCons.Script.SConscript.HelpFunction = raisePrintHelp

    _set_globals(options)
    SCons.Node.implicit_cache = options.implicit_cache
    SCons.Node.implicit_deps_changed = options.implicit_deps_changed
    SCons.Node.implicit_deps_unchanged = options.implicit_deps_unchanged
    if options.warn:
        _setup_warn(options.warn)
    if options.noexec:
        SCons.SConf.dryrun = 1
        SCons.Action.execute_actions = None
        CleanTask.execute = CleanTask.show
    if options.question:
        SCons.SConf.dryrun = 1
        
    if options.no_progress or options.silent:
        display.set_mode(0)
    if options.silent:
        SCons.Action.print_actions = None
    if options.cache_disable:
        def disable(self): pass
        SCons.Node.FS.default_fs.CacheDir = disable
    if options.cache_force:
        SCons.Node.FS.default_fs.cache_force = 1
    if options.cache_show:
        SCons.Node.FS.default_fs.cache_show = 1
    if options.directory:
        cdir = _create_path(options.directory)
        try:
            os.chdir(cdir)
        except:
            sys.stderr.write("Could not change directory to %s\n" % cdir)

    xmit_args = []
    for a in args:
        if '=' in a:
            xmit_args.append(a)
        else:
            targets.append(a)
    SCons.Script.SConscript._scons_add_args(xmit_args)

    target_top = None
    if options.climb_up:
        target_top = '.'  # directory to prepend to targets
        script_dir = os.getcwd()  # location of script
        while script_dir and not _SConstruct_exists(script_dir):
            script_dir, last_part = os.path.split(script_dir)
            if last_part:
                target_top = os.path.join(last_part, target_top)
            else:
                script_dir = ''
        if script_dir:
            display("scons: Entering directory `%s'" % script_dir)
            os.chdir(script_dir)
        else:
            raise SCons.Errors.UserError, "No SConstruct file found."

    SCons.Node.FS.default_fs.set_toplevel_dir(os.getcwd())

    # Now that the top-level directory has been set,
    # we can initialize the default Environment.
    SCons.Defaults._default_env = SCons.Environment.Environment()

    scripts = []
    if options.file:
        scripts.extend(options.file)
    if not scripts:
        sfile = _SConstruct_exists()
        if sfile:
            scripts.append(sfile)

    if options.help_msg:
        if not scripts:
            # There's no SConstruct, but they specified -h.
            # Give them the options usage now, before we fail
            # trying to read a non-existent SConstruct file.
            parser.print_help()
            sys.exit(0)
        SCons.Script.SConscript.print_help = 1

    if not scripts:
        raise SCons.Errors.UserError, "No SConstruct file found."

    if scripts[0] == "-":
        d = SCons.Node.FS.default_fs.getcwd()
    else:
        d = SCons.Node.FS.default_fs.File(scripts[0]).dir
    SCons.Node.FS.default_fs.set_SConstruct_dir(d)

    class Unbuffered:
        def __init__(self, file):
            self.file = file
        def write(self, arg):
            self.file.write(arg)
            self.file.flush()
        def __getattr__(self, attr):
            return getattr(self.file, attr)

    sys.stdout = Unbuffered(sys.stdout)

    if options.include_dir:
        sys.path = options.include_dir + sys.path

    global repositories
    for rep in repositories:
        SCons.Node.FS.default_fs.Repository(rep)

    display("scons: Reading SConscript files ...")
    try:
        start_time = time.time()
        try:
            for script in scripts:
                SCons.Script.SConscript.SConscript(script)
        except SCons.Errors.StopError, e:
            # We had problems reading an SConscript file, such as it
            # couldn't be copied in to the BuildDir.  Since we're just
            # reading SConscript files and haven't started building
            # things yet, stop regardless of whether they used -i or -k
            # or anything else, but don't say "Stop." on the message.
            global exit_status
            sys.stderr.write("scons: *** %s\n" % e)
            exit_status = 2
            sys.exit(exit_status)
        global sconscript_time
        sconscript_time = time.time() - start_time
    except PrintHelp, text:
        display("scons: done reading SConscript files.")
        print text
        print "Use scons -H for help about command-line options."
        sys.exit(0)
    display("scons: done reading SConscript files.")

    SCons.Node.FS.default_fs.chdir(SCons.Node.FS.default_fs.Top)

    if options.help_msg:
        # They specified -h, but there was no Help() inside the
        # SConscript files.  Give them the options usage.
        parser.print_help(sys.stdout)
        sys.exit(0)

    # Now that we've read the SConscripts we can set the options
    # that are SConscript settable:
    SCons.Node.implicit_cache = ssoptions.get('implicit_cache')

    lookup_top = None
    if targets:
        # They specified targets on the command line, so if they
        # used -u, -U or -D, we have to look up targets relative
        # to the top, but we build whatever they specified.
        if target_top:
            lookup_top = SCons.Node.FS.default_fs.Dir(target_top)
            target_top = None
    else:
        # There are no targets specified on the command line,
        # so if they used -u, -U or -D, we may have to restrict
        # what actually gets built.
        if target_top:
            if options.climb_up == 1:
                # -u, local directory and below
                target_top = SCons.Node.FS.default_fs.Dir(target_top)
                lookup_top = target_top
            elif options.climb_up == 2:
                # -D, all Default() targets
                target_top = None
                lookup_top = None
            elif options.climb_up == 3:
                # -U, local SConscript Default() targets
                target_top = SCons.Node.FS.default_fs.Dir(target_top)
                def check_dir(x, target_top=target_top):
                    if hasattr(x, 'cwd') and not x.cwd is None:
                        cwd = x.cwd.srcnode()
                        return cwd == target_top
                    else:
                        # x doesn't have a cwd, so it's either not a target,
                        # or not a file, so go ahead and keep it as a default
                        # target and let the engine sort it out:
                        return 1                
                default_targets = SCons.Script.SConscript.default_targets
                if default_targets is None:
                    default_targets = []
                else:
                    default_targets = filter(check_dir, default_targets)
                SCons.Script.SConscript.default_targets = default_targets
                target_top = None
                lookup_top = None

        targets = SCons.Script.SConscript.default_targets
        if targets is None:
            targets = [SCons.Node.FS.default_fs.Dir('.')]

    if not targets:
        sys.stderr.write("scons: *** No targets specified and no Default() targets found.  Stop.\n")
        sys.exit(2)

    def Entry(x, ltop=lookup_top, ttop=target_top):
        if isinstance(x, SCons.Node.Node):
            node = x
        else:
            node = SCons.Node.Alias.default_ans.lookup(x)
            if node is None:
                node = SCons.Node.FS.default_fs.Entry(x,
                                                      directory = ltop,
                                                      create = 1)
        if ttop and not node.is_under(ttop):
            if isinstance(node, SCons.Node.FS.Dir) and ttop.is_under(node):
                node = ttop
            else:
                node = None
        return node

    nodes = filter(lambda x: x is not None, map(Entry, targets))

    calc = None
    task_class = BuildTask	# default action is to build targets
    opening_message = "Building targets ..."
    closing_message = "done building targets."
    if options.question:
        task_class = QuestionTask
    try:
        if ssoptions.get('clean'):
            task_class = CleanTask
            class CleanCalculator:
                def bsig(self, node):
                    return None
                def csig(self, node):
                    return None
                def current(self, node, sig):
                    return 0
                def write(self):
                    pass
            calc = CleanCalculator()
            opening_message = "Cleaning targets ..."
            closing_message = "done cleaning targets."
    except AttributeError:
        pass

    if not calc:
        SCons.Sig.default_calc = SCons.Sig.Calculator(module=sig_module,
                                                      max_drift=ssoptions.get('max_drift'))
        calc = SCons.Sig.default_calc

    if options.random:
        def order(dependencies):
            """Randomize the dependencies."""
            # This is cribbed from the implementation of
            # random.shuffle() in Python 2.X.
            d = dependencies
            for i in xrange(len(d)-1, 0, -1):
                j = int(random.random() * (i+1))
                d[i], d[j] = d[j], d[i]
            return d
    else:
        def order(dependencies):
            """Leave the order of dependencies alone."""
            return dependencies

    display("scons: " + opening_message)
    taskmaster = SCons.Taskmaster.Taskmaster(nodes, task_class, calc, order)

    jobs = SCons.Job.Jobs(ssoptions.get('num_jobs'), taskmaster)

    try:
        jobs.run()
    finally:
        display("scons: " + closing_message)
        if not options.noexec:
            SCons.Sig.write()

def main():
    global exit_status
    
    try:
	_main()
    except SystemExit, s:
        if s:
            exit_status = s
    except KeyboardInterrupt:
        print "Build interrupted."
        sys.exit(2)
    except SyntaxError, e:
        _scons_syntax_error(e)
    except SCons.Errors.UserError, e:
        _scons_user_error(e)
    except SCons.Errors.ConfigureDryRunError, e:
        _scons_configure_dryrun_error(e)
    except:
        _scons_other_errors()

    if print_time:
        total_time = time.time()-start_time
        scons_time = total_time-sconscript_time-command_time
        print "Total build time: %f seconds"%total_time
        print "Total SConscript file execution time: %f seconds"%sconscript_time
        print "Total SCons execution time: %f seconds"%scons_time
        print "Total command execution time: %f seconds"%command_time

    sys.exit(exit_status)
