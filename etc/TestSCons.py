"""
TestSCmd.py:  a testing framework for commands and scripts.

The TestCmd module provides a framework for portable automated testing
of executable commands and scripts (in any language, not just Python),
especially commands and scripts that require file system interaction.

In addition to running tests and evaluating conditions, the TestCmd module
manages and cleans up one or more temporary workspace directories, and
provides methods for creating files and directories in those workspace
directories from in-line data, here-documents), allowing tests to be
completely self-contained.

A TestCmd environment object is created via the usual invocation:

    test = TestCmd()

The TestCmd module provides pass_test(), fail_test(), and no_result()
unbound methods that report test results for use with the Aegis change
management system.  These methods terminate the test immediately,
reporting PASSED, FAILED, or NO RESULT respectively, and exiting with
status 0 (success), 1 or 2 respectively.  This allows for a distinction
between an actual failed test and a test that could not be properly
evaluated because of an external condition (such as a full file system
or incorrect permissions).
"""

# Copyright 2001 Steven Knight

__revision__ = "TestSCons.py __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestCmd

class TestSCons(TestCmd.TestCmd):
    """Class for testing SCons
    """

    def __init__(self, **kw):
	if not kw.has_key('program'):
	    kw['program'] = 'scons.py'
	if not kw.has_key('interpreter'):
	    kw['interpreter'] = 'python'
	if not kw.has_key('workdir'):
	    kw['workdir'] = ''
	apply(TestCmd.TestCmd.__init__, [self], kw)
	os.chdir(self.workdir)

