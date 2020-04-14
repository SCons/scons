#!/usr/bin/env python
#
# __COPYRIGHT__
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

"""bootstrap.py

Execute SCons from this source tree. It copies Python scripts and modules
from src/ subdirectory into a subdirectory named "bootstrap/" (by default),
and executes SCons from there with the supplied command-line arguments.

This is a minimal build of SCons to bootstrap the full build of all the
packages, as specified in our local SConstruct file.

Some options are specific to this bootstrap.py script and are *not* passed
on to the SCons script. All of these begin with the string "bootstrap_":

    --bootstrap_dir=DIR

        Sets the name of the directory into which the SCons files will
        be copied.  The default is "bootstrap" in the local subdirectory.

    --bootstrap_force

        Forces a copy of all necessary files.  By default, the
        bootstrap.py script only updates the bootstrap copy if the
        content of the source copy is different.

    --bootstrap_src=DIR

        Searches for the SCons files relative to the specified DIR,
        then relative to the directory in which this bootstrap.py
        script is found.

    --bootstrap_update

        Only updates the bootstrap subdirectory, and then exits.

In addition to the above, the bootstrap.py script understands
the following SCons options:

    -C, --directory

        Changes to the specified directory before invoking SCons.
        Because we change directory right away to the specified directory,
        the SCons script itself doesn't need to, so this option gets
        "eaten" by the bootstrap.py script.
"""

import os
import os.path
import sys
import glob
import subprocess
import filecmp
import shutil

def parseManifestLines(basedir, manifest):
    """
    Scans a MANIFEST file, and returns the list of source files.

    Has basic support for recursive globs '**',
    filename wildcards of the form '*.xml' and
    comment lines, starting with a '#'.

    :param basedir: base path to find files in. Note this does not
                    run in an SCons context so path must not need
                    further processing (e.g. no '#' signs)
    :param manifest: path to manifest file
    :returns: list of files
    """
    sources = []
    basewd = os.path.abspath(basedir)
    with open(manifest) as m:
        lines = m.readlines()
    for l in lines:
        if l.startswith('#'):
            # Skip comments
            continue
        l = l.rstrip('\n')
        if l.endswith('**'):
            # Glob all files recursively
            globwd = os.path.dirname(os.path.join(basewd, l))
            for path, dirs, files in os.walk(globwd):
                for f in files:
                    fpath = os.path.join(globwd, path, f)
                    sources.append(os.path.relpath(fpath, basewd))
        elif '*' in l:
            # Glob file pattern
            files = glob.glob(os.path.join(basewd, l))
            for f in files:
                sources.append(os.path.relpath(f, basewd))
        else:
            sources.append(l)

    return sources

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))

    bootstrap_dir = os.path.join(script_dir, 'bootstrap')

    pass_through_args = []
    update_only = None

    requires_an_argument = 'bootstrap.py:  %s requires an argument\n'

    search = [script_dir]

    def find(filename, search=search):
        for dir_name in search:
            filepath = os.path.join(dir_name, filename)
            if os.path.exists(filepath):
                return os.path.normpath(filepath)
        sys.stderr.write("could not find `%s' in search path:\n" % filename)
        sys.stderr.write("\t" + "\n\t".join(search) + "\n")
        sys.exit(2)

    def must_copy(dst, src):
        if not os.path.exists(dst):
            return 1
        return not filecmp.cmp(dst,src)

    # Note:  We don't use the getopt module to process the command-line
    # arguments because we'd have to teach it about all of the SCons options.

    command_line_args = sys.argv[1:]

    while command_line_args:
        arg = command_line_args.pop(0)

        if arg == '--bootstrap_dir':
            try:
                bootstrap_dir = command_line_args.pop(0)
            except IndexError:
                sys.stderr.write(requires_an_argument % arg)
                sys.exit(1)
        elif arg[:16] == '--bootstrap_dir=':
            bootstrap_dir = arg[16:]
        elif arg == '--bootstrap_force':
            def must_copy(dst, src):
                return 1
        elif arg == '--bootstrap_src':
            try:
                search.insert(0, command_line_args.pop(0))
            except IndexError:
                sys.stderr.write(requires_an_argument % arg)
                sys.exit(1)
        elif arg[:16] == '--bootstrap_src=':
            search.insert(0, arg[16:])
        elif arg == '--bootstrap_update':
            update_only = 1
        elif arg in ('-C', '--directory'):
            try:
                dir = command_line_args.pop(0)
            except IndexError:
                sys.stderr.write(requires_an_argument % arg)
                sys.exit(1)
            else:
                os.chdir(dir)
        elif arg[:2] == '-C':
            os.chdir(arg[2:])
        elif arg[:12] == '--directory=':
            os.chdir(arg[12:])
        else:
            pass_through_args.append(arg)

    scons_py = os.path.join('scripts', 'scons.py')
    src_engine = os.path.join('src', 'engine')
    MANIFEST_in = find(os.path.join(src_engine, 'MANIFEST.in'))
    manifest_files = [os.path.join(src_engine, x)
                      for x in parseManifestLines(os.path.join(script_dir, src_engine),
                                                  MANIFEST_in)]

    files = [scons_py] + manifest_files

    for filename in files:
        src = find(filename)
        dst = os.path.join(bootstrap_dir, filename)
        if must_copy(dst, src):
            dir = os.path.split(dst)[0]
            if not os.path.isdir(dir):
                os.makedirs(dir)
            try:
                os.unlink(dst)
            except Exception as e:
                pass

            shutil.copyfile(src, dst)

    if update_only:
        sys.exit(0)

    args = [sys.executable, os.path.join(bootstrap_dir, scons_py)] + pass_through_args

    sys.stdout.write(" ".join(args) + '\n')
    sys.stdout.flush()

    os.environ['SCONS_LIB_DIR'] = os.path.join(bootstrap_dir, src_engine)

    sys.exit(subprocess.Popen(args, env=os.environ).wait())


if __name__ == "__main__":
    print("Please use")
    print("python scripts/scons.py")
    print("Instead of python bootstrap.py. Bootstrap.py is obsolete")
    sys.exit(-1)
    main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
