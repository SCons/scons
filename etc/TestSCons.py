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

# Copyright 2001, 2002, 2003 Steven Knight

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

    def detect(self, var, prog=None):
        """
        Detect a program named 'prog' by first checking the construction
        variable named 'var' and finally searching the path used by
        SCons. If either method fails to detect the program, then false
        is returned, otherwise the full path to prog is returned. If
        prog is None, then the value of the environment variable will be
        used as prog.
        """

        import SCons.Environment
        env = SCons.Environment.Environment()
        try:
            if prog is None:
                prog = env[var]
            return env[var] == prog and env.WhereIs(prog)
        except KeyError:
            return None

    def detect_tool(self, tool, prog=None):
        """
        Given a tool (i.e., tool specification that would be passed
        to the "tools=" parameter of Environment()) and one a program that
        corresponds to that tool, return true if and only if we can find
        that tool using Environment.Detect().

        By default, progs is set to the value passed into the tools parameter.
        """

        if not prog:
            prog = tool
        import SCons.Environment
        import SCons.Errors
        try:
            env=SCons.Environment.Environment(tools=[tool])
        except (SCons.Errors.UserError, SCons.Errors.InternalError):
            return None
        return env.Detect([prog])

    def wrap_stdout(self, build_str = "", read_str = "", error = 0):
        """Wraps standard output string(s) in the normal
        "Reading ... done" and "Building ... done" strings
        """
        if error:
            term = "scons: building terminated because of errors.\n"
        else:
            term = "scons: done building targets.\n"
        return "scons: Reading SConscript files ...\n" + \
               read_str + \
               "scons: done reading SConscript files.\n" + \
               "scons: Building targets ...\n" + \
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

# In some environments, $AR will generate a warning message to stderr
# if the library doesn't previously exist and is being created.  One
# way to fix this is to tell AR to be quiet (sometimes the 'c' flag),
# but this is difficult to do in a platform-/implementation-specific
# method.  Instead, we will use the following as a stderr match for
# tests that use AR so that we will view zero or more "ar: creating
# <file>" messages to be successful executions of the test (see
# test/AR.py for sample usage).

noisy_ar=r'(ar: creating( archive)? \S+\n?)*'
