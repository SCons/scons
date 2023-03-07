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
A testing framework for the SCons software construction tool.

A TestSCons environment object is created via the usual invocation:

    test = TestSCons()

TestScons is a subclass of TestCommon, which in turn is a subclass
of TestCmd), and hence has available all of the methods and attributes
from those classes, as well as any overridden or additional methods or
attributes defined in this subclass.
"""

import os
import re
import shutil
import sys
import time
import subprocess as sp
import zipfile
from collections import namedtuple

from TestCommon import *
from TestCommon import __all__, _python_
from SCons.Util import get_hash_format, get_current_hash_algorithm_used

from TestCmd import Popen
from TestCmd import PIPE

# Some tests which verify that SCons has been packaged properly need to
# look for specific version file names.  Replicating the version number
# here provides some independent verification that what we packaged
# conforms to what we expect.

default_version = '4.5.2ayyyymmdd'

# TODO: these need to be hand-edited when there are changes
python_version_unsupported = (3, 6, 0)
python_version_deprecated = (3, 6, 0)
python_version_supported_str = "3.6.0"  # str of lowest non-deprecated version

SConsVersion = default_version

__all__.extend([
    'TestSCons',
    'machine',
    'python',
    '_exe',
    '_obj',
    '_shobj',
    'shobj_',
    'lib_',
    '_lib',
    'dll_',
    '_dll'
])

machine_map = {
    'i686': 'i386',
    'i586': 'i386',
    'i486': 'i386',
}

try:
    uname = os.uname
except AttributeError:
    # Windows doesn't have a uname() function.  We could use something like
    # sys.platform as a fallback, but that's not really a "machine," so
    # just leave it as None.
    machine = None
else:
    machine = uname()[4]
    machine = machine_map.get(machine, machine)

_exe = exe_suffix
_obj = obj_suffix
_shobj = shobj_suffix
shobj_ = shobj_prefix
_lib = lib_suffix
lib_ = lib_prefix
_dll = dll_suffix
dll_ = dll_prefix

if sys.platform == 'cygwin':
    # On Cygwin, os.path.normcase() lies, so just report back the
    # fact that the underlying Win32 OS is case-insensitive.
    def case_sensitive_suffixes(s1, s2):
        return 0
else:
    def case_sensitive_suffixes(s1, s2):
        return (os.path.normcase(s1) != os.path.normcase(s2))

file_expr = r"""File "[^"]*", line \d+, in [^\n]+
"""


# re.escape escapes too much.
def re_escape(str):
    for c in '\\.[]()*+?':  # Not an exhaustive list.
        str = str.replace(c, f"\\{c}")
    return str


#
# Helper functions that we use as a replacement to the default re.match
# when searching for special strings in stdout/stderr.
#
def search_re(out, l):
    """ Search the regular expression 'l' in the output 'out'
        and return the start index when successful.
    """
    m = re.search(l, out)
    if m:
        return m.start()

    return None


def search_re_in_list(out, l):
    """ Search the regular expression 'l' in each line of
        the given string list 'out' and return the line's index
        when successful.
    """
    for idx, o in enumerate(out):
        m = re.search(l, o)
        if m:
            return idx

    return None


#
# Helpers for handling Python version numbers
#
def python_version_string():
    return sys.version.split()[0]


def python_minor_version_string():
    return sys.version[:3]


def unsupported_python_version(version=sys.version_info):
    return version < python_version_unsupported


def deprecated_python_version(version=sys.version_info):
    return version < python_version_deprecated


if deprecated_python_version():
    msg = r"""
scons: warning: Support for pre-%s Python version (%s) is deprecated.
    If this will cause hardship, contact scons-dev@scons.org