#    def __del__(self):
#	self.cleanup()
#
#    def __repr__(self):
#	return "%x" % id(self)
#
#    def cleanup(self, condition = None):
#	"""Removes any temporary working directories for the specified
#	TestCmd environment.  If the environment variable PRESERVE was
#	set when the TestCmd environment was created, temporary working
#	directories are not removed.  If any of the environment variables
#	PRESERVE_PASS, PRESERVE_FAIL, or PRESERVE_NO_RESULT were set
#	when the TestCmd environment was created, then temporary working
#	directories are not removed if the test passed, failed, or had
#	no result, respectively.  Temporary working directories are also
#	preserved for conditions specified via the preserve method.
#
#	Typically, this method is not called directly, but is used when
#	the script exits to clean up temporary working directories as
#	appropriate for the exit status.
#	"""
#	if not self._dirlist:
#	    return
#	if condition is None:
#	    condition = self.condition
#	#print "cleanup(" + condition + "):  ", self._preserve
#	if self._preserve[condition]:
#	    return
#	os.chdir(self._cwd)
#	self.workdir = None
#	list = self._dirlist[:]
#	self._dirlist = []
#	list.reverse()
#	for dir in list:
#	    self.writable(dir, 1)
#	    shutil.rmtree(dir, ignore_errors = 1)
#	try:
#	    global _Cleanup
#	    _Cleanup.remove(self)
#	except (AttributeError, ValueError):
#	    pass
#
#    def description_set(self, description):
#	"""Set the description of the functionality being tested.
#	"""
#	self.description = description
#
##    def diff(self):
##	"""Diff two arrays.
##	"""
#
#    def fail_test(self, condition = 1, function = None, skip = 0):
#	"""Cause the test to fail.
#	"""
#	if not condition:
#	    return
#	self.condition = 'fail_test'
#	fail_test(self = self,
#		  condition = condition,
#		  function = function,
#		  skip = skip)
#
#    def interpreter_set(self, interpreter):
#	"""Set the program to be used to interpret the program
#	under test as a script.
#	"""
#	self.interpreter = interpreter
#
#    def match(self, lines, matches):
#	"""Compare actual and expected file contents.
#	"""
#	return self.match_func(lines, matches)
#
#    def match_exact(self, lines, matches):
#	"""Compare actual and expected file contents.
#	"""
#	return match_exact(lines, matches)
#
#    def match_re(self, lines, res):
#	"""Compare actual and expected file contents.
#	"""
#	return match_re(lines, res)
#
#    def no_result(self, condition = 1, function = None, skip = 0):
#	"""Report that the test could not be run.
#	"""
#	if not condition:
#	    return
#	self.condition = 'no_result'
#	no_result(self = self,
#		  condition = condition,
#		  function = function,
#		  skip = skip)
#
#    def pass_test(self, condition = 1, function = None):
#	"""Cause the test to pass.
#	"""
#	if not condition:
#	    return
#	self.condition = 'pass_test'
#	pass_test(self = self, condition = condition, function = function)
#
#    def preserve(self, *conditions):
#	"""Arrange for the temporary working directories for the
#	specified TestCmd environment to be preserved for one or more
#	conditions.  If no conditions are specified, arranges for
#	the temporary working directories to be preserved for all
#	conditions.
#	"""
#	if conditions is ():
#	    conditions = ('pass_test', 'fail_test', 'no_result')
#	for cond in conditions:
#	    self._preserve[cond] = 1
#
#    def program_set(self, program):
#	"""Set the executable program or script to be tested.
#	"""
#	if program and not os.path.isabs(program):
#	    program = os.path.join(self._cwd, program)
#	self.program = program
#
#    def read(self, file, mode = 'rb'):
#	"""Reads and returns the contents of the specified file name.
#	The file name may be a list, in which case the elements are
#	concatenated with the os.path.join() method.  The file is
#	assumed to be under the temporary working directory unless it
#	is an absolute path name.  The I/O mode for the file may
#	be specified; it must begin with an 'r'.  The default is
#	'rb' (binary read).
#	"""
#	if type(file) is ListType:
#	    file = apply(os.path.join, tuple(file))
#	if not os.path.isabs(file):
#	    file = os.path.join(self.workdir, file)
#	if mode[0] != 'r':
#	    raise ValueError, "mode must begin with 'r'"
#	return open(file, mode).read()
#
#    def run(self, program = None,
#		  interpreter = None,
#		  arguments = None,
#		  chdir = None,
#		  stdin = None):
#	"""Runs a test of the program or script for the test
#	environment.  Standard output and error output are saved for
#	future retrieval via the stdout() and stderr() methods.
#	"""
#	if chdir:
#	    oldcwd = os.getcwd()
#	    if not os.path.isabs(chdir):
#		chdir = os.path.join(self.workpath(chdir))
#	    if self.verbose:
#		sys.stderr.write("chdir(" + chdir + ")\n")
#	    os.chdir(chdir)
#	cmd = None
#	if program:
#	    if not os.path.isabs(program):
#		program = os.path.join(self._cwd, program)
#	    cmd = program
#	    if interpreter:
#		cmd = interpreter + " " + cmd
#	else:
#	    cmd = self.program
#	    if self.interpreter:
#		cmd =  self.interpreter + " " + cmd
#	if arguments:
#	    cmd = cmd + " " + arguments
#	if self.verbose:
#	    sys.stderr.write(cmd + "\n")
#	try:
#	    p = popen2.Popen3(cmd, 1)
#	except AttributeError:
#	    (tochild, fromchild, childerr) = os.popen3(cmd)
#	    if stdin:
#		if type(stdin) is ListType:
#		    for line in stdin:
#			tochild.write(line)
#		else:
#		    tochild.write(stdin)
#	    tochild.close()
#	    self._stdout.append(fromchild.read())
#	    self._stderr.append(childerr.read())
#	    fromchild.close()
#	    self._status = childerr.close()
#	except:
#	    raise
#	else:
#	    if stdin:
#		if type(stdin) is ListType:
#		    for line in stdin:
#			p.tochild.write(line)
#		else:
#		    p.tochild.write(stdin)
#	    p.tochild.close()
#	    self._stdout.append(p.fromchild.read())
#	    self._stderr.append(p.childerr.read())
#	    self.status = p.wait()
#	if chdir:
#	    os.chdir(oldcwd)
#
#    def stderr(self, run = None):
#	"""Returns the error output from the specified run number.
#	If there is no specified run number, then returns the error
#	output of the last run.  If the run number is less than zero,
#	then returns the error output from that many runs back from the
#	current run.
#	"""
#	if not run:
#	    run = len(self._stderr)
#	elif run < 0:
#	    run = len(self._stderr) + run
#	run = run - 1
#	return self._stderr[run]
#
#    def stdout(self, run = None):
#	"""Returns the standard output from the specified run number.
#	If there is no specified run number, then returns the standard
#	output of the last run.  If the run number is less than zero,
#	then returns the standard output from that many runs back from
#	the current run.
#	"""
#	if not run:
#	    run = len(self._stdout)
#	elif run < 0:
#	    run = len(self._stdout) + run
#	run = run - 1
#	return self._stdout[run]
#
#    def subdir(self, *subdirs):
#	"""Create new subdirectories under the temporary working
#	directory, one for each argument.  An argument may be a list,
#	in which case the list elements are concatenated using the
#	os.path.join() method.  Subdirectories multiple levels deep
#	must be created using a separate argument for each level:
#
#		test.subdir('sub', ['sub', 'dir'], ['sub', 'dir', 'ectory'])
#
#	Returns the number of subdirectories actually created.
#	"""
#	count = 0
#	for sub in subdirs:
#	    if sub is None:
#		continue
#	    if type(sub) is ListType:
#		sub = apply(os.path.join, tuple(sub))
#	    new = os.path.join(self.workdir, sub)
#	    try:
#		os.mkdir(new)
#	    except:
#		pass
#	    else:
#		count = count + 1
#	return count
#
#    def verbose_set(self, verbose):
#	"""Set the verbose level.
#	"""
#	self.verbose = verbose
#
#    def workdir_set(self, path):
#	"""Creates a temporary working directory with the specified
#	path name.  If the path is a null string (''), a unique
#	directory name is created.
#	"""
#	if (path != None):
#	    if path == '':
#		path = tempfile.mktemp()
#	    if path != None:
#		os.mkdir(path)
#	    self._dirlist.append(path)
#	    global _Cleanup
#	    try:
#		_Cleanup.index(self)
#	    except ValueError:
#		_Cleanup.append(self)
#	    # We'd like to set self.workdir like this:
#	    #	self.workdir = path
#	    # But symlinks in the path will report things
#	    # differently from os.getcwd(), so chdir there
#	    # and back to fetch the canonical path.
#	    cwd = os.getcwd()
#	    os.chdir(path)
#	    self.workdir = os.getcwd()
#	    os.chdir(cwd)
#	else:
#	    self.workdir = None
#
#    def workpath(self, *args):
#	"""Returns the absolute path name to a subdirectory or file
#	within the current temporary working directory.  Concatenates
#	the temporary working directory name with the specified
#	arguments using the os.path.join() method.
#	"""
#	return apply(os.path.join, (self.workdir,) + tuple(args))
#
#    def writable(self, top, write):
#	"""Make the specified directory tree writable (write == 1)
#	or not (write == None).
#	"""
#
#	def _walk_chmod(arg, dirname, names):
#	    st = os.stat(dirname)
#	    os.chmod(dirname, arg(st[stat.ST_MODE]))
#	    for name in names:
#		n = os.path.join(dirname, name)
#		st = os.stat(n)
#		os.chmod(n, arg(st[stat.ST_MODE]))
#
#	def _mode_writable(mode):
#	    return stat.S_IMODE(mode|0200)
#
#	def _mode_non_writable(mode):
#	    return stat.S_IMODE(mode&~0200)
#
#	if write:
#	    f = _mode_writable
#	else:
#	    f = _mode_non_writable
#	os.path.walk(top, _walk_chmod, f)
#
#    def write(self, file, content, mode = 'wb'):
#	"""Writes the specified content text (second argument) to the
#	specified file name (first argument).  The file name may be
#	a list, in which case the elements are concatenated with the
#	os.path.join() method.	The file is created under the temporary
#	working directory.  Any subdirectories in the path must already
#	exist.  The I/O mode for the file may be specified; it must
#	begin with a 'w'.  The default is 'wb' (binary write).
#	"""
#	if type(file) is ListType:
#	    file = apply(os.path.join, tuple(file))
#	if not os.path.isabs(file):
#	    file = os.path.join(self.workdir, file)
#	if mode[0] != 'w':
#	    raise ValueError, "mode must begin with 'w'"
#	open(file, mode).write(content)
