#!/usr/bin/python
#

# A script for turning a generic Ubuntu system into a master for
# SCons development.
import getopt
import sys

from Command import CommandRunner, Usage

INITIAL_PACKAGES = [
    'git',
]

INSTALL_PACKAGES = [
    'wget',
    'xz-utils',
]

PYTHON_PACKAGES = [
    'g++',
    'gcc',
    'make',
    'zlib1g-dev',
    'libreadline-gplv2-dev',
    'libncursesw5-dev',
    'libssl-dev',
    'libsqlite3-dev',
    'tk-dev',
    'libgdbm-dev',
    'libc6-dev',
    'libbz2-dev'
]

BUILDING_PACKAGES = [
    'python3-lxml',
    'fop',
    'python3-dev',
    'rpm',
    'tar',
    'lynx',
    
    # additional packages that Bill Deegan's web page suggests
    #'docbook-to-man',
    #'docbook2x',
    #'tetex-bin',
    #'tetex-latex',

    'python3-sphinx',
    'python3-sphinx-rtd-theme',

]

DOCUMENTATION_PACKAGES = [
    'docbook-doc',
    'sphinx-doc',
    'gcc-doc',
    'pkg-config',
    'python3-doc',
    'openjdk-8-doc',
    'swig-doc',
    'texlive-doc',
]

TESTING_PACKAGES = [
    'bison',
    'cssc',
    'cvs',
    'flex',
    'g++',
    'gcc',
    # not on ubuntu 18.04
    #    'gcj',
    #    'hg',
    'ghostscript',
    'm4',
    'openssh-client',
    'openssh-server',
    'python3-profiler',
    'python3-line-profiler',
    'python3-all-dev',
    'pypy3-dev',
    'rcs',
    'rpm',
    'openjdk-8-jdk',
    'swig',
    'texlive-base-bin',
    'texlive-font-utils',
    'texlive-extra-utils',
    'texlive-latex-base',
    'texlive-latex-extra',
    'texlive-bibtex-extra',
    'docbook-xsl',
    'biber',
    'zip',
]

BUILDBOT_PACKAGES = [
    'buildbot-worker',
    'cron',
]

default_args = [
    'upgrade',
    'checkout',
    'building',
    'testing',
    'python-versions',
    'scons-versions',
]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    short_options = 'hnqy'
    long_options = ['help', 'no-exec', 'password=', 'quiet', 'username=',
                    'yes', 'assume-yes']

    helpstr = """\
Usage:  scons_dev_master.py [-hnqy] [--password PASSWORD] [--username USER]
                            [ACTIONS ...]

    ACTIONS (in default order):
        upgrade                 Upgrade the system
        checkout                Check out SCons
        building                Install packages for building SCons
        testing                 Install packages for testing SCons
        scons-versions          Install versions of SCons
        python-versions         Install versions of Python

    ACTIONS (optional):
        buildbot                Install packages for running BuildBot
"""

    scons_url = 'https://github.com/SCons/scons.git'
    sudo = 'sudo'
    password = '""'
    username = 'guest'
    yesflag = ''

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
                CommandRunner.execute = CommandRunner.do_not_execute
            elif o == '--password':
                password = a
            elif o in ('-q', '--quiet'):
                CommandRunner.display = CommandRunner.do_not_display
            elif o == '--username':
                username = a
            elif o in ('-y', '--yes', '--assume-yes'):
                yesflag = o
    except Usage as err:
        sys.stderr.write(str(err.msg) + '\n')
        sys.stderr.write('use -h to get help\n')
        return 2

    if not args:
        args = default_args

    initial_packages = ' '.join(INITIAL_PACKAGES)
    install_packages = ' '.join(INSTALL_PACKAGES)
    building_packages = ' '.join(BUILDING_PACKAGES)
    testing_packages = ' '.join(TESTING_PACKAGES)
    buildbot_packages = ' '.join(BUILDBOT_PACKAGES)
    python_packages = ' '.join(PYTHON_PACKAGES)
    doc_packages = ' '.join(DOCUMENTATION_PACKAGES)

    cmd = CommandRunner(locals())

    for arg in args:
        if arg == 'upgrade':
            cmd.run('%(sudo)s apt-get %(yesflag)s upgrade')
        elif arg == 'checkout':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(initial_packages)s')
            cmd.run('git clone" %(scons_url)s')
        elif arg == 'building':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(building_packages)s')
        elif arg == 'docs':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(doc_packages)s')
        elif arg == 'testing':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(testing_packages)s')
            #TODO: maybe copy ipkg-build from openwrt git
            #cmd.run('%(sudo)s wget https://raw.githubusercontent.com/openwrt/openwrt/master/scripts/ipkg-build SOMEWHERE')
        elif arg == 'buildbot':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(buildbot_packages)s')
        elif arg == 'python-versions':
            if install_packages:
                cmd.run('%(sudo)s apt-get %(yesflag)s install %(install_packages)s')
                install_packages = None
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(python_packages)s')
            try:
                import install_python
            except ImportError:
                msg = 'Could not import install_python; skipping python-versions.\n'
                sys.stderr.write(msg)
            else:
                install_python.main(['install_python.py', '-a'])
        elif arg == 'scons-versions':
            if install_packages:
                cmd.run('%(sudo)s apt-get %(yesflag)s install %(install_packages)s')
                install_packages = None
            try:
                import install_scons
            except ImportError:
                msg = 'Could not import install_scons; skipping scons-versions.\n'
                sys.stderr.write(msg)
            else:
                install_scons.main(['install_scons.py', '-a'])
        else:
            msg = '%s:  unknown argument %s\n'
            sys.stderr.write(msg % (argv[0], repr(arg)))
            sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
