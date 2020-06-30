# flake8: noqa
import os.path

from SConsRevision import SCons_revision
from Utilities import is_windows, whereis, platform, deb_date
# from zip_utils import unzipit, zipit, zcat
from soe_utils import soelim, soscan, soelimbuilder
# from epydoc import epydoc_cli, epydoc_commands
from BuildCommandLine import BuildCommandLine
from scons_local_package import install_local_package_files, create_local_packages
from update_build_info import update_init_file

gzip = whereis('gzip')
git = os.path.exists('.git') and whereis('git')
unzip = whereis('unzip')
zip_path = whereis('zip')

BuildCommandLine.git = git