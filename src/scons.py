#! /usr/bin/env python
#
# SCons
#

__revision__ = "scons.py __REVISION__ __DATE__ __DEVELOPER__"

import getopt
import os.path
import string
import sys
import traceback

from scons.Node.FS import init, Dir, File, lookup
from scons.Environment import Environment
import scons.Job
from scons.Builder import Builder
from scons.Errors import *

class Task:
    "XXX: this is here only until the build engine is implemented"

    def __init__(self, target):
        self.target = target

    def execute(self):
        self.target.build()



class Taskmaster:
    "XXX: this is here only until the build engine is implemented"

    def __init__(self, targets):
        self.targets = targets
        self.num_iterated = 0


    def next_task(self):
        if self.num_iterated == len(self.targets):
            return None
        else:
            current = self.num_iterated
            self.num_iterated = self.num_iterated + 1
            return Task(self.targets[current])

    def is_blocked(self):
        return 0

    def executed(self, task):
        pass

    def failed(self, task):
        pass


# Global variables

local_help = None
num_jobs = 1
Scripts = []

# utility functions

def _scons_syntax_error(e):
    """Handle syntax errors. Print out a message and show where the error
    occurred.
    """
    etype, value, tb = sys.exc_info()
    lines = traceback.format_exception_only(etype, value)
    for line in lines:
        sys.stderr.write(line+'\n')

def _scons_user_error(e):
    """Handle user errors. Print out a message and a description of the
    error, along with the line number and routine where it occured.
    """
    print 'user error'
    etype, value, tb = sys.exc_info()
    while tb.tb_next is not None:
        tb = tb.tb_next
    lineno = traceback.tb_lineno(tb)
    filename = tb.tb_frame.f_code.co_filename
    routine = tb.tb_frame.f_code.co_name
    sys.stderr.write("\nSCons error: %s\n" % value)
    sys.stderr.write('File "%s", line %d, in %s\n' % (filename, lineno, routine))

def _scons_other_errors():
    """Handle all errors but user errors. Print out a message telling
    the user what to do in this case and print a normal trace.
    """
    print 'other errors'
    traceback.print_exc()



def Conscript(filename):
    global Scripts
    Scripts.append(filename)

def Help(text):
    global local_help
    if local_help:
	print text
	print "Use scons -H for help about command-line options."
	sys.exit(0)


option_list = []

# Generic routine for to-be-written options, used by multiple options below.

def opt_not_yet(opt, arg):
    sys.stderr.write("Warning:  the %s option is not yet implemented\n" % opt)

class Option:
    """Class for command-line option information.

    This exists to provide a central location for everything
    describing a command-line option, so that we can change
    options without having to update the code to handle the
    option in one place, the -h help message in another place,
    etc.  There are no methods here, only attributes.

    You can initialize an Option with the following:

	func	The function that will be called when this
		option is processed on the command line.
		Calling sequence is:

			func(opt, arg)

		If there is no func, then this Option probably
		stores an optstring to be printed.

	helpline
		The string to be printed in -h output.  If no
		helpline is specified but a help string is
		specified (the usual case), a helpline will be
		constructed automatically from the short, long,
		arg, and help attributes.  (In practice, then,
		setting helpline without setting func allows you
		to print arbitrary lines of text in the -h
		output.)

	short	The string for short, single-hyphen
		command-line options.
		Do not include the hyphen:

			'a' for -a, 'xy' for -x and -y, etc.

	long	An array of strings for long, double-hyphen
		command-line options.  Do not include
		the hyphens:

			['my-option', 'verbose']

	arg	If this option takes an argument, this string
		specifies how you want it to appear in the
		-h output ('DIRECTORY', 'FILE', etc.).

	help	The help string that will be printed for
		this option in the -h output.  Must be
		49 characters or fewer.

	future	If non-zero, this indicates that this feature
		will be supported in a future release, not
		the currently planned one.  SCons will
		recognize the option, but it won't show up
		in the -h output.

    The following attribute is derived from the supplied attributes:

	optstring
		A string, with hyphens, describing the flags
		for this option, as constructed from the
		specified short, long and arg attributes.

    All Option objects are stored in the global option_list list,
    in the order in which they're created.  This is the list
    that's used to generate -h output, so the order in which the
    objects are created is the order in which they're printed.

    The upshot is that specifying a command-line option and having
    everything work correctly is a matter of defining a function to
    process its command-line argument (set the right flag, update
    the right value), and then creating an appropriate Option object
    at the correct point in the code below.
    """

    def __init__(self, func = None, helpline = None,
		 short = None, long = None, arg = None,
		 help = None, future = None):
	self.func = func
	self.short = short
	self.long = long
	self.arg = arg
	self.help = help
	opts = []
	if self.short:
	    for c in self.short:
		if arg:
		    c = c + " " + arg
		opts = opts + ['-' + c]
	if self.long:
	    l = self.long
	    if arg:
		l = map(lambda x,a=arg: x + "=" + a, self.long)
	    opts = opts + map(lambda x: '--' + x, l)
	self.optstring = string.join(opts, ', ')
	if helpline:
	    self.helpline = helpline
	elif help and not future:
	    if len(self.optstring) <= 26:
		sep = " " * (28 - len(self.optstring))
	    else:
		sep = self.helpstring = "\n" + " " * 30
	    self.helpline = "  " + self.optstring + sep + self.help
	else:
	    self.helpline = None
	global option_list
	option_list.append(self)