"""
    deprecated_python_expr = (
        re_escape(msg % (python_version_supported_str, python_version_string()))
        + file_expr
    )
    del msg
else:
    deprecated_python_expr = ""


def initialize_sconsflags(ignore_python_version):
    """
    Add the --warn=no-python-version option to SCONSFLAGS for every
    command so test scripts don't have to filter out Python version
    deprecation warnings.
    Same for --warn=no-visual-c-missing.
    """
    save_sconsflags = os.environ.get('SCONSFLAGS')
    if save_sconsflags:
        sconsflags = [save_sconsflags]
    else:
        sconsflags = []
    if ignore_python_version and deprecated_python_version():
        sconsflags.append('--warn=no-python-version')
    # Provide a way to suppress or provide alternate flags for
    # TestSCons purposes by setting TESTSCONS_SCONSFLAGS.
    # (The intended use case is to set it to null when running
    # timing tests of earlier versions of SCons which don't
    # support the --warn=no-visual-c-missing warning.)
    visual_c = os.environ.get('TESTSCONS_SCONSFLAGS',
                              '--warn=no-visual-c-missing')
    if visual_c and visual_c not in sconsflags:
        sconsflags.append(visual_c)
    os.environ['SCONSFLAGS'] = ' '.join(sconsflags)
    return save_sconsflags


def restore_sconsflags(sconsflags):
    if sconsflags is None:
        del os.environ['SCONSFLAGS']
    else:
        os.environ['SCONSFLAGS'] = sconsflags


# Helpers for Configure()'s config.log processing
ConfigCheckInfo = namedtuple('ConfigCheckInfo',
                             ['check_string', 'result', 'cached', 'temp_filename'])
#         check_string: the string output to for this checker
#         results : The expected results for each check
#         cached  : If the corresponding check is expected to be cached
#         temp_filename : The name of the generated tempfile for this check


class NoMatch(Exception):
    """
    Exception for matchPart to indicate there was no match found in the passed logfile
    """
    def __init__(self, p):
        self.pos = p


def match_part_of_configlog(log, logfile, lastEnd, NoMatch=NoMatch):
    """
    Match part of the logfile
    """
    # print("Match:\n%s\n==============\n%s" % (log , logfile[lastEnd:]))
    m = re.match(log, logfile[lastEnd:])
    if not m:
        raise NoMatch(lastEnd)
    return m.end() + lastEnd


class TestSCons(TestCommon):
    """Class for testing SCons.

    This provides a common place for initializing SCons tests,
    eliminating the need to begin every test with the same repeated
    initializations.
    """

    scons_version = SConsVersion
    javac_is_gcj = False

    def __init__(self, **kw):
        """Initialize an SCons testing object.

        If they're not overridden by keyword arguments, this
        initializes the object with the following default values:

                program = 'scons' if it exists,
                          else 'scons.py'
                interpreter = 'python'
                match = match_exact
                workdir = ''

        The workdir value means that, by default, a temporary workspace
        directory is created for a TestSCons environment.  In addition,
        this method changes directory (chdir) to the workspace directory,
        so an explicit "chdir = '.'" on all of the run() method calls
        is not necessary.
        """
        self.orig_cwd = os.getcwd()
        self.external = os.environ.get('SCONS_EXTERNAL_TEST', 0)

        if not self.external:
            try:
                script_dir = os.environ['SCONS_SCRIPT_DIR']
            except KeyError:
                pass
            else:
                os.chdir(script_dir)
        if 'program' not in kw:
            kw['program'] = os.environ.get('SCONS')
            if not kw['program']:
                if not self.external:
                    if os.path.exists('scons'):
                        kw['program'] = 'scons'
                    else:
                        kw['program'] = 'scons.py'
                else:
                    kw['program'] = 'scons'
                    kw['interpreter'] = ''
            elif not self.external and not os.path.isabs(kw['program']):
                kw['program'] = os.path.join(self.orig_cwd, kw['program'])
        if 'interpreter' not in kw and not os.environ.get('SCONS_EXEC'):
            kw['interpreter'] = [python, ]
        if 'match' not in kw:
            kw['match'] = match_exact
        if 'workdir' not in kw:
            kw['workdir'] = ''

        # Term causing test failures due to bogus readline init
        # control character output on FC8
        # TERM can cause test failures due to control chars in prompts etc.
        os.environ['TERM'] = 'dumb'

        self.ignore_python_version = kw.get('ignore_python_version', 1)
        if kw.get('ignore_python_version', -1) != -1:
            del kw['ignore_python_version']

        super().__init__(**kw)

        if not self.external:
            import SCons.Node.FS
            if SCons.Node.FS.default_fs is None:
                SCons.Node.FS.default_fs = SCons.Node.FS.FS()

        try:
            self.fixture_dirs = (os.environ['FIXTURE_DIRS']).split(os.pathsep)
        except KeyError:
            pass

    def Environment(self, ENV=None, *args, **kw):
        """
        Return a construction Environment that optionally overrides
        the default external environment with the specified ENV.
        """
        if not self.external:
            import SCons.Environment
            import SCons.Errors
            if ENV is not None:
                kw['ENV'] = ENV
            try:
                return SCons.Environment.Environment(*args, **kw)
            except (SCons.Errors.UserError, SCons.Errors.InternalError):
                return None

        return None

    def detect(self, var, prog=None, ENV=None, norm=None):
        """
        Return the detected path to a tool program.

        Searches first the named construction variable, then
        the SCons path.

        Args:
            var: name of construction variable to check for tool name.
            prog: tool program to check for.
            ENV: if present, kwargs to initialize an environment that
                will be created to perform the lookup.
            norm: if true, normalize any returned path looked up in
                the environment to use UNIX-style path separators.

        Returns: full path to the tool, or None.

        """
        env = self.Environment(ENV)
        if env:
            v = env.subst(f"${var}")
            if not v:
                return None
            if prog is None:
                prog = v
            if v != prog:
                return None
            result = env.WhereIs(prog)
            if result and norm and os.sep != '/':
                result = result.replace(os.sep, '/')
            return result

        return self.where_is(prog)

    def detect_tool(self, tool, prog=None, ENV=None):
        """
        Given a tool (i.e., tool specification that would be passed
        to the "tools=" parameter of Environment()) and a program that
        corresponds to that tool, return true if and only if we can find
        that tool using Environment.Detect().

        By default, prog is set to the value passed into the tools parameter.
        """

        if not prog:
            prog = tool
        env = self.Environment(ENV, tools=[tool])
        if env is None:
            return None
        return env.Detect([prog])

    def where_is(self, prog, path=None, pathext=None):
        """
        Given a program, search for it in the specified external PATH,
        or in the actual external PATH if none is specified.
        """
        if path is None:
            path = os.environ['PATH']
        if self.external:
            if isinstance(prog, str):
                prog = [prog]
            for p in prog:
                result = TestCmd.where_is(self, p, path, pathext)
                if result:
                    return os.path.normpath(result)
        else:
            import SCons.Environment
            env = SCons.Environment.Environment()
            return env.WhereIs(prog, path, pathext)

        return None

    def wrap_stdout(self, build_str="", read_str="", error=0, cleaning=0) -> str:
        """Wraps "expect" strings in SCons boilerplate.

        Given strings of expected output specific to a test,
        returns a string which includes the SCons wrapping such as
        "Reading ... done", etc.: that is, adds the text that would
        be left out by running SCons in quiet mode;
        Makes a complete message to match against.

        Args:
            read_str: the message for the execution part of the output.
                If non-empty, needs to be newline-terminated.
            read_str: the message for the reading-sconscript part of
                the output. If non-empty, needs to be newline-terminated.
            error: if true, expect a fail message rather than a done message.
            cleaning (int): index into type messages, if 0 selects
                build messages, if 1 selects clean messages.
        """
        cap, lc = [('Build', 'build'),
                   ('Clean', 'clean')][cleaning]
        if error:
            term = f"scons: {lc}ing terminated because of errors.\n"
        else:
            term = f"scons: done {lc}ing targets.\n"

        return "scons: Reading SConscript files ...\n" + \
               read_str + \
               "scons: done reading SConscript files.\n" + \
               f"scons: {cap}ing targets ...\n" + \
               build_str + \
               term

    def run(self, *args, **kw):
        """
        Set up SCONSFLAGS for every command so test scripts don't need
        to worry about unexpected warnings in their output.
        """
        sconsflags = initialize_sconsflags(self.ignore_python_version)
        try:
            super().run(*args, **kw)
        finally:
            restore_sconsflags(sconsflags)

    # Modifying the options should work and ought to be simpler, but this
    # class is used for more than just running 'scons' itself.  If there's
    # an automated  way of determining whether it's running 'scons' or
    # something else, this code should be resurected.
    #        options = kw.get('options')
    #        if options:
    #            options = [options]
    #        else:
    #            options = []
    #        if self.ignore_python_version and deprecated_python_version():
    #            options.append('--warn=no-python-version')
    #        # Provide a way to suppress or provide alternate flags for
    #        # TestSCons purposes by setting TESTSCONS_SCONSFLAGS.
    #        # (The intended use case is to set it to null when running
    #        # timing tests of earlier versions of SCons which don't
    #        # support the --warn=no-visual-c-missing warning.)
    #        visual_c = os.environ.get('TESTSCONS_SCONSFLAGS',
    #                                      '--warn=no-visual-c-missing')
    #        if visual_c:
    #            options.append(visual_c)
    #        kw['options'] = ' '.join(options)
    #        TestCommon.run(self, *args, **kw)

    def up_to_date(self, arguments='.', read_str="", **kw):
        """Asserts that all of the targets listed in arguments is
        up to date, but does not make any assumptions on other targets.
        This function is most useful in conjunction with the -n option.
        """
        s = ""
        for arg in arguments.split():
            s = f"{s}scons: `{arg}' is up to date.\n"
        kw['arguments'] = arguments
        stdout = self.wrap_stdout(read_str=read_str, build_str=s)
        # Append '.*' so that timing output that comes after the
        # up-to-date output is okay.
        kw['stdout'] = f"{re.escape(stdout)}.*"
        kw['match'] = self.match_re_dotall
        self.run(**kw)

    def not_up_to_date(self, arguments='.', read_str="", **kw):
        """Asserts that none of the targets listed in arguments is
        up to date, but does not make any assumptions on other targets.
        This function is most useful in conjunction with the -n option.
        """
        s = ""
        for arg in arguments.split():
            s = f"{s}(?!scons: `{re.escape(arg)}' is up to date.)"
        s = f"({s}[^\n]*\n)*"
        kw['arguments'] = arguments
        stdout = re.escape(self.wrap_stdout(read_str=read_str, build_str='ARGUMENTSGOHERE'))
        kw['stdout'] = stdout.replace('ARGUMENTSGOHERE', s)
        kw['match'] = self.match_re_dotall
        self.run(**kw)

    def option_not_yet_implemented(self, option, arguments=None, **kw):
        """
        Verifies expected behavior for options that are not yet implemented:
        a warning message, and exit status 1.
        """
        msg = f"Warning:  the {option} option is not yet implemented\n"
        kw['stderr'] = msg
        if arguments:
            # If it's a long option and the argument string begins with '=',
            # it's of the form --foo=bar and needs no separating space.
            if option[:2] == '--' and arguments[0] == '=':
                kw['arguments'] = option + arguments
            else:
                kw['arguments'] = f"{option} {arguments}"
        return self.run(**kw)

    def deprecated_wrap(self, msg):
        """
        Calculate the pattern that matches a deprecation warning.
        """
        return f"\nscons: warning: {re_escape(msg)}\n{file_expr}"

    def deprecated_fatal(self, warn, msg):
        """
        Determines if the warning has turned into a fatal error.  If so,
        passes the test, as any remaining runs are now moot.

        This method expects a SConscript to be present that will causes
        the warning.  The method writes a SConstruct that calls the
        SConsscript and looks to see what type of result occurs.

        The pattern that matches the warning is returned.

        TODO: Actually detect that it's now an error.  We don't have any
        cases yet, so there's no way to test it.
        """
        self.write('SConstruct', """if True:
            WARN = ARGUMENTS.get('WARN')
            if WARN: SetOption('warn', WARN)
            SConscript('SConscript')
        """)

        def err_out():
            # TODO calculate stderr for fatal error
            return re_escape('put something here')

        # no option, should get one of nothing, warning, or error
        warning = self.deprecated_wrap(msg)
        self.run(arguments='.', stderr=None)
        stderr = self.stderr()
        if stderr:
            # most common case done first
            if match_re_dotall(stderr, warning):
                # expected output
                pass
            elif match_re_dotall(stderr, err_out()):
                # now a fatal error; skip the rest of the tests
                self.pass_test()
            else:
                # test failed; have to do this by hand...
                print(self.banner('STDOUT '))
                print(self.stdout())
                print(self.diff(warning, stderr, 'STDERR '))
                self.fail_test()

        return warning

    def deprecated_warning(self, warn, msg):
        """
        Verifies the expected behavior occurs for deprecation warnings.
        This method expects a SConscript to be present that will causes
        the warning.  The method writes a SConstruct and exercises various
        combinations of command-line options and SetOption parameters to
        validate that it performs correctly.

        The pattern that matches the warning is returned.
        """
        warning = self.deprecated_fatal(warn, msg)

        def RunPair(option, expected):
            # run the same test with the option on the command line and
            # then with the option passed via SetOption().
            self.run(options=f"--warn={option}",
                     arguments='.',
                     stderr=expected,
                     match=match_re_dotall)
            self.run(options=f"WARN={option}",
                     arguments='.',
                     stderr=expected,
                     match=match_re_dotall)

        # all warnings off, should get no output
        RunPair('no-deprecated', '')

        # warning enabled, should get expected output
        RunPair(warn, warning)

        # warning disabled, should get either nothing or mandatory message
        expect = f"""()|(Can not disable mandataory warning: 'no-{warn}'\n\n{warning})"""
        RunPair(f"no-{warn}", expect)

        return warning

    def diff_substr(self, expect, actual, prelen=20, postlen=40):
        i = 0
        for x, y in zip(expect, actual):
            if x != y:
                return "Actual did not match expect at char %d:\n" \
                       "    Expect:  %s\n" \
                       "    Actual:  %s\n" \
                       % (i, repr(expect[i - prelen:i + postlen]),
                          repr(actual[i - prelen:i + postlen]))
            i = i + 1
        return "Actual matched the expected output???"

    def python_file_line(self, file, line):
        """
        Returns a Python error line for output comparisons.

        The exec of the traceback line gives us the correct format for
        this version of Python.

            File "<string>", line 1, <module>

        We stick the requested file name and line number in the right
        places, abstracting out the version difference.
        """
        # This routine used to use traceback to get the proper format
        # that doesn't work well with py3. And the format of the
        # traceback seems to be stable, so let's just format
        # an appropriate string
        #
        # exec('import traceback; x = traceback.format_stack()[-1]')
        #       import traceback
        #       x = traceback.format_stack()
        #        x = # XXX: .lstrip()
        #       x = x.replace('<string>', file)
        #      x = x.replace('line 1,', 'line %s,' % line)
        #      x="\n".join(x)
        x = f'File "{file}", line {line}, in <module>\n'
        return x

    def normalize_ps(self, s):
        s = re.sub(r'(Creation|Mod)Date: .*',
                   r'\1Date XXXX', s)
        s = re.sub(r'%DVIPSSource:\s+TeX output\s.*',
                   r'%DVIPSSource:   TeX output XXXX', s)
        s = re.sub(r'/(BaseFont|FontName) /[A-Z0-9]{6}',
                   r'/\1 /XXXXXX', s)
        s = re.sub(r'BeginFont: [A-Z0-9]{6}',
                   r'BeginFont: XXXXXX', s)

        return s

    @staticmethod
    def to_bytes_re_sub(pattern, repl, str, count=0, flags=0):
        """
        Wrapper around re.sub to change pattern and repl to bytes to work with
        both python 2 & 3
        """
        pattern = to_bytes(pattern)
        repl = to_bytes(repl)
        return re.sub(pattern, repl, str, count, flags)

    def normalize_pdf(self, s):
        s = self.to_bytes_re_sub(r'/(Creation|Mod)Date \(D:[^)]*\)',
                                 r'/\1Date (D:XXXX)', s)
        s = self.to_bytes_re_sub(r'/ID \[<[0-9a-fA-F]*> <[0-9a-fA-F]*>\]',
                                 r'/ID [<XXXX> <XXXX>]', s)
        s = self.to_bytes_re_sub(r'/(BaseFont|FontName) /[A-Z]{6}',
                                 r'/\1 /XXXXXX', s)
        s = self.to_bytes_re_sub(r'/Length \d+ *\n/Filter /FlateDecode\n',
                                 r'/Length XXXX\n/Filter /FlateDecode\n', s)

        try:
            import zlib
        except ImportError:
            pass
        else:
            begin_marker = to_bytes('/FlateDecode\n>>\nstream\n')
            end_marker = to_bytes('endstream\nendobj')

            encoded = []
            b = s.find(begin_marker, 0)
            while b != -1:
                b = b + len(begin_marker)
                e = s.find(end_marker, b)
                encoded.append((b, e))
                b = s.find(begin_marker, e + len(end_marker))

            x = 0
            r = []
            for b, e in encoded:
                r.append(s[x:b])
                d = zlib.decompress(s[b:e])
                d = self.to_bytes_re_sub(r'%%CreationDate: [^\n]*\n',
                                         r'%%CreationDate: 1970 Jan 01 00:00:00\n', d)
                d = self.to_bytes_re_sub(r'%DVIPSSource:  TeX output \d\d\d\d\.\d\d\.\d\d:\d\d\d\d',
                                         r'%DVIPSSource:  TeX output 1970.01.01:0000', d)
                d = self.to_bytes_re_sub(r'/(BaseFont|FontName) /[A-Z]{6}',
                                         r'/\1 /XXXXXX', d)
                r.append(d)
                x = e
            r.append(s[x:])
            s = to_bytes('').join(r)

        return s

    def paths(self, patterns):
        import glob
        result = []
        for p in patterns:
            result.extend(sorted(glob.glob(p)))
        return result

    def get_sconsignname(self):
        """Get the scons database name used, and return both the prefix and full filename.
        if the user left the options defaulted AND the default algorithm set by
        SCons is md5, then set the database name to be the special default name

        otherwise, if it defaults to something like 'sha1' or the user explicitly
        set 'md5' as the hash format, set the database name to .sconsign_<algorithm>
        eg .sconsign_sha1, etc.

        Returns:
            a pair containing: the current dbname, the dbname.dblite filename
        """
        hash_format = get_hash_format()
        current_hash_algorithm = get_current_hash_algorithm_used()
        if hash_format is None and current_hash_algorithm == 'md5':
            return ".sconsign"
        else:
            database_prefix=f".sconsign_{current_hash_algorithm}"
            return database_prefix


    def unlink_sconsignfile(self, name='.sconsign.dblite'):
        """Delete the sconsign file.

        Note on python it seems to append .p3 to the file name so we take
        care of that.

        TODO the above seems to not be an issue any more.

        Args:
            name: expected name of sconsign file
        """
        if sys.version_info[0] == 3:
            name += '.p3'
        self.unlink(name)

    def java_ENV(self, version=None):
        """ Initialize JAVA SDK environment.

        Initialize with a default external environment that uses a local
        Java SDK in preference to whatever's found in the default PATH.

        Args:
            version: if set, match only that version

        Returns:
            the new env.
        """
        if not self.external:
            try:
                return self._java_env[version]['ENV']
            except AttributeError:
                self._java_env = {}
            except KeyError:
                pass

            import SCons.Environment
            env = SCons.Environment.Environment()
            self._java_env[version] = env

            if version:
                if sys.platform == 'win32':
                    patterns = [
                        f'C:/Program Files*/Java/jdk*{version}*/bin',
                    ]
                else:
                    patterns = [
                        f'/usr/java/jdk{version}*/bin',
                        f'/usr/lib/jvm/*-{version}*/bin',
                        f'/usr/local/j2sdk{version}*/bin',
                    ]
                java_path = self.paths(patterns) + [env['ENV']['PATH']]
            else:
                if sys.platform == 'win32':
                    patterns = [
                        'C:/Program Files*/Java/jdk*/bin',
                    ]
                else:
                    patterns = [
                        '/usr/java/latest/bin',
                        '/usr/lib/jvm/*/bin',
                        '/usr/local/j2sdk*/bin',
                    ]
                java_path = self.paths(patterns) + [env['ENV']['PATH']]

            env['ENV']['PATH'] = os.pathsep.join(java_path)
            return env['ENV']

        return None

    def java_where_includes(self, version=None):
        """ Find include path needed for compiling java jni code.

        Args:
            version: if set, match only that version

        Returns:
            path to java headers or None
        """
        import sys

        result = []
        if sys.platform[:6] == 'darwin':
            java_home = self.java_where_java_home(version)
            jni_path = os.path.join(java_home, 'include', 'jni.h')
            if os.path.exists(jni_path):
                result.append(os.path.dirname(jni_path))

        if not version:
            version = ''
            jni_dirs = ['/System/Library/Frameworks/JavaVM.framework/Headers/jni.h',
                        '/usr/lib/jvm/default-java/include/jni.h',
                        '/usr/lib/jvm/java-*-oracle/include/jni.h']
        else:
            jni_dirs = [f'/System/Library/Frameworks/JavaVM.framework/Versions/{version}*/Headers/jni.h']
        jni_dirs.extend([f'/usr/lib/jvm/java-*-sun-{version}*/include/jni.h',
                         f'/usr/lib/jvm/java-{version}*-openjdk*/include/jni.h',
                         f'/usr/java/jdk{version}*/include/jni.h'])
        dirs = self.paths(jni_dirs)
        if not dirs:
            return None
        d = os.path.dirname(self.paths(jni_dirs)[0])
        result.append(d)

        if sys.platform == 'win32':
            result.append(os.path.join(d, 'win32'))
        elif sys.platform.startswith('linux'):
            result.append(os.path.join(d, 'linux'))
        return result

    def java_where_java_home(self, version=None) -> str:
        """ Find path to what would be JAVA_HOME.

        SCons does not read JAVA_HOME from the environment, so deduce it.

        Args:
            version: if set, match only that version

        Returns:
            path where JDK components live
            Bails out of the entire test (skip) if not found.
        """
        if sys.platform[:6] == 'darwin':
            # osx 10.11+
            home_tool = '/usr/libexec/java_home'
            java_home = ''
            if os.path.exists(home_tool):
                cp = sp.run(home_tool, stdout=sp.PIPE, stderr=sp.STDOUT)
                if cp.returncode == 0:
                    java_home = cp.stdout.decode().strip()

            if version is None:
                if java_home:
                    return java_home
                for home in [
                    '/System/Library/Frameworks/JavaVM.framework/Home',
                    # osx 10.10
                    '/System/Library/Frameworks/JavaVM.framework/Versions/Current/Home'
                ]:
                    if os.path.exists(home):
                        return home
            else:
                if java_home.find(f'jdk{version}') != -1:
                    return java_home
                for home in [
                    f'/System/Library/Frameworks/JavaVM.framework/Versions/{version}/Home',
                    # osx 10.10
                    '/System/Library/Frameworks/JavaVM.framework/Versions/Current/'
                ]:
                    if os.path.exists(home):
                        return home
            # if we fell through, make sure flagged as not found
            home = ''
        else:
            jar = self.java_where_jar(version)
            home = os.path.normpath(f'{jar}/..')

        if home and os.path.isdir(home):
            return home

        self.skip_test(
            "Could not run Java: unable to detect valid JAVA_HOME, skipping test.\n",
            from_fw=True,
        )

    def java_mac_check(self, where_java_bin, java_bin_name) -> None:
        """Extra check for Java on MacOS.

        MacOS has a place holder java/javac, which fails with a detectable
        error if Java is not actually installed, and works normally if it is.
        Note msg has changed over time.

        Bails out of the entire test (skip) if not found.
        """
        cp = sp.run([where_java_bin, "-version"], stdout=sp.PIPE, stderr=sp.STDOUT)
        if (
            b"No Java runtime" in cp.stdout
            or b"Unable to locate a Java Runtime" in cp.stdout
        ):
            self.skip_test(
                f"Could not find Java {java_bin_name}, skipping test.\n",
                from_fw=True,
            )

    def java_where_jar(self, version=None) -> str:
        """ Find java archiver jar.

        Args:
            version: if set, match only that version

        Returns:
            path to jar
        """
        ENV = self.java_ENV(version)
        if self.detect_tool('jar', ENV=ENV):
            where_jar = self.detect('JAR', 'jar', ENV=ENV)
        else:
            where_jar = self.where_is('jar', ENV['PATH'])
        if not where_jar:
            self.skip_test("Could not find Java jar, skipping test(s).\n", from_fw=True)
        elif sys.platform == "darwin":
            self.java_mac_check(where_jar, 'jar')

        return where_jar

    def java_where_java(self, version=None) -> str:
        """ Find java executable.

        Args:
            version: if set, match only that version

        Returns:
            path to the java rutime
        """
        ENV = self.java_ENV(version)
        where_java = self.where_is('java', ENV['PATH'])

        if not where_java:
            self.skip_test("Could not find Java java, skipping test(s).\n", from_fw=True)
        elif sys.platform == "darwin":
            self.java_mac_check(where_java, 'java')

        return where_java

    def java_where_javac(self, version=None) -> str:
        """ Find java compiler.

        Args:
            version: if set, match only that version

        Returns:
            path to javac
        """
        ENV = self.java_ENV(version)
        if self.detect_tool('javac'):
            where_javac = self.detect('JAVAC', 'javac', ENV=ENV)
        else:
            where_javac = self.where_is('javac', ENV['PATH'])
        if not where_javac:
            self.skip_test("Could not find Java javac, skipping test(s).\n", from_fw=True)
        elif sys.platform == "darwin":
            self.java_mac_check(where_javac, 'javac')

        self.run(program=where_javac,
                 arguments='-version',
                 stderr=None,
                 status=None)
        # Note recent versions output version info to stdout instead of stderr
        if version:
            verf = f'javac {version}'
            if self.stderr().find(verf) == -1 and self.stdout().find(verf) == -1:
                fmt = "Could not find javac for Java version %s, skipping test(s).\n"
                self.skip_test(fmt % version, from_fw=True)
        else:
            version_re = r'javac (\d*\.*\d)'
            m = re.search(version_re, self.stderr())
            if not m:
                m = re.search(version_re, self.stdout())

            if m:
                version = m.group(1)
                self.javac_is_gcj = False
            elif self.stderr().find('gcj') != -1:
                version = '1.2'
                self.javac_is_gcj = True
            else:
                version = None
                self.javac_is_gcj = False
        return where_javac, version

    def java_where_javah(self, version=None) -> str:
        """ Find java header generation tool.

        TODO issue #3347 since JDK10, there is no separate javah command,
        'javac -h' is used. We should not return a javah from a different
        installed JDK - how to detect and what to return in this case?

        Args:
            version: if set, match only that version

        Returns:
            path to javah
        """
        ENV = self.java_ENV(version)
        if self.detect_tool('javah'):
            where_javah = self.detect('JAVAH', 'javah', ENV=ENV)
        else:
            where_javah = self.where_is('javah', ENV['PATH'])
        if not where_javah:
            self.skip_test("Could not find Java javah, skipping test(s).\n", from_fw=True)
        return where_javah

    def java_where_rmic(self, version=None) -> str:
        """ Find java rmic tool.

        Args:
            version: if set, match only that version

        Returns:
            path to rmic
        """
        ENV = self.java_ENV(version)
        if self.detect_tool('rmic'):
            where_rmic = self.detect('RMIC', 'rmic', ENV=ENV)
        else:
            where_rmic = self.where_is('rmic', ENV['PATH'])
        if not where_rmic:
            self.skip_test("Could not find Java rmic, skipping non-simulated test(s).\n", from_fw=True)
        return where_rmic

    def java_get_class_files(self, dir):
        result = []
        for dirpath, dirnames, filenames in os.walk(dir):
            for fname in filenames:
                if fname.endswith('.class'):
                    result.append(os.path.join(dirpath, fname))
        return sorted(result)

    def Qt_dummy_installation(self, dir='qt'):
        # create a dummy qt installation

        self.subdir(dir, [dir, 'bin'], [dir, 'include'], [dir, 'lib'])

        self.write([dir, 'bin', 'mymoc.py'], """\
