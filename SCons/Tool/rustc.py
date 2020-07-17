"""SCons.Tool.rustc

Tool-specific initialization for the rustc compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

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

import SCons.Defaults
import SCons.Tool
import subprocess
import shlex


def _rust_library_dict_to_list(library_dict):
    return [
        name if kind is None else '{}={}'.format(kind, name)
        for name, kind in library_dict.items()
    ]

def _Crate(env, target, source, type='bin', name=None, *args, **kwargs):
    if name is None:
        name = target
    return env.Command(
        target,
        source,
        (
            '$RUSTC '
            '$_RUSTCODEGENFLAGS '
            '$_RUSTLIBFLAGS '
            '$_RUSTLINTFLAGS '
            '$RUSTFLAGS '
            '--crate-type $CRATE_TYPE '
            '--crate-name $CRATE_NAME '
            '-o $TARGET '
            '$SOURCES'
        ),
        CRATE_TYPE=type,
        CRATE_NAME=name,
        *args,
        **kwargs,
    )

def generate(env):
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in SCons.Tool.RustSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.RustAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)

        shared_obj.add_action(suffix, SCons.Defaults.ShRustAction)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)

    env['RUSTC'] = env.Detect('rustc') or 'rustc'
    env['RUSTCOM'] = '$RUSTC $_RUSTCODEGENFLAGS $_RUSTLIBFLAGS $_RUSTLINTFLAGS $RUSTFLAGS --crate-type staticlib --emit obj -o $TARGET $SOURCES'
    env['RUSTFLAGS'] = []

    env['SHRUSTC'] = '$RUSTC'
    env['SHRUSTCOM'] = '$SHRUSTC $_RUSTCODEGENFLAGS $_RUSTLIBFLAGS $_RUSTLINTFLAGS $SHRUSTFLAGS --crate-type cdylib --emit obj -o $TARGET $SOURCES'
    env['SHRUSTFLAGS'] = []

    env['RUSTCODEGENPREFIX'] = '-C'
    env['RUSTCODEGENFLAGS'] = {
        'linker': '$LINK',
        'link-args': '$LINKFLAGS',
    }
    env['_RUSTCODEGENFLAGS'] = '${_defines(RUSTCODEGENPREFIX, RUSTCODEGENFLAGS, "", __env__)}'

    env['_rust_library_dict_to_list'] = _rust_library_dict_to_list
    env['RUSTLIBPATHPREFIX'] = '-L'
    env['RUSTLIBPATH'] = dict()
    env['RUSTLIBSPREFIX'] = '-l'
    env['RUSTLIBS'] = dict()
    env['_RUSTLIBFLAGS'] = (
        '${_concat(RUSTLIBPATHPREFIX, _rust_library_dict_to_list(RUSTLIBPATH), "", __env__)} '
        '${_concat(RUSTLIBSPREFIX, _rust_library_dict_to_list(RUSTLIBS), "", __env__)}'
    )

    # Automatically append stdlib
    # TODO: Evaluate lazily
    libdir_command = env.subst('$RUSTC $_RUSTCODEGENFLAGS $_RUSTLIBFLAGS $_RUSTLINTFLAGS $RUSTFLAGS --print=target-libdir')
    libdir = subprocess.run(shlex.split(libdir_command), stdout=subprocess.PIPE).stdout.decode().strip('\n')
    env.Append(LIBS=env.Glob(libdir + "/libstd-*$SHLIBSUFFIX"))

    env['RUSTLINTWARNPREFIX'] = '-W'
    env['RUSTLINTWARN'] = []
    env['RUSTLINTALLOWPREFIX'] = '-A'
    env['RUSTLINTALLOW'] = []
    env['RUSTLINTDENYPREFIX'] = '-D'
    env['RUSTLINTDENY'] = []
    env['RUSTLINTFORBIDPREFIX'] = '-F'
    env['RUSTLINTFORBID'] = []
    env['_RUSTLINTFLAGS'] = (
        '${_concat(RUSTLINTWARNPREFIX, RUSTLINTWARN, "", __env__)} '
        '${_concat(RUSTLINTALLOWPREFIX, RUSTLINTALLOW, "", __env__)} '
        '${_concat(RUSTLINTDENYPREFIX, RUSTLINTDENY, "", __env__)} '
        '${_concat(RUSTLINTFORBIDPREFIX, RUSTLINTFORBID, "", __env__)}'
    )

    env.AddMethod(_Crate, "Crate")

def exists(env):
    return env.Detect('rustc')
