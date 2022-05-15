import time
import os
import socket

from SCons.Script import ARGUMENTS

class BuildCommandLine:

    git = None

    def init_command_line_variables(self):
        self.command_line_variables = [
            ("BUILDDIR=", "The directory in which to build the packages.  " +
             "The default is the './build' subdirectory."),

            ("BUILD_ID=", "An identifier for the specific build." +
             "The default is the Subversion revision number."),

            ("BUILD_SYSTEM=", "The system on which the packages were built.  " +
             "The default is whatever hostname is returned " +
             "by socket.gethostname(). If SOURCE_DATE_EPOCH " +
             "env var is set, '_reproducible' is the default."),

            ("CHECKPOINT=", "The specific checkpoint release being packaged, " +
             "which will be appended to the VERSION string.  " +
             "A value of CHECKPOINT=d will generate a string " +
             "of 'd' plus today's date in the format YYYMMDD.  " +
             "A value of CHECKPOINT=r will generate a " +
             "string of 'r' plus the Subversion revision " +
             "number.  Any other CHECKPOINT= string will be " +
             "used as is.  There is no default value."),

            ("DATE=", "The date string representing when the packaging " +
             "build occurred.  The default is the day and time " +
             "the SConstruct file was invoked, in the format " +
             "YYYY/MM/DD HH:MM:SS."),

            ("DEVELOPER=", "The developer who created the packages.  " +
             "The default is the first set environment " +
             "variable from the list $USERNAME, $LOGNAME, $USER." +
             "If the SOURCE_DATE_EPOCH env var is set, " +
             "'_reproducible' is the default."),

            ("REVISION=", "The revision number of the source being built.  " +
             "The default is the git hash returned " +
             "'git rev-parse HEAD', with an appended string of " +
             "'[MODIFIED]' if there are any changes in the " +
             "working copy."),

            ("VERSION=", "The SCons version being packaged.  The default " +
             "is the hard-coded value '%s' " % self.default_version +
             "from this SConstruct file."),

            ("SKIP_DOC=", "Skip building all documents. The default is False (build docs)"),
        ]

    def __init__(self, default_version="99.99.99"):
        self.date = None
        self.default_version = default_version
        self.developer = None
        self.build_dir = None
        self.build_system = None
        self.version = None
        self.revision = None
        self.git_status_lines = []
        self.git_hash = None

        self.init_command_line_variables()

    def set_date(self):
        """
        Determine the release date and the pattern to match a date
        Mon, 05 Jun 2010 21:17:15 -0700
        NEW DATE WILL BE INSERTED HERE
        """

        min = (time.daylight and time.altzone or time.timezone) // 60
        hr = min // 60
        min = -(min % 60 + hr * 100)
        self.date = (time.strftime('%a, %d %b %Y %X', time.localtime(int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))))
                     + ' %+.4d' % min)

    def process_command_line_vars(self):
        #
        # Now grab the information that we "build" into the files.
        #
        self.date = ARGUMENTS.get('DATE')
        if not self.date:
            self.set_date()

        self.developer = ARGUMENTS.get('DEVELOPER')
        if not self.developer:
            for variable in ['USERNAME', 'LOGNAME', 'USER']:
                self.developer = os.environ.get(variable)
                if self.developer:
                    break
            if os.environ.get('SOURCE_DATE_EPOCH'):
                self.developer = '_reproducible'

        self.build_system = ARGUMENTS.get('BUILD_SYSTEM')
        if not self.build_system:
            if os.environ.get('SOURCE_DATE_EPOCH'):
                self.build_system = '_reproducible'
            else:
                self.build_system = socket.gethostname().split('.')[0]

        self.version = ARGUMENTS.get('VERSION', '')
        if not self.version:
            self.version = self.default_version

        if BuildCommandLine.git:
            cmd = "%s ls-files 2> /dev/null" % BuildCommandLine.git
            with os.popen(cmd, "r") as p:
                self.git_status_lines = p.readlines()

        self.revision = ARGUMENTS.get('REVISION', '')

        def _generate_build_id(revision):
            return revision

        generate_build_id=_generate_build_id

        if not self.revision and BuildCommandLine.git:
            with os.popen("%s rev-parse HEAD 2> /dev/null" % BuildCommandLine.git, "r") as p:
                self.git_hash = p.read().strip()

            def _generate_build_id_git(revision):
                result = self.git_hash
                if [l for l in self.git_status_lines if 'modified' in l]:
                    result = result + '[MODIFIED]'
                return result

            generate_build_id = _generate_build_id_git
            self.revision = self.git_hash

        self.checkpoint = ARGUMENTS.get('CHECKPOINT', '')
        if self.checkpoint:
            if self.checkpoint == 'd':
                self.checkpoint = time.strftime('%Y%m%d', time.localtime(time.time()))
            elif self.checkpoint == 'r':
                self.checkpoint = 'r' + self.revision
            self.version = self.version + '.beta.' + self.checkpoint

        self.build_id = ARGUMENTS.get('BUILD_ID')
        if self.build_id is None:
            if self.revision:
                self.build_id = generate_build_id(self.revision)
            else:
                self.build_id = ''

        # Re-exporting LD_LIBRARY_PATH is necessary if the Python version was
        # built with the --enable-shared option.
        self.ENV = {'PATH': os.environ['PATH']}
        for key in ['LOGNAME', 'PYTHONPATH', 'LD_LIBRARY_PATH']:
            if key in os.environ:
                self.ENV[key] = os.environ[key]

        self.build_dir = ARGUMENTS.get('BUILDDIR', 'build')
        if not os.path.isabs(self.build_dir):
            self.build_dir = os.path.normpath(os.path.join(os.getcwd(), self.build_dir))