import getopt
import sys
import re
# -w and -z are fake options used in test/QT/QTFLAGS.py
cmd_opts, args = getopt.getopt(sys.argv[1:], 'io:wz', [])
impl = 0
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': outfile = arg
    elif opt == '-i': impl = 1
    else: opt_string = opt_string + ' ' + opt

with open(outfile, 'w') as ofp:
    ofp.write("/* mymoc.py%s */\\n" % opt_string)
    for a in args:
        with open(a, 'r') as ifp:
            contents = ifp.read()
        a = a.replace('\\\\', '\\\\\\\\')
        subst = r'{ my_qt_symbol( "' + a + '\\\\n" ); }'
        if impl:
            contents = re.sub(r'#include.*', '', contents)
        ofp.write(contents.replace('Q_OBJECT', subst))
sys.exit(0)
""")

        self.write([dir, 'bin', 'myuic.py'], """\
import os.path
import re
import sys
output_arg = 0
impl_arg = 0
impl = None
source = None
opt_string = ''
for arg in sys.argv[1:]:
    if output_arg:
        outfile = arg
        output_arg = 0
    elif impl_arg:
        impl = arg
        impl_arg = 0
    elif arg == "-o":
        output_arg = 1
    elif arg == "-impl":
        impl_arg = 1
    elif arg[0:1] == "-":
        opt_string = opt_string + ' ' + arg
    else:
        if source:
            sys.exit(1)
        source = sourceFile = arg

