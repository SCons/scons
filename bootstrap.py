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
#

import os
import os.path
import string
import sys

__doc__ = """bootstrap.py

This script supports "bootstrap" execution of the current SCons in
this local source tree by copying of all necessary Python scripts and
modules from underneath the src/ subdirectory into a subdirectory (named
"bootstrap/" by default), and then executing the copied SCons with the
supplied command-line arguments.

There are a handful of options that are specific to this bootstrap.py
script and which are *not* passed on to the underlying SCons script.
All of these begin with the string "bootstrap_":

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

In addition to the above options, the bootstrap.py script understands
the following SCons options:

    -C, --directory

        Changes to the specified directory before invoking SCons.
        Because we change directory right away to the specified directory,
        the SCons script itself doesn't need to, so this option gets
        "eaten" by the bootstrap.py script.

    -Y, --repository

        These options are used under Aegis to specify a search path
        for the source files that may not have been copied in to the
        Aegis change.

This is essentially a minimal build of SCons to bootstrap ourselves into
executing it for the full build of all the packages, as specified in our
local SConstruct file.
"""

try:
    script_dir = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # Pre-2.3 versions of Python don't have __file__.
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

bootstrap_dir = os.path.join(script_dir, 'bootstrap')

pass_through_args = []
update_only = None

requires_an_argument = 'bootstrap.py:  %s requires an argument\n'

def must_copy(dst, src):
    if not os.path.exists(dst):
        return 1
    return open(dst, 'rb').read() != open(src, 'rb').read()

search = [script_dir]

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

    elif arg in ('-Y', '--repository'):
        try:
            dir = command_line_args.pop(0)
        except IndexError:
            sys.stderr.write(requires_an_argument % arg)
            sys.exit(1)
        else:
            search.append(dir)
        pass_through_args.extend([arg, dir])
    elif arg[:2] == '-Y':
        search.append(arg[2:])
        pass_through_args.append(arg)
    elif arg[:13] == '--repository=':
        search.append(arg[13:])
        pass_through_args.append(arg)

    else:
        pass_through_args.append(arg)

def find(file, search=search):
    for dir in search:
        f = os.path.join(dir, file)
        if os.path.exists(f):
            return os.path.normpath(f)
    sys.stderr.write("could not find `%s' in search path:\n" % file)
    sys.stderr.write("\t" + string.join(search, "\n\t") + "\n")
    sys.exit(2)

scons_py = os.path.join('src', 'script', 'scons.py')
src_engine = os.path.join('src', 'engine')
MANIFEST_in = find(os.path.join(src_engine, 'MANIFEST.in'))

files = [ scons_py ] + map(lambda x: os.path.join(src_engine, x[:-1]),
                           open(MANIFEST_in).readlines())

for file in files:
    src = find(file)
    dst = os.path.join(bootstrap_dir, file)
    if must_copy(dst, src):
        dir = os.path.split(dst)[0]
        if not os.path.isdir(dir):
            os.makedirs(dir)
        try: os.unlink(dst)
        except: pass
        open(dst, 'wb').write( open(src, 'rb').read() )

if update_only:
    sys.exit(0)

args = [
            sys.executable,
            os.path.join(bootstrap_dir, scons_py)
       ] + pass_through_args

sys.stdout.write(string.join(args, " ") + '\n')
sys.stdout.flush()

os.environ['SCONS_LIB_DIR'] = os.path.join(bootstrap_dir, src_engine)

os.execve(sys.executable, args, os.environ)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
