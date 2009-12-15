#!/usr/bin/env python
#
# time-scons.py:  a wrapper script for running SCons timings
#
# This script exists to:
#
#     1)  Wrap the invocation of runtest.py to run the actual TimeSCons
#         timings consistently.  It does this specifically by building
#         SCons first, so .pyc compilation is not part of the timing.
#
#     2)  Provide an interface for running TimeSCons timings against
#         earlier revisions, before the whole TimeSCons infrastructure
#         was "frozen" to provide consistent timings.  This is done
#         by updating the specific pieces containing the TimeSCons
#         infrastructure to the earliest revision at which those pieces
#         were "stable enough."
#
# By encapsulating all the logic in this script, our Buildbot
# infrastructure only needs to call this script, and we should be able
# to change what we need to in this script and have it affect the build
# automatically when the source code is updated, without having to
# restart either master or slave.

import optparse
import os
import shutil
import subprocess
import sys
import tempfile
import xml.sax.handler


SubversionURL = 'http://scons.tigris.org/svn/scons'


# This is the earliest revision when the TimeSCons scripts collected
# "real," stable timings.  If we're timing a revision prior to this,
# we'll forcibly update the TimeSCons pieces of the tree to this revision
# to collect consistent timings for earlier revisions.
TimeSCons_revision = 4547

# The pieces of the TimeSCons infrastructure that are necessary to
# produce consistent timings, even when the rest of the tree is from
# an earlier revision that doesn't have these pieces.
TimeSCons_pieces = ['QMTest', 'timings', 'runtest.py']


class CommandRunner:
    """
    Executor class for commands, including "commands" implemented by
    Python functions.
    """
    verbose = True
    active = True

    def __init__(self, dictionary={}):
        self.subst_dictionary(dictionary)

    def subst_dictionary(self, dictionary):
        self._subst_dictionary = dictionary

    def subst(self, string, dictionary=None):
        """
        Substitutes (via the format operator) the values in the specified
        dictionary into the specified command.

        The command can be an (action, string) tuple.    In all cases, we
        perform substitution on strings and don't worry if something isn't
        a string.    (It's probably a Python function to be executed.)
        """
        if dictionary is None:
            dictionary = self._subst_dictionary
        if dictionary:
            try:
                string = string % dictionary
            except TypeError:
                pass
        return string

    def display(self, command, stdout=None, stderr=None):
        if not self.verbose:
            return
        if type(command) == type(()):
            func = command[0]
            args = command[1:]
            s = '%s(%s)' % (func.__name__, ', '.join(map(repr, args)))
        if type(command) == type([]):
            # TODO:    quote arguments containing spaces
            # TODO:    handle meta characters?
            s = ' '.join(command)
        else:
            s = self.subst(command)
        if not s.endswith('\n'):
            s += '\n'
        sys.stdout.write(s)
        sys.stdout.flush()

    def execute(self, command, stdout=None, stderr=None):
        """
        Executes a single command.
        """
        if not self.active:
            return 0
        if type(command) == type(''):
            command = self.subst(command)
            cmdargs = shlex.split(command)
            if cmdargs[0] == 'cd':
                 command = (os.chdir,) + tuple(cmdargs[1:])
        if type(command) == type(()):
            func = command[0]
            args = command[1:]
            return func(*args)
        else:
            if stdout is sys.stdout:
                # Same as passing sys.stdout, except works with python2.4.
                subout = None
            else:
                # Open pipe for anything else so Popen works on python2.4.
                subout = subprocess.PIPE
            if stderr is sys.stderr:
                # Same as passing sys.stdout, except works with python2.4.
                suberr = None
            elif stderr is None:
                # Merge with stdout if stderr isn't specified.
                suberr = subprocess.STDOUT
            else:
                # Open pipe for anything else so Popen works on python2.4.
                suberr = subprocess.PIPE
            p = subprocess.Popen(command,
                                 shell=(sys.platform == 'win32'),
                                 stdout=subout,
                                 stderr=suberr)
            p.wait()
            if stdout is None:
                self.stdout = p.stdout.read()
            elif stdout is not sys.stdout:
                stdout.write(p.stdout.read())
            if stderr not in (None, sys.stderr):
                stderr.write(p.stderr.read())
            return p.returncode

    def run(self, command, display=None, stdout=None, stderr=None):
        """
        Runs a single command, displaying it first.
        """
        if display is None:
            display = command
        self.display(display)
        return self.execute(command, stdout, stderr)

    def run_list(self, command_list, **kw):
        """
        Runs a list of commands, stopping with the first error.

        Returns the exit status of the first failed command, or 0 on success.
        """
        for command in command_list:
            status = self.run(command, **kw)
            if status:
                return status
        return 0