with open(outfile, 'w') as ofp, open(source, 'r') as ifp:
    ofp.write("/* myuic.py%s */\\n" % opt_string)
    if impl:
        ofp.write('#include "' + impl + '"\\n')
        includes = re.findall('<include.*?>(.*?)</include>', ifp.read())
        for incFile in includes:
            # this is valid for ui.h files, at least
            if os.path.exists(incFile):
                ofp.write('#include "' + incFile + '"\\n')
    else:
        ofp.write('#include "my_qobject.h"\\n' + ifp.read() + " Q_OBJECT \\n")
sys.exit(0)
""")

        self.write([dir, 'include', 'my_qobject.h'], r"""
#define Q_OBJECT ;
void my_qt_symbol(const char *arg);
""")

        self.write([dir, 'lib', 'my_qobject.cpp'], r"""
#include "../include/my_qobject.h"
#include <stdio.h>
void my_qt_symbol(const char *arg) {
  fputs(arg, stdout);
}
""")

        self.write([dir, 'lib', 'SConstruct'], r"""
import sys
DefaultEnvironment(tools=[])  # test speedup
env = Environment()
if sys.platform == 'win32':
    env.StaticLibrary('myqt', 'my_qobject.cpp')
else:
    env.SharedLibrary('myqt', 'my_qobject.cpp')