# In the following instantiations, the help string should be no
# longer than 49 characters.  Use the following as a guide:
#	help = "1234567890123456789012345678901234567890123456789"

def opt_ignore(opt, arg):
    sys.stderr.write("Warning:  ignoring %s option\n" % opt)

Option(func = opt_ignore,
	short = 'bmSt', long = ['no-keep-going', 'stop', 'touch'],
	help = "Ignored for compatibility.")

Option(func = opt_not_yet,
	short = 'c', long = ['clean', 'remove'],
	help = "Remove specified targets and dependencies.")

Option(func = opt_not_yet, future = 1,
	long = ['cache-disable', 'no-cache'],
	help = "Do not retrieve built targets from Cache.")

Option(func = opt_not_yet, future = 1,
	long = ['cache-force', 'cache-populate'],
	help = "Copy already-built targets into the Cache.")

Option(func = opt_not_yet, future = 1,
	long = ['cache-show'],
	help = "Print what would have built Cached targets.")

def opt_C(opt, arg):
    try:
	os.chdir(arg)
    except:
	sys.stderr.write("Could not change directory to 'arg'\n")

Option(func = opt_C,
	short = 'C', long = ['directory'], arg = 'DIRECTORY',
	help = "Change to DIRECTORY before doing anything.")

Option(func = opt_not_yet,
	short = 'd',
	help = "Print file dependency information.")

Option(func = opt_not_yet, future = 1,
	long = ['debug'], arg = 'FLAGS',
	help = "Print various types of debugging information.")

Option(func = opt_not_yet, future = 1,
	short = 'e', long = ['environment-overrides'],
	help = "Environment variables override makefiles.")

def opt_f(opt, arg):
    global Scripts
    Scripts.append(arg)

Option(func = opt_f,
	short = 'f', long = ['file', 'makefile', 'sconstruct'], arg = 'FILE',
	help = "Read FILE as the top-level SConstruct file.")

def opt_help(opt, arg):
    global local_help
    local_help = 1

Option(func = opt_help,
	short = 'h', long = ['help'],
	help = "Print defined help message, or this one.")

def opt_help_options(opt, arg):
    PrintUsage()
    sys.exit(0)

Option(func = opt_help_options,
	short = 'H', long = ['help-options'],
	help = "Print this message and exit.")

Option(func = opt_not_yet,
	short = 'i', long = ['ignore-errors'],
	help = "Ignore errors from build actions.")

Option(func = opt_not_yet,
	short = 'I', long = ['include-dir'], arg = 'DIRECTORY',
	help = "Search DIRECTORY for imported Python modules.")

def opt_j(opt, arg):
    global num_jobs
    try:
        num_jobs = int(arg)
    except:
        PrintUsage()
        sys.exit(1)

    if num_jobs <= 0:
        PrintUsage()
        sys.exit(1)

Option(func = opt_j,
	short = 'j', long = ['jobs'], arg = 'N',
	help = "Allow N jobs at once.")

Option(func = opt_not_yet,
	short = 'k', long = ['keep-going'],
	help = "Keep going when a target can't be made.")

Option(func = opt_not_yet, future = 1,
	short = 'l', long = ['load-average', 'max-load'], arg = 'N',
	help = "Don't start multiple jobs unless load is below N.")

Option(func = opt_not_yet, future = 1,
	long = ['list-derived'],
	help = "Don't build; list files that would be built.")

Option(func = opt_not_yet, future = 1,
	long = ['list-actions'],
	help = "Don't build; list files and build actions.")

Option(func = opt_not_yet, future = 1,
	long = ['list-where'],
	help = "Don't build; list files and where defined.")

def opt_n(opt, arg):
    scons.Builder.execute_actions = None

Option(func = opt_n,
	short = 'n', long = ['no-exec', 'just-print', 'dry-run', 'recon'],
	help = "Don't build; just print commands.")

Option(func = opt_not_yet, future = 1,
	short = 'o', long = ['old-file', 'assume-old'], arg = 'FILE',
	help = "Consider FILE to be old; don't rebuild it.")