def get_svn_revisions(branch, revisions=None):
    """
    Fetch the actual SVN revisions for the given branch querying
    "svn log."  A string specifying a range of revisions can be
    supplied to restrict the output to a subset of the entire log.
    """
    command = ['svn', 'log', '--xml']
    if revisions:
        command.extend(['-r', revisions])
    command.append(branch)
    p = subprocess.Popen(command, stdout=subprocess.PIPE)

    class SVNLogHandler(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.revisions = []
        def startElement(self, name, attributes):
            if name == 'logentry':
                self.revisions.append(int(attributes['revision']))

    parser = xml.sax.make_parser()
    handler = SVNLogHandler()
    parser.setContentHandler(handler)
    parser.parse(p.stdout)
    return sorted(handler.revisions)


def script_commands(script):
    """
    Returns a list of the commands to be executed to test the specified
    TimeSCons script.  This involves building SCons (specifically the
    'tar-gz' Alias that creates and unpacks a SCons .tar.gz package,
    in order to have the *.py files compiled to *.pyc) after first
    removing the build directory, and then actually calling runtest.py
    to run the timing script.
    """
    commands = []
    if os.path.exists('build'):
        commands.extend([
            ['mv', 'build', 'build.OLD'],
            ['rm', '-rf', 'build.OLD'],
        ])
    commands.extend([
        [sys.executable, 'bootstrap.py', 'tar-gz'],
        # --noqmtest is necessary for the log to contain the
        # actual scons output (which qmtest normally swallows).
        [sys.executable, 'runtest.py', '--noqmtest', '-p', 'tar-gz', script],
    ])
    return commands

def do_revisions(cr, opts, branch, revisions, scripts):
    """
    Time the SCons branch specified scripts through a list of revisions.

    We assume we're in a (temporary) directory in which we can check
    out the source for the specified revisions.
    """
    stdout = sys.stdout
    stderr = sys.stderr

    for this_revision in revisions:

        if opts.logfiles:
            log_file = os.path.join(opts.origin, '%s.log' % this_revision)
            stdout = open(log_file, 'w')
            stderr = None

        commands = [
            ['svn', 'co', '-q', '-r', str(this_revision), branch, '.'],
        ]

        if int(this_revision) < int(TimeSCons_revision):
            commands.append(['svn', 'up', '-q', '-r', str(TimeSCons_revision)]
                            + TimeSCons_pieces)

        for script in scripts:
            commands.extend(script_commands(script))

        if int(this_revision) < int(TimeSCons_revision):
            # "Revert" the pieces that we previously updated to the
            # TimeSCons_revision, so the update to the next revision
            # works cleanly.
            commands.append(['svn', 'up', '-q', '-r', str(this_revision)]
                            + TimeSCons_pieces)

        status = cr.run(commands, stdout=stdout, stderr=stderr)
        if status:
            return status

    return 0

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage="time-scons.py [-hnq] [-r REVISION ...] [--branch BRANCH] [--svn] SCRIPT ...")
    parser.add_option("--branch", metavar="BRANCH", default="trunk",
                      help="time revision on BRANCH")
    parser.add_option("--logfiles", action="store_true",
                      help="generate separate log files for each revision")
    parser.add_option("-n", "--no-exec", action="store_true",
                      help="no execute, just print the command line")
    parser.add_option("-q", "--quiet", action="store_true",
                      help="quiet, don't print the command line")
    parser.add_option("-r", "--revision", metavar="REVISION",
                      help="time specified revisions")
    parser.add_option("--svn", action="store_true",
                      help="fetch actual revisions for BRANCH")
    opts, scripts = parser.parse_args(argv[1:])

    if not scripts:
        sys.stderr.write('No scripts specified.\n')
        sys.exit(1)

    CommandRunner.verbose = not opts.quiet
    CommandRunner.active = not opts.no_exec
    cr = CommandRunner()

    os.environ['TESTSCONS_SCONSFLAGS'] = ''

    branch = SubversionURL + '/' + opts.branch

    if opts.svn:
        revisions = get_svn_revisions(branch, opts.revision)
    else:
        # TODO(sgk):  parse this for SVN-style revision strings
        revisions = opts.revision

    if revisions:
        opts.origin = os.getcwd()
        tempdir = tempfile.mkdtemp(prefix='time-scons-')
        try:
            os.chdir(tempdir)
            status = do_revisions(cr, opts, branch, revisions, scripts)
        finally:
            os.chdir(opts.origin)
            shutil.rmtree(tempdir)
    else:
        for script in scripts:
            commands = script_commands(script)
            status = cr.run_list(commands, stdout=sys.stdout, stderr=sys.stderr)
            if status:
                return status

    return status


if __name__ == "__main__":
    sys.exit(main())