""")

        self.run(chdir=self.workpath(dir, 'lib'),
                 arguments='.',
                 stderr=noisy_ar,
                 match=self.match_re_dotall)

        self.QT = self.workpath(dir)
        self.QT_LIB = 'myqt'
        self.QT_MOC = f"{_python_} {self.workpath(dir, 'bin', 'mymoc.py')}"
        self.QT_UIC = f"{_python_} {self.workpath(dir, 'bin', 'myuic.py')}"
        self.QT_LIB_DIR = self.workpath(dir, 'lib')

    def Qt_create_SConstruct(self, place, qt_tool='qt3'):
        if isinstance(place, list):
            place = test.workpath(*place)

        var_prefix=qt_tool.upper()
        self.write(place, f"""\
if ARGUMENTS.get('noqtdir', 0):
    {var_prefix}DIR = None
else:
    {var_prefix}DIR = r'{self.QT}'
DefaultEnvironment(tools=[])  # test speedup
env = Environment(
    {var_prefix}DIR={var_prefix}DIR, {var_prefix}_LIB=r'{self.QT_LIB}', {var_prefix}_MOC=r'{self.QT_MOC}',
    {var_prefix}_UIC=r'{self.QT_UIC}', tools=['default', '{qt_tool}']
)
dup = 1
if ARGUMENTS.get('variant_dir', 0):
    if ARGUMENTS.get('chdir', 0):
        SConscriptChdir(1)
    else:
        SConscriptChdir(0)
    dup = int(ARGUMENTS.get('dup', 1))
    if dup == 0:
        builddir = 'build_dup0'
        env['QT_DEBUG'] = 1
    else:
        builddir = 'build'
    VariantDir(builddir, '.', duplicate=dup)
    print(builddir, dup)
    sconscript = Dir(builddir).File('SConscript')
else:
    sconscript = File('SConscript')
