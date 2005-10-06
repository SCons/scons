"""
TestSCons.py:  a testing framework for the SCons software construction
tool.

A TestSCons environment object is created via the usual invocation:

    test = TestSCons()

TestScons is a subclass of TestCommon, which is in turn is a subclass
of TestCmd), and hence has available all of the methods and attributes
from those classes, as well as any overridden or additional methods or
attributes defined in this subclass.
"""

# __COPYRIGHT__

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import string
import sys

from TestCommon import *
from TestCommon import __all__

__all__.extend([ 'TestSCons',
                 'python',
                 '_exe',
                 '_obj',
                 '_shobj',
                 'lib_',
                 '_lib',
                 'dll_',
                 '_dll'
               ])

python = python_executable
_exe = exe_suffix
_obj = obj_suffix
_shobj = shobj_suffix
_lib = lib_suffix
lib_ = lib_prefix
_dll = dll_suffix
dll_ = dll_prefix

def gccFortranLibs():
    """Test whether -lfrtbegin is required.  This can probably be done in
    a more reliable way, but using popen3 is relatively efficient."""

    libs = ['g2c']

    try:
        import popen2
        stderr = popen2.popen3('gcc -v')[2]
    except OSError:
        return libs

    for l in stderr.readlines():
        list = string.split(l)
        if len(list) > 3 and list[:2] == ['gcc', 'version']:
            if list[2][:2] == '3.':
                libs = ['frtbegin'] + libs
                break
    return libs


if sys.platform == 'cygwin':
    # On Cygwin, os.path.normcase() lies, so just report back the
    # fact that the underlying Win32 OS is case-insensitive.
    def case_sensitive_suffixes(s1, s2):
        return 0
else:
    def case_sensitive_suffixes(s1, s2):
        return (os.path.normcase(s1) != os.path.normcase(s2))


if sys.platform == 'win32':
    fortran_lib = gccFortranLibs()
elif sys.platform == 'cygwin':
    fortran_lib = gccFortranLibs()
elif string.find(sys.platform, 'irix') != -1:
    fortran_lib = ['ftn']
else:
    fortran_lib = gccFortranLibs()



file_expr = r"""File "[^"]*", line \d+, in .+
"""

# re.escape escapes too much.
def re_escape(str):
    for c in ['.', '[', ']', '(', ')', '*', '+', '?']:  # Not an exhaustive list.
        str = string.replace(str, c, '\\' + c)
    return str



