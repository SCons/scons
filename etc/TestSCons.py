"""
TestSCons.py:  a testing framework for the SCons software construction
tool.

A TestSCons environment object is created via the usual invocation:

    test = TestSCons()

TestScons is a subclass of TestCmd, and hence has available all of its
methods and attributes, as well as any overridden or additional methods
or attributes defined in this subclass.
"""

# Copyright 2001, 2002, 2003 Steven Knight

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import string
import sys

import TestCmd

python = TestCmd.python_executable


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


if sys.platform == 'win32':
    _exe   = '.exe'
    _obj   = '.obj'
    _shobj = '.obj'
    _dll   = '.dll'
    lib_   = ''
    fortran_lib = gccFortranLibs()
elif sys.platform == 'cygwin':
    _exe   = '.exe'
    _obj   = '.o'
    _shobj = '.os'
    _dll   = '.dll'
    lib_   = ''
    fortran_lib = gccFortranLibs()
elif string.find(sys.platform, 'irix') != -1:
    _exe   = ''
    _obj   = '.o'
    _shobj = '.o'
    _dll   = '.so'
    lib_   = 'lib'
    fortran_lib = ['ftn']
else:
    _exe   = ''
    _obj   = '.o'
    _shobj = '.os'
    _dll   = '.so'
    lib_   = 'lib'
    fortran_lib = gccFortranLibs()


class TestFailed(Exception):
    def __init__(self, args=None):
        self.args = args

class TestNoResult(Exception):
    def __init__(self, args=None):
        self.args = args

if os.name == 'posix':
    def _failed(self, status = 0):
        if self.status is None:
            return None
        if os.WIFSIGNALED(self.status):
            return None
        return _status(self) != status
    def _status(self):
        if os.WIFEXITED(self.status):
            return os.WEXITSTATUS(self.status)
        else:
            return None
elif os.name == 'nt':
    def _failed(self, status = 0):
        return not self.status is None and self.status != status
    def _status(self):
        return self.status

class TestSCons(TestCmd.TestCmd):
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
		match = TestCmd.match_exact
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
	    kw['match'] = TestCmd.match_exact
	if not kw.has_key('workdir'):
	    kw['workdir'] = ''
	apply(TestCmd.TestCmd.__init__, [self], kw)
	os.chdir(self.workdir)

    def run(self, options = None, arguments = None,
                  stdout = None, stderr = '', status = 0, **kw):
	"""Runs SCons.

        This is the same as the base TestCmd.run() method, with
        the addition of:

		stdout	The expected standard output from
			the command.  A value of None means
			don't test standard output.

		stderr	The expected error output from
			the command.  A value of None means
			don't test error output.

                status  The expected exit status from the 
                        command. 

        By default, this does not test standard output (stdout = None),
        and expects that error output is empty (stderr = "").
	"""
        if options:
            arguments = options + " " + arguments
        kw['arguments'] = arguments
	try:
	    apply(TestCmd.TestCmd.run, [self], kw)
	except:
	    print "STDOUT ============"
	    print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise
	if _failed(self, status):
            expect = ''
            if status != 0:
                expect = " (expected %s)" % str(status)
            print "%s returned %s%s" % (self.program, str(_status(self)), expect)
            print "STDOUT ============"
            print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise TestFailed
	if not stdout is None and not self.match(self.stdout(), stdout):
                print "Expected STDOUT =========="
                print stdout
                print "Actual STDOUT ============"
                print self.stdout()
                stderr = self.stderr()
                if stderr:
                    print "STDERR ==================="
                    print stderr
                raise TestFailed
	if not stderr is None and not self.match(self.stderr(), stderr):
            print "STDOUT ==================="
            print self.stdout()
	    print "Expected STDERR =========="
	    print stderr
	    print "Actual STDERR ============"
	    print self.stderr()
	    raise TestFailed

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

    def up_to_date(self, options = None, arguments = None, **kw):
        s = ""
        for arg in string.split(arguments):
            s = s + "scons: `%s' is up to date.\n" % arg
            if options:
                arguments = options + " " + arguments
        kw['arguments'] = arguments
        kw['stdout'] = self.wrap_stdout(build_str = s)
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
        old_match_func = self.match_func
        self.match_func = TestCmd.match_re_dotall
        apply(self.run, [], kw)
        self.match_func = old_match_func