Export("env dup")
SConscript(sconscript)
""")

    NCR = 0  # non-cached rebuild
    CR = 1  # cached rebuild (up to date)
    NCF = 2  # non-cached build failure
    CF = 3  # cached build failure

    if sys.platform == 'win32':
        Configure_lib = 'msvcrt'
    else:
        Configure_lib = 'm'

    # to use cygwin compilers on cmd.exe -> uncomment following line
    # Configure_lib = 'm'

    def coverage_run(self):
        """ Check if the the tests are being run under coverage.
        """
        return 'COVERAGE_PROCESS_START' in os.environ or 'COVERAGE_FILE' in os.environ

    def skip_if_not_msvc(self, check_platform=True):
        """ Skip test if MSVC is not available.

        Check whether we are on a Windows platform and skip the test if
        not. This check can be omitted by setting check_platform to False.

        Then, for a win32 platform, additionally check whether we have
        an MSVC toolchain installed in the system, and skip the test if
        none can be found (e.g. MinGW is the only compiler available).
        """
        if check_platform:
            if sys.platform != 'win32':
                msg = f"Skipping Visual C/C++ test on non-Windows platform '{sys.platform}'\n"
                self.skip_test(msg, from_fw=True)
                return

        try:
            import SCons.Tool.MSCommon as msc
            if not msc.msvc_exists():
                msg = "No MSVC toolchain found...skipping test\n"
                self.skip_test(msg, from_fw=True)
        except Exception:
            pass

    def checkConfigureLogAndStdout(self, checks,
                                   logfile='config.log',
                                   sconf_dir='.sconf_temp',
                                   sconstruct="SConstruct",
                                   doCheckLog=True, doCheckStdout=True):
        """ Verify expected output from Configure.

        Used to verify the expected output from using Configure()
        via the contents of one or both of stdout or config.log file.
        If the algorithm does not succeed, the test is marked a fail
        and this function does not return.

        TODO: Perhaps a better API makes sense?

        Args:
            checks: list of ConfigCheckInfo tuples which specify
            logfile: Name of the config log
            sconf_dir: Name of the sconf dir
            sconstruct: SConstruct file name
            doCheckLog: check specified log file, defaults to true
            doCheckStdout: Check stdout, defaults to true
        """

        try:
            ls = '\n'
            nols = '([^\n])'
            lastEnd = 0

            # Read the whole logfile
            logfile = self.read(self.workpath(logfile), mode='r')

            # Some debug code to keep around..
            # sys.stderr.write("LOGFILE[%s]:%s"%(type(logfile),logfile))

            if (doCheckLog and
                    logfile.find("scons: warning: The stored build information has an unexpected class.") >= 0):
                self.fail_test()

            log = r'file\ \S*%s\,line \d+:' % re.escape(sconstruct) + ls
            if doCheckLog:
                lastEnd = match_part_of_configlog(log, logfile, lastEnd)

            log = f"\t{re.escape(f'Configure(confdir = {sconf_dir})')}" + ls
            if doCheckLog:
                lastEnd = match_part_of_configlog(log, logfile, lastEnd)

            rdstr = ""

            for check_info in checks:
                log = re.escape(f"scons: Configure: {check_info.check_string}") + ls

                if doCheckLog:
                    lastEnd = match_part_of_configlog(log, logfile, lastEnd)

                log = ""
                result_cached = 1
                for bld_desc in check_info.cached:  # each TryXXX
                    for ext, flag in bld_desc:  # each file in TryBuild
                        conf_filename = re.escape(check_info.temp_filename%ext)

                        if flag == self.NCR:
                            # NCR = Non Cached Rebuild
                            # rebuild will pass
                            if ext in ['.c', '.cpp']:
                                log = log + conf_filename + re.escape(" <-") + ls
                                log = f"{log}(  \\|{nols}*{ls})+?"
                            else:
                                log = f"{log}({nols}*{ls})*?"
                            result_cached = 0
                        if flag == self.CR:
                            # CR = cached rebuild (up to date)s
                            # up to date
                            log = log + \
                                  re.escape("scons: Configure: \"") + \
                                  conf_filename + \
                                  re.escape("\" is up to date.") + ls
                            log = log + re.escape("scons: Configure: The original builder "
                                                  "output was:") + ls
                            log = f"{log}(  \\|.*{ls})+"
                        if flag == self.NCF:
                            # non-cached rebuild failure
                            log = f"{log}({nols}*{ls})*?"
                            result_cached = 0
                        if flag == self.CF:
                            # cached rebuild failure
                            log = log + \
                                  re.escape("scons: Configure: Building \"") + \
                                  conf_filename + \
                                  re.escape("\" failed in a previous run and all its sources are up to date.") + ls
                            log = log + re.escape("scons: Configure: The original builder output was:") + ls
                            log = f"{log}(  \\|.*{ls})+"
                if result_cached:
                    result = f"(cached) {check_info.result}"
                else:
                    result = check_info.result
                rdstr = f"{rdstr + re.escape(check_info.check_string) + re.escape(result)}\n"

                log = log + re.escape(f"scons: Configure: {result}") + ls + ls

                if doCheckLog:
                    lastEnd = match_part_of_configlog(log, logfile, lastEnd)

                log = ""
            if doCheckLog:
                lastEnd = match_part_of_configlog(ls, logfile, lastEnd)

            if doCheckLog and lastEnd != len(logfile):
                raise NoMatch(lastEnd)

        except NoMatch as m:
            print("Cannot match log file against log regexp.")
            print("log file: ")
            print("------------------------------------------------------")
            print(logfile[m.pos:])
            print("------------------------------------------------------")
            print("log regexp: ")
            print("------------------------------------------------------")
            print(log)
            print("------------------------------------------------------")
            self.fail_test()

        if doCheckStdout:
            exp_stdout = self.wrap_stdout(".*", rdstr)
            if not self.match_re_dotall(self.stdout(), exp_stdout):
                print("Unexpected stdout: ")
                print("-----------------------------------------------------")
                print(repr(self.stdout()))
                print("-----------------------------------------------------")
                print(repr(exp_stdout))
                print("-----------------------------------------------------")
                self.fail_test()



    def checkLogAndStdout(self, checks, results, cached,
                          logfile, sconf_dir, sconstruct,
                          doCheckLog=True, doCheckStdout=True):
        """ Verify expected output from Configure.

        Used to verify the expected output from using Configure()
        via the contents of one or both of stdout or config.log file.
        The checks, results, cached parameters all are zipped together
        for use in comparing results. If the algorithm does not
        succeed, the test is marked a fail and this function does not return.

        TODO: Perhaps a better API makes sense?

        Args:
            checks: The Configure checks being run
            results: The expected results for each check
            cached: If the corresponding check is expected to be cached
            logfile: Name of the config log
            sconf_dir: Name of the sconf dir
            sconstruct: SConstruct file name
            doCheckLog: check specified log file, defaults to true
            doCheckStdout: Check stdout, defaults to true
        """
        try:

            ls = '\n'
            nols = '([^\n])'
            lastEnd = 0

            # Read the whole logfile
            logfile = self.read(self.workpath(logfile), mode='r')

            # Some debug code to keep around..
            # sys.stderr.write("LOGFILE[%s]:%s"%(type(logfile),logfile))

            if (doCheckLog and
                    logfile.find("scons: warning: The stored build information has an unexpected class.") >= 0):
                self.fail_test()

            sconf_dir = sconf_dir
            sconstruct = sconstruct

            log = r'file\ \S*%s\,line \d+:' % re.escape(sconstruct) + ls
            if doCheckLog:
                lastEnd = match_part_of_configlog(log, logfile, lastEnd)

            log = f"\t{re.escape(f'Configure(confdir = {sconf_dir})')}" + ls
            if doCheckLog:
                lastEnd = match_part_of_configlog(log, logfile, lastEnd)

            rdstr = ""

            cnt = 0
            for check, result, cache_desc in zip(checks, results, cached):
                log = re.escape(f"scons: Configure: {check}") + ls

                if doCheckLog:
                    lastEnd = match_part_of_configlog(log, logfile, lastEnd)

                log = ""
                result_cached = 1
                for bld_desc in cache_desc:  # each TryXXX
                    for ext, flag in bld_desc:  # each file in TryBuild
                        if ext in ['.c', '.cpp']:
                            conf_filename = re.escape(os.path.join(sconf_dir, "conftest")) +\
                                            r'_[a-z0-9]{32,64}_\d+%s' % re.escape(ext)
                        elif ext == '':
                            conf_filename = re.escape(os.path.join(sconf_dir, "conftest")) +\
                                            r'_[a-z0-9]{32,64}(_\d+_[a-z0-9]{32,64})?'

                        else:
                            # We allow the second hash group to be optional because
                            # TryLink() will create a c file, then compile to obj, then link that
                            # The intermediate object file will not get the action hash
                            # But TryCompile()'s where the product is the .o will get the
                            # action hash. Rather than add a ton of complications to this logic
                            # this shortcut should be sufficient.
                            # TODO: perhaps revisit and/or fix file naming for intermediate files in
                            #  Configure context logic
                            conf_filename = re.escape(os.path.join(sconf_dir, "conftest")) +\
                                            r'_[a-z0-9]{32,64}_\d+(_[a-z0-9]{32,64})?%s' % re.escape(ext)

                        if flag == self.NCR:
                            # NCR = Non Cached Rebuild
                            # rebuild will pass
                            if ext in ['.c', '.cpp']:
                                log = log + conf_filename + re.escape(" <-") + ls
                                log = f"{log}(  \\|{nols}*{ls})+?"
                            else:
                                log = f"{log}({nols}*{ls})*?"
                            result_cached = 0
                        if flag == self.CR:
                            # CR = cached rebuild (up to date)s
                            # up to date
                            log = log + \
                                  re.escape("scons: Configure: \"") + \
                                  conf_filename + \
                                  re.escape("\" is up to date.") + ls
                            log = log + re.escape("scons: Configure: The original builder "
                                                  "output was:") + ls
                            log = f"{log}(  \\|.*{ls})+"
                        if flag == self.NCF:
                            # non-cached rebuild failure
                            log = f"{log}({nols}*{ls})*?"
                            result_cached = 0
                        if flag == self.CF:
                            # cached rebuild failure
                            log = log + \
                                  re.escape("scons: Configure: Building \"") + \
                                  conf_filename + \
                                  re.escape("\" failed in a previous run and all its sources are up to date.") + ls
                            log = log + re.escape("scons: Configure: The original builder output was:") + ls
                            log = f"{log}(  \\|.*{ls})+"
                    # cnt = cnt + 1
                if result_cached:
                    result = f"(cached) {result}"

                rdstr = f"{rdstr + re.escape(check) + re.escape(result)}\n"

                log = log + re.escape(f"scons: Configure: {result}") + ls + ls

                if doCheckLog:
                    lastEnd = match_part_of_configlog(log, logfile, lastEnd)

                log = ""
            if doCheckLog:
                lastEnd = match_part_of_configlog(ls, logfile, lastEnd)

            if doCheckLog and lastEnd != len(logfile):
                raise NoMatch(lastEnd)

        except NoMatch as m:
            print("Cannot match log file against log regexp.")
            print("log file: ")
            print("------------------------------------------------------")
            print(logfile[m.pos:])
            print("------------------------------------------------------")
            print("log regexp: ")
            print("------------------------------------------------------")
            print(log)
            print("------------------------------------------------------")
            self.fail_test()

        if doCheckStdout:
            exp_stdout = self.wrap_stdout(".*", rdstr)
            if not self.match_re_dotall(self.stdout(), exp_stdout):
                print("Unexpected stdout: ")
                print("----Actual-------------------------------------------")
                print(repr(self.stdout()))
                print("----Expected-----------------------------------------")
                print(repr(exp_stdout))
                print("-----------------------------------------------------")
                self.fail_test()

    def get_python_version(self) -> str:
        """ Returns the Python version.

        Convenience function so everyone doesn't have to
        hand-code slicing the right number of characters
        """
        # see also sys.prefix documentation
        return python_minor_version_string()

    def get_platform_python_info(self, python_h_required=False):
        """Return information about Python.

        Returns a path to a Python executable suitable for testing on
        this platform and its associated include path, library path and
        library name.

        If the Python executable or Python header (if required)
        is not found, the test is skipped.

        Returns:
            tuple: path to python, include path, library path, library name
        """
        python = os.environ.get('python_executable', self.where_is('python'))
        if not python:
            self.skip_test('Can not find installed "python", skipping test.\n', from_fw=True)

        # construct a program to run in the intended environment
        # in order to fetch the characteristics of that Python.
        # Windows Python doesn't store all the info in config vars.
        if sys.platform == 'win32':
            self.run(program=python, stdin="""\
