#!/usr/bin/env python
#
# A script for unpacking and installing different historic versions of
# SCons in a consistent manner for side-by-side development testing.
#
# This abstracts the changes we've made to the SCons setup.py scripts in
# different versions so that, no matter what version is specified, it ends
# up installing the necessary script(s) and library into version-specific
# names that won't interfere with other things.
#
# By default, we expect to extract the .tar.gz files from a Downloads
# subdirectory in the current directory.
#
# Note that this script cleans up after itself, removing the extracted
# directory in which we do the build.
#
# This was written for a Linux system (specifically Ubuntu) but should
# be reasonably generic to any POSIX-style system with a /usr/local
# hierarchy.

import getopt
import os
import shutil
import sys
import tarfile
from urllib.request import urlretrieve

from Command import CommandRunner, Usage

all_versions = [
    '0.01',
    '0.02',
    '0.03',
    '0.04',
    '0.05',
    '0.06',
    '0.07',
    '0.08',
    '0.09',
    '0.10',
    '0.11',
    '0.12',
    '0.13',
    '0.14',
    '0.90',
    '0.91',
    '0.92',
    '0.93',
    '0.94',
    #'0.94.1',
    '0.95',
    #'0.95.1',
    '0.96',
    '0.96.1',
    '0.96.90',
    '0.96.91',
    '0.96.92',
    '0.96.93',
    '0.96.94',
    '0.96.95',
    '0.96.96',
    '0.97',
    '0.97.0d20070809',
    '0.97.0d20070918',
    '0.97.0d20071212',
    '0.98.0',
    '0.98.1',
    '0.98.2',
    '0.98.3',
    '0.98.4',
    '0.98.5',
    '1.0.0',
    '1.0.0.d20080826',
    '1.0.1',
    '1.0.1.d20080915',
    '1.0.1.d20081001',
    '1.1.0',
    '1.1.0.d20081104',
    '1.1.0.d20081125',
    '1.1.0.d20081207',
    '1.2.0',
    '1.2.0.d20090113',
    '1.2.0.d20090223',
    '1.2.0.d20090905',
    '1.2.0.d20090919',
    '1.2.0.d20091224',
    '1.2.0.d20100117',
    '1.2.0.d20100306',
    '1.3.0',
    '1.3.0.d20100404',
    '1.3.0.d20100501',
    '1.3.0.d20100523',
    '1.3.0.d20100606',
    '2.0.0.alpha.20100508',
    '2.0.0.beta.20100531',
    '2.0.0.beta.20100605',
    '2.0.0.final.0',
]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    all = False
    downloads_dir = 'Downloads'
    downloads_url = 'http://downloads.sourceforge.net/scons'
    if sys.platform == 'win32':
        sudo = ''
        prefix = sys.prefix
    else:
        sudo = 'sudo'
        prefix = '/usr/local'
    python = sys.executable

    short_options = 'ad:hnp:q'
    long_options = ['all', 'help', 'no-exec', 'prefix=', 'quiet']

    helpstr = """\
Usage:  install_scons.py [-ahnq] [-d DIR] [-p PREFIX] [VERSION ...]

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
        except getopt.error as msg:
            raise Usage(msg)

        for o, a in opts:
            if o in ('-a', '--all'):
                all = True
            elif o in ('-d', '--downloads'):
                downloads_dir = a
            elif o in ('-h', '--help'):
                print(helpstr)
                sys.exit(0)
            elif o in ('-n', '--no-exec'):
                CommandRunner.execute = CommandRunner.do_not_execute
            elif o in ('-p', '--prefix'):
                prefix = a
            elif o in ('-q', '--quiet'):
                CommandRunner.display = CommandRunner.do_not_display
    except Usage as err:
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
        scons = 'scons-' + version
        tar_gz = os.path.join(downloads_dir, scons + '.tar.gz')
        tar_gz_url = "%s/%s.tar.gz" % (downloads_url, scons)

        cmd.subst_dictionary(locals())

        if not os.path.exists(tar_gz):
            if not os.path.exists(downloads_dir):
                cmd.run('mkdir %(downloads_dir)s')
            cmd.run((urlretrieve, tar_gz_url, tar_gz),
                    'wget -O %(tar_gz)s %(tar_gz_url)s')

        def extract(tar_gz):
            tarfile.open(tar_gz, "r:gz").extractall()
        cmd.run((extract, tar_gz), 'tar zxf %(tar_gz)s')

        cmd.run('cd %(scons)s')

        if version in ('0.01', '0.02', '0.03', '0.04', '0.05',
                       '0.06', '0.07', '0.08', '0.09', '0.10'):

            # 0.01 through 0.10 install /usr/local/bin/scons and
            # /usr/local/lib/scons.  The "scons" script knows how to
            # look up the library in a version-specific directory, but
            # we have to move both it and the library directory into
            # the right version-specific name by hand.
            cmd.run('%(python)s setup.py build')
            cmd.run('%(sudo)s %(python)s setup.py install --prefix=%(prefix)s')
            cmd.run('%(sudo)s mv %(prefix)s/bin/scons %(prefix)s/bin/scons-%(version)s')
            cmd.run('%(sudo)s mv %(prefix)s/lib/scons %(prefix)s/lib/scons-%(version)s')

        elif version in ('0.11', '0.12', '0.13', '0.14', '0.90'):

            # 0.11 through 0.90 install /usr/local/bin/scons and
            # /usr/local/lib/scons-%(version)s.  We just need to move
            # the script to a version-specific name.
            cmd.run('%(python)s setup.py build')
            cmd.run('%(sudo)s %(python)s setup.py install --prefix=%(prefix)s')
            cmd.run('%(sudo)s mv %(prefix)s/bin/scons %(prefix)s/bin/scons-%(version)s')

        elif version in ('0.91', '0.92', '0.93',
                         '0.94', '0.94.1',
                         '0.95', '0.95.1',
                         '0.96', '0.96.1', '0.96.90'):

            # 0.91 through 0.96.90 install /usr/local/bin/scons,
            # /usr/local/bin/sconsign and /usr/local/lib/scons-%(version)s.
            # We need to move both scripts to version-specific names.
            cmd.run('%(python)s setup.py build')
            cmd.run('%(sudo)s %(python)s setup.py install --prefix=%(prefix)s')
            cmd.run('%(sudo)s mv %(prefix)s/bin/scons %(prefix)s/bin/scons-%(version)s')
            cmd.run('%(sudo)s mv %(prefix)s/bin/sconsign %(prefix)s/bin/sconsign-%(version)s')
            lib_scons = os.path.join(prefix, 'lib', 'scons')
            if os.path.isdir(lib_scons):
                cmd.run('%(sudo)s mv %(prefix)s/lib/scons %(prefix)s/lib/scons-%(version)s')

        else:

            # Versions from 0.96.91 and later support what we want
            # with a --no-scons-script option.
            cmd.run('%(python)s setup.py build')
            cmd.run('%(sudo)s %(python)s setup.py install --prefix=%(prefix)s --no-scons-script')

        cmd.run('cd ..')

        cmd.run((shutil.rmtree, scons), 'rm -rf %(scons)s')

if __name__ == "__main__":
    sys.exit(main())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
