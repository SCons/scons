"""
TestSCons.py:  a testing framework for the SCons software construction
tool.

A TestSCons environment object is created via the usual invocation:

    test = TestSCons()

TestScons is a subclass of TestCmd, and hence has available all of its
methods and attributes, as well as any overridden or additional methods
or attributes defined in this subclass.
"""

# Copyright 2001 Steven Knight

__revision__ = "TestSCons.py __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestCmd

class TestFailed(Exception):
    def __init__(self, args=None):
        self.args = args

class TestNoResult(Exception):
    def __init__(self, args=None):
        self.args = args

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

		program = 'scons.py'
		interpreter = 'python'
		workdir = ''

        The workdir value means that, by default, a temporary workspace
        directory is created for a TestSCons environment.  In addition,
	this method changes directory (chdir) to the workspace directory,
	so an explicit "chdir = '.'" on all of the run() method calls
	is not necessary.
	"""
	if not kw.has_key('program'):
	    kw['program'] = 'scons.py'
	if not kw.has_key('interpreter'):
	    kw['interpreter'] = 'python'
	if not kw.has_key('workdir'):
	    kw['workdir'] = ''
	apply(TestCmd.TestCmd.__init__, [self], kw)
	os.chdir(self.workdir)

    def run(self, stdout = None, stderr = '', **kw):
	"""Runs SCons.

	This is the same as the base TestCmd.run() method, with
	the addition of

		stdout	The expected standard output from
			the command.  A value of None means
			don't test standard output.

		stderr	The expected error output from
			the command.  A value of None means
			don't test error output.

        By default, this does not test standard output (stdout = None),
        and expects that error output is empty (stderr = "").
	"""
	try:
	    apply(TestCmd.TestCmd.run, [self], kw)
	except:
	    print "STDOUT ============"
	    print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise
	if stdout and not self.match(self.stdout(), stdout):
	    print "Expected STDOUT =========="
	    print stdout
	    print "Actual STDOUT ============"
	    print self.stdout()
	    raise TestFailed
	if stderr and not self.match(self.stderr(), stderr):
	    print "Expected STDERR =========="
	    print stderr
	    print "Actual STDERR ============"
	    print self.stderr()
	    raise TestFailed
