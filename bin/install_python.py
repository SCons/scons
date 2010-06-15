#!/usr/bin/env python
#
# A script for unpacking and installing different historic versions of
# Python in a consistent manner for side-by-side development testing.
#
# This was written for a Linux system (specifically Ubuntu) but should
# be reasonably generic to any POSIX-style system with a /usr/local
# hierarchy.

import getopt
import os
import shutil
import sys

from Command import CommandRunner, Usage

all_versions = [
    #'1.5.2',   # no longer available at python.org
    #'2.0.1',   # no longer supported by SCons
    #'2.1.3',   # no longer supported by SCons
    '2.2',
    #'2.2.3',
    '2.3',
    #'2.3.7',
    #'2.4',
    '2.4.6',
    '2.5.5',
    '2.6.5',
    '3.0.1',
    '3.1.2',
]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    all = False
    downloads_dir = 'Downloads'
    downloads_url = 'http://www.python.org/ftp/python'
    sudo = 'sudo'
    prefix = '/usr/local'

    short_options = 'ad:hnp:q'
    long_options = ['all', 'help', 'no-exec', 'prefix=', 'quiet']

    helpstr = """\
Usage:  install_python.py [-ahnq] [-d DIR] [-p PREFIX] [VERSION ...]

  -a, --all                     Install all SCons versions.
  -d DIR, --downloads=DIR       Downloads directory.
  -h, --help                    Print this help and exit
  -n, --no-exec                 No execute, just print command lines
  -p PREFIX, --prefix=PREFIX    Installation prefix.
  -q, --quiet                   Quiet, don't print command lines
"""

    try:
        try:
            opts, args = getopt.getopt(argv[1:], short_options, long_options)
        except getopt.error, msg:
            raise Usage(msg)

        for o, a in opts:
            if o in ('-a', '--all'):
                all = True
            elif o in ('-d', '--downloads'):
                downloads_dir = a
            elif o in ('-h', '--help'):
                print helpstr
                sys.exit(0)
            elif o in ('-n', '--no-exec'):
                CommandRunner.execute = CommandRunner.do_not_execute
            elif o in ('-p', '--prefix'):
                prefix = a
            elif o in ('-q', '--quiet'):
                CommandRunner.display = CommandRunner.do_not_display
    except Usage, err:
        sys.stderr.write(str(err.msg) + '\n')
        sys.stderr.write('use -h to get help\n')
        return 2

    if all:
        if args:
            msg = 'install-scons.py:  -a and version arguments both specified'
            sys.stderr.write(msg)
            sys.exit(1)

        args = all_versions

    cmd = CommandRunner()

    for version in args:
        python = 'Python-' + version
        tar_gz = os.path.join(downloads_dir, python + '.tgz')
        tar_gz_url = os.path.join(downloads_url, version, python + '.tgz')

        cmd.subst_dictionary(locals())

        if not os.path.exists(tar_gz):
            if not os.path.exists(downloads_dir):
                cmd.run('mkdir %(downloads_dir)s')
            cmd.run('wget -O %(tar_gz)s %(tar_gz_url)s')

        cmd.run('tar zxf %(tar_gz)s')

        cmd.run('cd %(python)s')

        cmd.run('./configure --prefix=%(prefix)s %(configureflags)s 2>&1 | tee configure.out')
        cmd.run('make 2>&1 | tee make.out')
        cmd.run('%(sudo)s make install')

        cmd.run('%(sudo)s rm -f %(prefix)s/bin/{idle,pydoc,python,python-config,smtpd.py}')

        cmd.run('cd ..')

        cmd.run((shutil.rmtree, python), 'rm -rf %(python)s')

if __name__ == "__main__":
    sys.exit(main())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