Option(func = opt_not_yet, future = 1,
	long = ['override'], arg = 'FILE',
	help = "Override variables as specified in FILE.")

Option(func = opt_not_yet, future = 1,
	short = 'p',
	help = "Print internal environments/objects.")

Option(func = opt_not_yet, future = 1,
	short = 'q', long = ['question'],
	help = "Don't build; exit status says if up to date.")

Option(func = opt_not_yet, future = 1,
	short = 'rR', long = ['no-builtin-rules', 'no-builtin-variables'],
	help = "Clear default environments and variables.")

Option(func = opt_not_yet, future = 1,
	long = ['random'],
	help = "Build dependencies in random order.")

def opt_s(opt, arg):
    scons.Builder.print_actions = None

Option(func = opt_s,
	short = 's', long = ['silent', 'quiet'],
	help = "Don't print commands.")

Option(func = opt_not_yet, future = 1,
	short = 'u', long = ['up', 'search-up'],
	help = "Search up directory tree for SConstruct.")

def option_v(opt, arg):
    print "SCons version __VERSION__, by Steven Knight et al."
    print "Copyright 2001 Steven Knight"
    sys.exit(0)

Option(func = option_v,
	short = 'v', long = ['version'],
	help = "Print the SCons version number and exit.")

Option(func = opt_not_yet,
	short = 'w', long = ['print-directory'],
	help = "Print the current directory.")

Option(func = opt_not_yet,
	long = ['no-print-directory'],
	help = "Turn off -w, even if it was turned on implicitly.")

Option(func = opt_not_yet, future = 1,
	long = ['write-filenames'], arg = 'FILE',
	help = "Write all filenames examined into FILE.")

Option(func = opt_not_yet, future = 1,
	short = 'W', long = ['what-if', 'new-file', 'assume-new'], arg = 'FILE',
	help = "Consider FILE to be changed.")

Option(func = opt_not_yet, future = 1,
	long = ['warn-undefined-variables'],
	help = "Warn when an undefined variable is referenced.")

Option(func = opt_not_yet, future = 1,
	short = 'Y', long = ['repository'], arg = 'REPOSITORY',
	help = "Search REPOSITORY for source and target files.")

short_opts = ""
long_opts = []
opt_func = {}

for o in option_list:
    if o.short:
	if o.func:
	    for c in o.short:
		opt_func['-' + c] = o.func
	short_opts = short_opts + o.short
	if o.arg:
	    short_opts = short_opts + ":"
    if o.long:
	if o.func:
	    for l in o.long:
		opt_func['--' + l] = o.func
	if o.arg:
	    long_opts = long_opts + map(lambda a: a + "=", o.long)
	else:
	    long_opts = long_opts + o.long



def PrintUsage():
    print "Usage: scons [OPTION] [TARGET] ..."
    print "Options:"
    for o in option_list:
	if o.helpline:
	    print o.helpline



def main():
    global Scripts, local_help, num_jobs

    try:
	cmd_opts, targets = getopt.getopt(sys.argv[1:], short_opts, long_opts)
#   except getopt.GetoptError, x:
    except:
        #print x
        PrintUsage()
        sys.exit(1)

    for opt, arg in cmd_opts:
	opt_func[opt](opt, arg)

    if not Scripts:
        for file in ['SConstruct', 'Sconstruct', 'sconstruct']:
            if os.path.isfile(file):
                Scripts.append(file)
                break

    if local_help and not Scripts:
	# They specified -h, but there's no SConstruct.  Give them
	# the options usage before we try to read it and fail.
	PrintUsage()
	sys.exit(0)

    # XXX The commented-out code here adds any "scons" subdirs in anything
    # along sys.path to sys.path.  This was an attempt at setting up things
    # so we can import "node.FS" instead of "scons.Node.FS".  This doesn't
    # quite fit our testing methodology, though, so save it for now until
    # the right solutions pops up.
    #
    #dirlist = []
    #for dir in sys.path:
    #    scons = os.path.join(dir, 'scons')
    #    if os.path.isdir(scons):
    #     dirlist = dirlist + [scons]
    #    dirlist = dirlist + [dir]
    #
    #sys.path = dirlist

    # initialize node factory
    init()

    while Scripts:
        file, Scripts = Scripts[0], Scripts[1:]
        execfile(file)

    if local_help:
	# They specified -h, but there was no Help() inside the
	# SConscript files.  Give them the options usage.
	PrintUsage()
	sys.exit(0)

    taskmaster = Taskmaster(map(lambda x: lookup(File, x), targets))

    jobs = scons.Job.Jobs(num_jobs, taskmaster)
    jobs.start()
    jobs.wait()

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print "Build interrupted."
    except SyntaxError, e:
        _scons_syntax_error(e)
    except UserError, e:
        _scons_user_error(e)
    except:
        _scons_other_errors()
