# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from glob import glob
import os.path
from zip_utils import zipit, zipappit
from Utilities import is_windows


def get_local_package_file_list():
    """Get list of all files which should be included in scons-local package"""

    s_files = glob("SCons/**", recursive=True)

    # import pdb; pdb.set_trace()

    non_test = [f for f in s_files if "Tests.py" not in f]
    non_test_non_doc = [
        f for f in non_test if '.xml' not in f or "SCons/Tool/docbook" in f
    ]
    filtered_list = [f for f in non_test_non_doc if 'pyc' not in f]
    filtered_list = [f for f in filtered_list if '__pycache__' not in f]
    filtered_list = [f for f in filtered_list if not os.path.isdir(f)]

    return filtered_list


def install_local_package_files(env):

    all_local_installed = []
    files = get_local_package_file_list()
    target_dir = '#/build/scons-local/scons-local-$VERSION'
    for f in files:
        all_local_installed.extend(
            env.Install(os.path.join(target_dir, os.path.dirname(f)), f)
        )

    basedir_files = [
        'scripts/scons.bat',
        'scripts/scons.py',
        'scripts/scons-configure-cache.py',
        'scripts/sconsign.py',
        'bin/scons-time.py',
    ]
    for bf in basedir_files:
        fn = os.path.basename(bf)
        all_local_installed.append(
            env.SCons_revision(f'#/build/scons-local/{fn}', bf)
        )

    # Now copy manpages into scons-local package
    built_manpage_files = env.Glob('build/doc/man/*.1')
    for bmp in built_manpage_files:
        fn = os.path.basename(str(bmp))
        all_local_installed.append(
            env.SCons_revision(f'#/build/scons-local/{fn}', bmp)
        )

    rename_files = [
        ('scons-${VERSION}.bat', 'scripts/scons.bat'),
        ('scons-README', 'README-local'),
        ('scons-LICENSE', 'LICENSE-local'),
    ]
    for t, f in rename_files:
        target_file = f"#/build/scons-local/{t}"
        all_local_installed.append(env.SCons_revision(target_file, f))

    return all_local_installed


def create_local_packages(env):
    [env.Tool(x) for x in ['packaging', 'filesystem', 'zip']]
    installed_files = install_local_package_files(env)

    build_local_dir = 'build/scons-local'
    package = env.Command(
        '#build/dist/scons-local-${VERSION}.zip',
        installed_files,
        zipit,
        CD=build_local_dir,
        PSV='.',
    )

    do_zipapp = True  # Q: maybe an external way to specify whether to build?
    if do_zipapp:
        # We need to descend into the versioned directory for zipapp,
        # but we don't know the version. env.Glob lets us expand that.
        # The action isn't going to use the sources, but including
        # them makes sure SCons has populated the dir we're going to zip.
        app_dir = env.Glob(f"{build_local_dir}/scons-local-*")[0]
        zipapp = env.Command(
            target='#build/dist/scons-local-${VERSION}.pyz',
            source=installed_files,
            action=zipappit,
            CD=app_dir,
            PSV='.',
            entry='SCons.Script.Main:main',
        )

    if is_windows():
        # avoid problem with tar interpreting c:/ as a remote machine
        tar_cargs = '-cz --force-local -f'
    else:
        tar_cargs = '-czf'

    env.Command(
        '#build/dist/scons-local-${VERSION}.tar.gz',
        installed_files,
        "cd %s && tar %s $( ${TARGET.abspath} $) *" % (build_local_dir, tar_cargs),
    )

    print(f"Package:{package}")
    if do_zipapp:
        print(f"Zipapp:{zipapp}")