class TestSCons(TestCommon):
    """Class for testing SCons.

    This provides a common place for initializing SCons tests,
    eliminating the need to begin every test with the same repeated
    initializations.
    """

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
	if not kw.has_key('program'):
            kw['program'] = os.environ.get('SCONS')
            if not kw['program']:
                if os.path.exists('scons'):
                    kw['program'] = 'scons'
                else:
                    kw['program'] = 'scons.py'
	if not kw.has_key('interpreter') and not os.environ.get('SCONS_EXEC'):
	    kw['interpreter'] = python
	if not kw.has_key('match'):
	    kw['match'] = match_exact
	if not kw.has_key('workdir'):
	    kw['workdir'] = ''
	apply(TestCommon.__init__, [self], kw)

    def Environment(self, ENV=None, *args, **kw):
        """
        Return a construction Environment that optionally overrides
        the default external environment with the specified ENV.
        """
        import SCons.Environment
        import SCons.Errors
        if not ENV is None:
            kw['ENV'] = ENV
        try:
            return apply(SCons.Environment.Environment, args, kw)
        except (SCons.Errors.UserError, SCons.Errors.InternalError):
            return None

    def detect(self, var, prog=None, ENV=None):
        """
        Detect a program named 'prog' by first checking the construction
        variable named 'var' and finally searching the path used by
        SCons. If either method fails to detect the program, then false
        is returned, otherwise the full path to prog is returned. If
        prog is None, then the value of the environment variable will be
        used as prog.
        """
        env = self.Environment(ENV)
        v = env.subst('$'+var)
        if not v:
            return None
        if prog is None:
            prog = v
        if v != prog:
            return None
        return env.WhereIs(prog)

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

    def where_is(self, prog, path=None):
        """
        Given a program, search for it in the specified external PATH,
        or in the actual external PATH is none is specified.
        """
        import SCons.Environment
        env = SCons.Environment.Environment()
        if path is None:
            path = os.environ['PATH']
        return env.WhereIs(prog, path)

    def wrap_stdout(self, build_str = "", read_str = "", error = 0, cleaning = 0):
        """Wraps standard output string(s) in the normal
        "Reading ... done" and "Building ... done" strings
        """
        cap,lc = [ ('Build','build'),
                   ('Clean','clean') ][cleaning]
        if error:
            term = "scons: %sing terminated because of errors.\n" % lc
        else:
            term = "scons: done %sing targets.\n" % lc
        return "scons: Reading SConscript files ...\n" + \
               read_str + \
               "scons: done reading SConscript files.\n" + \
               "scons: %sing targets ...\n" % cap + \
               build_str + \
               term

    def up_to_date(self, options = None, arguments = None, read_str = "", **kw):
        s = ""
        for arg in string.split(arguments):
            s = s + "scons: `%s' is up to date.\n" % arg
            if options:
                arguments = options + " " + arguments
        kw['arguments'] = arguments
        kw['stdout'] = self.wrap_stdout(read_str = read_str, build_str = s)
        kw['match'] = self.match_exact
        apply(self.run, [], kw)

    def not_up_to_date(self, options = None, arguments = None, **kw):
        """Asserts that none of the targets listed in arguments is
        up to date, but does not make any assumptions on other targets.
        This function is most useful in conjunction with the -n option.
        """
        s = ""
        for  arg in string.split(arguments):
            s = s + "(?!scons: `%s' is up to date.)" % arg
            if options:
                arguments = options + " " + arguments
        kw['arguments'] = arguments
        kw['stdout'] = self.wrap_stdout(build_str="("+s+"[^\n]*\n)*")
        kw['stdout'] = string.replace(kw['stdout'],'\n','\\n')
        kw['stdout'] = string.replace(kw['stdout'],'.','\\.')
        kw['match'] = self.match_re_dotall
        apply(self.run, [], kw)

    def skip_test(self, message="Skipping test.\n"):
        """Skips a test.

        Proper test-skipping behavior is dependent on whether we're being
        executed as part of development of a change under Aegis.

        Technically, skipping a test is a NO RESULT, but Aegis will
        treat that as a test failure and prevent the change from going
        to the next step.  We don't want to force anyone using Aegis
        to have to install absolutely every tool used by the tests,
        so we actually report to Aegis that a skipped test has PASSED
        so that the workflow isn't held up.
        """
        if message:
            sys.stdout.write(message)
            sys.stdout.flush()
        devdir = os.popen("aesub '$dd' 2>/dev/null", "r").read()[:-1]
        intdir = os.popen("aesub '$intd' 2>/dev/null", "r").read()[:-1]
        if devdir and self._cwd[:len(devdir)] == devdir or \
           intdir and self._cwd[:len(intdir)] == intdir:
            # We're under the development directory for this change,
            # so this is an Aegis invocation; pass the test (exit 0).
            self.pass_test()
        else:
            # skip=1 means skip this function when showing where this
            # result came from.  They only care about the line where the
            # script called test.skip_test(), not the line number where
            # we call test.no_result().
            self.no_result(skip=1)

    def diff_substr(self, expect, actual):
        i = 0
        for x, y in zip(expect, actual):
            if x != y:
                return "Actual did not match expect at char %d:\n" \
                       "    Expect:  %s\n" \
                       "    Actual:  %s\n" \
                       % (i, repr(expect[i-20:i+40]), repr(actual[i-20:i+40]))
            i = i + 1
        return "Actual matched the expected output???"

    def java_ENV(self):
        """
        Return a default external environment that uses a local Java SDK
        in preference to whatever's found in the default PATH.
        """
        import SCons.Environment
        env = SCons.Environment.Environment()
        java_path = [
            '/usr/local/j2sdk1.4.2/bin',
            '/usr/local/j2sdk1.4.1/bin',
            '/usr/local/j2sdk1.3.1/bin',
            '/usr/local/j2sdk1.3.0/bin',
            '/usr/local/j2sdk1.2.2/bin',
            '/usr/local/j2sdk1.2/bin',
            '/usr/local/j2sdk1.1.8/bin',
            '/usr/local/j2sdk1.1.7/bin',
            '/usr/local/j2sdk1.1.6/bin',
            '/usr/local/j2sdk1.1.5/bin',
            '/usr/local/j2sdk1.1.4/bin',
            '/usr/local/j2sdk1.1.3/bin',
            '/usr/local/j2sdk1.1.2/bin',
            '/usr/local/j2sdk1.1.1/bin',
            env['ENV']['PATH'],
        ]
        env['ENV']['PATH'] = string.join(java_path, os.pathsep)
        return env['ENV']

    def Qt_dummy_installation(self, dir='qt'):
        # create a dummy qt installation

        self.subdir( dir, [dir, 'bin'], [dir, 'include'], [dir, 'lib'] )

        self.write([dir, 'bin', 'mymoc.py'], """\
import getopt
import sys
import string
import re
cmd_opts, args = getopt.getopt(sys.argv[1:], 'io:', [])
output = None
impl = 0
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    elif opt == '-i': impl = 1
    else: opt_string = opt_string + ' ' + opt
for a in args:
    contents = open(a, 'rb').read()
    subst = r'{ my_qt_symbol( "' + a + '\\\\n" ); }'
    if impl:
        contents = re.sub( r'#include.*', '', contents )
    output.write(string.replace(contents, 'Q_OBJECT', subst))
output.close()
sys.exit(0)
""")

        self.write([dir, 'bin', 'myuic.py'], """\
import os.path
import re
import sys
import string
output_arg = 0
impl_arg = 0
impl = None
source = None
for arg in sys.argv[1:]:
    if output_arg:
        output = open(arg, 'wb')
        output_arg = 0
    elif impl_arg:
        impl = arg
        impl_arg = 0
    elif arg == "-o":
        output_arg = 1
    elif arg == "-impl":
        impl_arg = 1
    else:
        if source:
            sys.exit(1)
        source = open(arg, 'rb')
        sourceFile = arg
if impl:
    output.write( '#include "' + impl + '"\\n' )
    includes = re.findall('<include.*?>(.*?)</include>', source.read())
    for incFile in includes:
        # this is valid for ui.h files, at least
        if os.path.exists(incFile):
            output.write('#include "' + incFile + '"\\n')
else:
    output.write( '#include "my_qobject.h"\\n' + source.read() + " Q_OBJECT \\n" )
output.close()
sys.exit(0)
""" )

        self.write([dir, 'include', 'my_qobject.h'], r"""
#define Q_OBJECT ;
void my_qt_symbol(const char *arg);
""")

        self.write([dir, 'lib', 'my_qobject.cpp'], r"""
#include "../include/my_qobject.h"
#include <stdio.h>
void my_qt_symbol(const char *arg) {
  printf( arg );
}
""")

        self.write(['qt', 'lib', 'SConstruct'], r"""
env = Environment()
env.StaticLibrary( 'myqt', 'my_qobject.cpp' )
""")

        self.run(chdir = self.workpath('qt', 'lib'),
                 arguments = '.',
                 stderr = noisy_ar,
                 match = self.match_re_dotall)

        self.QT = self.workpath(dir)
        self.QT_LIB = 'myqt'
        self.QT_MOC = '%s %s' % (python, self.workpath(dir, 'bin', 'mymoc.py'))
        self.QT_UIC = '%s %s' % (python, self.workpath(dir, 'bin', 'myuic.py'))

    def Qt_create_SConstruct(self, place):
        if type(place) is type([]):
            place = apply(test.workpath, place)
        self.write(place, """\
if ARGUMENTS.get('noqtdir', 0): QTDIR=None
else: QTDIR=r'%s'
env = Environment(QTDIR = QTDIR,
                  QT_LIB = r'%s',
                  QT_MOC = r'%s',
                  QT_UIC = r'%s',
                  tools=['default','qt'])
dup = 1
if ARGUMENTS.get('build_dir', 0):
    if ARGUMENTS.get('chdir', 0):
        SConscriptChdir(1)
    else:
        SConscriptChdir(0)
    dup=int(ARGUMENTS.get('dup', 1))
    if dup == 0:
        builddir = 'build_dup0'
        env['QT_DEBUG'] = 1
    else:
        builddir = 'build'
    BuildDir(builddir, '.', duplicate=dup)
    print builddir, dup
    sconscript = Dir(builddir).File('SConscript')
else:
    sconscript = File('SConscript')
Export("env dup")
SConscript( sconscript )
""" % (self.QT, self.QT_LIB, self.QT_MOC, self.QT_UIC))

    def msvs_versions(self):
        if not hasattr(self, '_msvs_versions'):

            # Determine the SCons version and the versions of the MSVS
            # environments installed on the test machine.
            #
            # We do this by executing SCons with an SConstruct file
            # (piped on stdin) that spits out Python assignments that
            # we can just exec().  We construct the SCons.__"version"__
            # string in the input here so that the SCons build itself
            # doesn't fill it in when packaging SCons.
            input = """\
import SCons
print "self._scons_version =", repr(SCons.__%s__)
env = Environment();
print "self._msvs_versions =", str(env['MSVS']['VERSIONS'])
""" % 'version'
        
            self.run(arguments = '-n -q -Q -f -', stdin = input)
            exec(self.stdout())

        return self._msvs_versions

    def vcproj_sys_path(self, fname):
        """
        """
        orig = 'sys.path = [ join(sys'

        enginepath = repr(os.path.join(self._cwd, '..', 'engine'))
        replace = 'sys.path = [ %s, join(sys' % enginepath

        contents = self.read(fname)
        contents = string.replace(contents, orig, replace)
        self.write(fname, contents)

    def msvs_substitute(self, input, msvs_ver, subdir=None, python=sys.executable):
        if not hasattr(self, '_msvs_versions'):
            self.msvs_versions()

        if subdir:
            workpath = self.workpath(subdir)
        else:
            workpath = self.workpath()

        exec_script_main = "from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-%s'), join(sys.prefix, 'scons-%s'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons') ] + sys.path; import SCons.Script; SCons.Script.main()" % (self._scons_version, self._scons_version)
        exec_script_main_xml = string.replace(exec_script_main, "'", "&apos;")

        result = string.replace(input, r'<WORKPATH>', workpath)
        result = string.replace(result, r'<PYTHON>', python)
        result = string.replace(result, r'<SCONS_SCRIPT_MAIN>', exec_script_main)
        result = string.replace(result, r'<SCONS_SCRIPT_MAIN_XML>', exec_script_main_xml)
        return result

# In some environments, $AR will generate a warning message to stderr
# if the library doesn't previously exist and is being created.  One
# way to fix this is to tell AR to be quiet (sometimes the 'c' flag),
# but this is difficult to do in a platform-/implementation-specific
# method.  Instead, we will use the following as a stderr match for
# tests that use AR so that we will view zero or more "ar: creating
# <file>" messages to be successful executions of the test (see
# test/AR.py for sample usage).

noisy_ar=r'(ar: creating( archive)? \S+\n?)*'
