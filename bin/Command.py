#!/usr/bin/env python
#
# XXX Python script template
#
# XXX Describe what the script does here.
#
import getopt
import os
import shlex
import sys

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class CommandRunner:
    """
    Representation of a command to be executed.
    """

    def __init__(self, dictionary={}):
        self.subst_dictionary(dictionary)

    def subst_dictionary(self, dictionary):
        self._subst_dictionary = dictionary

    def subst(self, string, dictionary=None):
        """
        Substitutes (via the format operator) the values in the specified
        dictionary into the specified command.

        The command can be an (action, string) tuple.  In all cases, we
        perform substitution on strings and don't worry if something isn't
        a string.  (It's probably a Python function to be executed.)
        """
        if dictionary is None:
            dictionary = self._subst_dictionary
        if dictionary:
            try:
                string = string % dictionary
            except TypeError:
                pass
        return string

    def do_display(self, string):
        if isinstance(string, tuple):
            func = string[0]
            args = string[1:]
            s = '%s(%s)' % (func.__name__, ', '.join(map(repr, args)))
        else:
            s = self.subst(string)
        if not s.endswith('\n'):
            s += '\n'
        sys.stdout.write(s)
        sys.stdout.flush()

    def do_not_display(self, string):
        pass

    def do_execute(self, command):
        if isinstance(command, str):
            command = self.subst(command)
            cmdargs = shlex.split(command)
            if cmdargs[0] == 'cd':
                 command = (os.chdir,) + tuple(cmdargs[1:])
            elif cmdargs[0] == 'mkdir':
                 command = (os.mkdir,) + tuple(cmdargs[1:])
        if isinstance(command, tuple):
            func = command[0]
            args = command[1:]
            return func(*args)
        else:
            return os.system(command)

    def do_not_execute(self, command):
        pass

    display = do_display
    execute = do_execute

    def run(self, command, display=None):
        """
        Runs this command, displaying it first.

        The actual display() and execute() methods we call may be
        overridden if we're printing but not executing, or vice versa.
        """
        if display is None:
            display = command
        self.display(display)
        return self.execute(command)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    short_options = 'hnq'
    long_options = ['help', 'no-exec', 'quiet']

    helpstr = """\
Usage:  script-template.py [-hnq] 

  -h, --help                    Print this help and exit
  -n, --no-exec                 No execute, just print command lines
  -q, --quiet                   Quiet, don't print command lines
"""

    try:
        try:
            opts, args = getopt.getopt(argv[1:], short_options, long_options)
        except getopt.error as msg:
            raise Usage(msg)

        for o, a in opts:
            if o in ('-h', '--help'):
                print(helpstr)
                sys.exit(0)
            elif o in ('-n', '--no-exec'):
                Command.execute = Command.do_not_execute
            elif o in ('-q', '--quiet'):
                Command.display = Command.do_not_display
    except Usage as err:
        sys.stderr.write(err.msg)
        sys.stderr.write('use -h to get help')
        return 2

    commands = [
    ]

    for command in [ Command(c) for c in commands ]:
        status = command.run(command)
        if status:
            sys.exit(status)

if __name__ == "__main__":
    sys.exit(main())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