import sysconfig, sys, os.path
py_ver = 'python%d%d' % sys.version_info[:2]
try:
    exec_prefix = sysconfig.get_config_var("exec_prefix")
    include = sysconfig.get_config_var("INCLUDEPY")
    print(include)
    lib_path = os.path.join(exec_prefix, 'libs')
    if not os.path.exists(lib_path):
        # check for virtualenv path.
        # this might not build anything different than first try.
        def venv_path():
            if hasattr(sys, 'real_prefix'):
                return sys.real_prefix
            if hasattr(sys, 'base_prefix'):
                return sys.base_prefix
        lib_path = os.path.join(venv_path(), 'libs')
    if not os.path.exists(lib_path):
        # not clear this is useful: 'lib' does not contain linkable libs
        lib_path = os.path.join(exec_prefix, 'lib')
    print(lib_path)
except:
    include = os.path.join(sys.prefix, 'include', py_ver)
    print(include)
    lib_path = os.path.join(sys.prefix, 'lib', py_ver, 'config')
    print(lib_path)
print(py_ver)
Python_h = os.path.join(include, "Python.h")
if os.path.exists(Python_h):
    print(Python_h)
else:
    print("False")
""")
        else:
            self.run(program=python, stdin="""\
import sys, sysconfig, os.path
include = sysconfig.get_config_var("INCLUDEPY")
print(include)
print(sysconfig.get_config_var("LIBDIR"))
py_library_ver = sysconfig.get_config_var("LDVERSION")
if not py_library_ver:
    py_library_ver = '%d.%d' % sys.version_info[:2]
print("python"+py_library_ver)
Python_h = os.path.join(include, "Python.h")
if os.path.exists(Python_h):
    print(Python_h)
else:
    print("False")
