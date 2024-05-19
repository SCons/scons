# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Actions to zip and unzip, for working with SCons release bundles.
Action for creating a zipapp.
"""

import os.path
import zipfile
import zipapp


def zipit(env, target, source):
    """Action function to zip *source* into *target*

    Values extracted from *env*:
      *CD*: the directory to work in
      *PSV*: the directory name to walk down to find the files
    """
    print(f"Zipping {target[0]}:")

    def visit(arg, dirname, filenames):
        for filename in filenames:
            path = os.path.join(dirname, filename)
            if os.path.isfile(path):
                arg.write(path)

    # default ZipFile compression is ZIP_STORED
    zf = zipfile.ZipFile(str(target[0]), 'w', compression=zipfile.ZIP_DEFLATED)
    olddir = os.getcwd()
    os.chdir(env.Dir(env['CD']).abspath)
    try:
        for dirname, dirnames, filenames in os.walk(env['PSV']):
            visit(zf, dirname, filenames)
    finally:
        os.chdir(olddir)
    zf.close()


def unzipit(env, target, source):
    """Action function to unzip *source*"""

    print(f"Unzipping {source[0]}:")
    zf = zipfile.ZipFile(str(source[0]), 'r')
    for name in zf.namelist():
        dest = os.path.join(env['UNPACK_ZIP_DIR'], name)
        dir = os.path.dirname(dest)
        os.makedirs(dir, exist_ok=True)
        print(dest, name)
        # if the file exists, then delete it before writing
        # to it so that we don't end up trying to write to a symlink:
        if os.path.isfile(dest) or os.path.islink(dest):
            os.unlink(dest)
        if not os.path.isdir(dest):
            with open(dest, 'wb') as fp:
                fp.write(zf.read(name))


def zipappit(env, target, source):
    """Action function to Create a zipapp *target* from specified directory.

    Values extracted from *env*:
      *CD*: the Dir node for the place we want to work.
      *PSV*: the directory name to point :meth:`zipapp.create_archive` at
        (note *source* is unused here in favor of PSV)
      *main*: the entry point for the zipapp
    """
    print(f"Creating zipapp {target[0]}:")
    dest = target[0].abspath
    olddir = os.getcwd()
    os.chdir(env['CD'].abspath)
    try:
        zipapp.create_archive(
            source=env['PSV'],
            target=dest,
            main=env['entry'],
            interpreter="/usr/bin/env python",
        )
    finally:
        os.chdir(olddir)