""")
        incpath, libpath, libname, python_h = self.stdout().strip().split('\n')
        if python_h == "False" and python_h_required:
            self.skip_test('Can not find required "Python.h", skipping test.\n', from_fw=True)

        return (python, incpath, libpath, libname)

    def start(self, *args, **kw):
        """
        Starts SCons in the test environment.

        This method exists to tell Test{Cmd,Common} that we're going to
        use standard input without forcing every .start() call in the
        individual tests to do so explicitly.
        """
        if 'stdin' not in kw:
            kw['stdin'] = True
        sconsflags = initialize_sconsflags(self.ignore_python_version)
        try:
            p = super().start(*args, **kw)
        finally:
            restore_sconsflags(sconsflags)
        return p

    def wait_for(self, fname, timeout=20.0, popen=None):
        """
        Waits for the specified file name to exist.
        """
        waited = 0.0
        while not os.path.exists(fname):
            if timeout and waited >= timeout:
                sys.stderr.write(f'timed out waiting for {fname} to exist\n')
                if popen:
                    popen.stdin.close()
                    popen.stdin = None
                    self.status = 1
                    self.finish(popen)
                stdout = self.stdout()
                if stdout:
                    sys.stdout.write(f"{self.banner('STDOUT ')}\n")
                    sys.stdout.write(stdout)
                stderr = self.stderr()
                if stderr:
                    sys.stderr.write(f"{self.banner('STDERR ')}\n")
                    sys.stderr.write(stderr)
                self.fail_test()
            time.sleep(1.0)
            waited = waited + 1.0

    def get_alt_cpp_suffix(self):
        """Return alternate C++ file suffix.

        Many CXX tests have this same logic.
        They all needed to determine if the current os supports
        files with .C and .c as different files or not
        in which case they are instructed to use .cpp instead of .C
        """
        if not case_sensitive_suffixes('.c', '.C'):
            alt_cpp_suffix = '.cpp'
        else:
            alt_cpp_suffix = '.C'
        return alt_cpp_suffix

    def platform_has_symlink(self) -> bool:
        """Retun an indication of whether symlink tests should be run.

        Despite the name, we really mean "are they reliably usable"
        rather than "do they exist" - basically the Windows case.
        """
        if not hasattr(os, 'symlink') or sys.platform == 'win32':
            return False
        else:
            return True

    def zipfile_contains(self, zipfilename, names):
        """Returns True if zipfilename contains all the names, False otherwise."""
        with zipfile.ZipFile(zipfilename, 'r') as zf:
            return all(elem in zf.namelist() for elem in names)

    def zipfile_files(self, fname):
        """Returns all the filenames in zip file fname."""
        with zipfile.ZipFile(fname, 'r') as zf:
            return zf.namelist()


class Stat:
    def __init__(self, name, units, expression, convert=None):
        if convert is None:
            convert = lambda x: x
        self.name = name
        self.units = units
        self.expression = re.compile(expression)
        self.convert = convert


StatList = [
    Stat('memory-initial', 'kbytes',
         r'Memory before reading SConscript files:\s+(\d+)',
         convert=lambda s: int(s) // 1024),
    Stat('memory-prebuild', 'kbytes',
         r'Memory before building targets:\s+(\d+)',
         convert=lambda s: int(s) // 1024),
    Stat('memory-final', 'kbytes',
         r'Memory after building targets:\s+(\d+)',
         convert=lambda s: int(s) // 1024),

    Stat('time-sconscript', 'seconds',
         r'Total SConscript file execution time:\s+([\d.]+) seconds'),
    Stat('time-scons', 'seconds',
         r'Total SCons execution time:\s+([\d.]+) seconds'),
    Stat('time-commands', 'seconds',
         r'Total command execution time:\s+([\d.]+) seconds'),
    Stat('time-total', 'seconds',
         r'Total build time:\s+([\d.]+) seconds'),
]


class TimeSCons(TestSCons):
    """Class for timing SCons."""

    def __init__(self, *args, **kw):
        """
        In addition to normal TestSCons.TestSCons intialization,
        this enables verbose mode (which causes the command lines to
        be displayed in the output) and copies the contents of the
        directory containing the executing script to the temporary
        working directory.
        """
        self.variables = kw.get('variables')
        default_calibrate_variables = []
        if self.variables is not None:
            for variable, value in self.variables.items():
                value = os.environ.get(variable, value)
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                    else:
                        default_calibrate_variables.append(variable)
                else:
                    default_calibrate_variables.append(variable)
                self.variables[variable] = value
            del kw['variables']
        calibrate_keyword_arg = kw.get('calibrate')
        if calibrate_keyword_arg is None:
            self.calibrate_variables = default_calibrate_variables
        else:
            self.calibrate_variables = calibrate_keyword_arg
            del kw['calibrate']

        self.calibrate = os.environ.get('TIMESCONS_CALIBRATE', '0') != '0'

        if 'verbose' not in kw and not self.calibrate:
            kw['verbose'] = True

        super().__init__(*args, **kw)

        # TODO(sgk):    better way to get the script dir than sys.argv[0]
        self.test_dir = os.path.dirname(sys.argv[0])
        test_name = os.path.basename(self.test_dir)

        if not os.path.isabs(self.test_dir):
            self.test_dir = os.path.join(self.orig_cwd, self.test_dir)
        self.copy_timing_configuration(self.test_dir, self.workpath())

    def main(self, *args, **kw):
        """
        The main entry point for standard execution of timings.

        This method run SCons three times:

          Once with the --help option, to have it exit after just reading
          the configuration.

          Once as a full build of all targets.

          Once again as a (presumably) null or up-to-date build of
          all targets.

        The elapsed time to execute each build is printed after
        it has finished.
        """
        if 'options' not in kw and self.variables:
            options = []
            for variable, value in self.variables.items():
                options.append(f'{variable}={value}')
            kw['options'] = ' '.join(options)
        if self.calibrate:
            self.calibration(*args, **kw)
        else:
            self.uptime()
            self.startup(*args, **kw)
            self.full(*args, **kw)
            self.null(*args, **kw)

    def trace(self, graph, name, value, units, sort=None):
        fmt = "TRACE: graph=%s name=%s value=%s units=%s"
        line = fmt % (graph, name, value, units)
        if sort is not None:
            line = f"{line} sort={sort}"
        line = f"{line}\n"
        sys.stdout.write(line)
        sys.stdout.flush()

    def report_traces(self, trace, stats):
        self.trace('TimeSCons-elapsed',
                   trace,
                   self.elapsed_time(),
                   "seconds",
                   sort=0)
        for name, args in stats.items():
            self.trace(name, trace, **args)

    def uptime(self):
        try:
            fp = open('/proc/loadavg')
        except EnvironmentError:
            pass
        else:
            avg1, avg5, avg15 = fp.readline().split(" ")[:3]
            fp.close()
            self.trace('load-average', 'average1', avg1, 'processes')
            self.trace('load-average', 'average5', avg5, 'processes')
            self.trace('load-average', 'average15', avg15, 'processes')

    def collect_stats(self, input):
        result = {}
        for stat in StatList:
            m = stat.expression.search(input)
            if m:
                value = stat.convert(m.group(1))
                # The dict keys match the keyword= arguments
                # of the trace() method above so they can be
                # applied directly to that call.
                result[stat.name] = {'value': value, 'units': stat.units}
        return result

    def add_timing_options(self, kw, additional=None):
        """
        Add the necessary timings options to the kw['options'] value.
        """
        options = kw.get('options', '')
        if additional is not None:
            options += additional
        kw['options'] = f"{options} --debug=memory,time"

    def startup(self, *args, **kw):
        """
        Runs scons with the --help option.

        This serves as a way to isolate just the amount of startup time
        spent reading up the configuration, since --help exits before any
        "real work" is done.
        """
        self.add_timing_options(kw, ' --help')
        # Ignore the exit status.  If the --help run dies, we just
        # won't report any statistics for it, but we can still execute
        # the full and null builds.
        kw['status'] = None
        self.run(*args, **kw)
        sys.stdout.write(self.stdout())
        stats = self.collect_stats(self.stdout())
        # Delete the time-commands, since no commands are ever
        # executed on the help run and it is (or should be) always 0.0.
        del stats['time-commands']
        self.report_traces('startup', stats)

    def full(self, *args, **kw):
        """
        Runs a full build of SCons.
        """
        self.add_timing_options(kw)
        self.run(*args, **kw)
        sys.stdout.write(self.stdout())
        stats = self.collect_stats(self.stdout())
        self.report_traces('full', stats)
        self.trace('full-memory', 'initial', **stats['memory-initial'])
        self.trace('full-memory', 'prebuild', **stats['memory-prebuild'])
        self.trace('full-memory', 'final', **stats['memory-final'])

    def calibration(self, *args, **kw):
        """
        Runs a full build of SCons, but only reports calibration
        information (the variable(s) that were set for this configuration,
        and the elapsed time to run.
        """
        self.add_timing_options(kw)
        self.run(*args, **kw)
        for variable in self.calibrate_variables:
            value = self.variables[variable]
            sys.stdout.write(f'VARIABLE: {variable}={value}\n')
        sys.stdout.write(f'ELAPSED: {self.elapsed_time()}\n')

    def null(self, *args, **kw):
        """
        Runs an up-to-date null build of SCons.
        """
        # TODO(sgk):  allow the caller to specify the target (argument)
        # that must be up-to-date.
        self.add_timing_options(kw)

        # Build up regex for
        # SConscript:/private/var/folders/ng/48pttrpj239fw5rmm3x65pxr0000gn/T/testcmd.12081.pk1bv5i5/SConstruct  took 533.646 ms
        read_str = 'SConscript:.*\n'
        self.up_to_date(arguments='.', read_str=read_str, **kw)
        sys.stdout.write(self.stdout())
        stats = self.collect_stats(self.stdout())
        # time-commands should always be 0.0 on a null build, because
        # no commands should be executed.  Remove it from the stats
        # so we don't trace it, but only if it *is* 0 so that we'll
        # get some indication if a supposedly-null build actually does
        # build something.
        if float(stats['time-commands']['value']) == 0.0:
            del stats['time-commands']
        self.report_traces('null', stats)
        self.trace('null-memory', 'initial', **stats['memory-initial'])
        self.trace('null-memory', 'prebuild', **stats['memory-prebuild'])
        self.trace('null-memory', 'final', **stats['memory-final'])

    def elapsed_time(self):
        """
        Returns the elapsed time of the most recent command execution.
        """
        return self.endTime - self.startTime

    def run(self, *args, **kw):
        """
        Runs a single build command, capturing output in the specified file.

        Because this class is about timing SCons, we record the start
        and end times of the elapsed execution, and also add the
        --debug=memory and --debug=time options to have SCons report
        its own memory and timing statistics.
        """
        self.startTime = time.perf_counter()
        try:
            result = TestSCons.run(self, *args, **kw)
        finally:
            self.endTime = time.perf_counter()
        return result

    def copy_timing_configuration(self, source_dir, dest_dir):
        """
        Copies the timing configuration from the specified source_dir (the
        directory in which the controlling script lives) to the specified
        dest_dir (a temporary working directory).

        This ignores all files and directories that begin with the string
        'TimeSCons-', and all '.svn' subdirectories.
        """
        for root, dirs, files in os.walk(source_dir):
            if '.svn' in dirs:
                dirs.remove('.svn')
            dirs = [d for d in dirs if not d.startswith('TimeSCons-')]
            files = [f for f in files if not f.startswith('TimeSCons-')]
            for dirname in dirs:
                source = os.path.join(root, dirname)
                destination = source.replace(source_dir, dest_dir)
                os.mkdir(destination)
                if sys.platform != 'win32':
                    shutil.copystat(source, destination)
            for filename in files:
                source = os.path.join(root, filename)
                destination = source.replace(source_dir, dest_dir)
                shutil.copy2(source, destination)

    def up_to_date(self, arguments='.', read_str="", **kw):
        """Asserts that all of the targets listed in arguments is
        up to date, but does not make any assumptions on other targets.
        This function is most useful in conjunction with the -n option.
        Note: This custom version for timings tests does NOT escape
              read_str.
        """
        s = ""
        for arg in arguments.split():
            s = f"{s}scons: `{arg}' is up to date.\n"
        kw['arguments'] = arguments
        stdout = self.wrap_stdout(read_str="REPLACEME", build_str=s)
        # Append '.*' so that timing output that comes after the
        # up-to-date output is okay.
        stdout = f"{re.escape(stdout)}.*"
        stdout = stdout.replace('REPLACEME', read_str)
        kw['stdout'] = stdout
        kw['match'] = self.match_re_dotall
        self.run(**kw)



# In some environments, $AR will generate a warning message to stderr
# if the library doesn't previously exist and is being created.  One
# way to fix this is to tell AR to be quiet (sometimes the 'c' flag),
# but this is difficult to do in a platform-/implementation-specific
# method.  Instead, we will use the following as a stderr match for
# tests that use AR so that we will view zero or more "ar: creating
# <file>" messages to be successful executions of the test (see
# test/AR.py for sample usage).

noisy_ar = r'(ar: creating( archive)? \S+\n?)*'

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
