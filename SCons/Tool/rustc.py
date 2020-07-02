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

def generate(env):
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    static_obj.add_action('.rs', SCons.Defaults.RustAction)
    static_obj.add_emitter('.rs', SCons.Defaults.StaticObjectEmitter)

    env['RUSTC'] = env.Detect('rustc') or 'rustc'
    env['RUSTCOM'] = '$RUSTC $_RUSTCODEGENFLAGS $RUSTFLAGS --crate-type staticlib --emit obj -o $TARGET $SOURCES'
    env['RUSTFLAGS'] = []

    shared_obj.add_action('.rs', SCons.Defaults.ShRustAction)
    shared_obj.add_emitter('.rs', SCons.Defaults.SharedObjectEmitter)

    env['SHRUSTC'] = '$RUSTC'
    env['SHRUSTCOM'] = '$SHRUSTC $_RUSTCODEGENFLAGS $SHRUSTFLAGS --crate-type cdynlib --emit obj -o $TARGET $SOURCES'
    env['SHRUSTFLAGS'] = []

    env['RUSTCODEGENPREFIX'] = '-C'
    env['RUSTCODEGENFLAGS'] = [  # TODO: This should be a dictionary
        'linker=$LINK',
        'link-args=$LINKFLAGS',
    ]
    env['_RUSTCODEGENFLAGS'] = '${_concat(RUSTCODEGENPREFIX, RUSTCODEGENFLAGS, "", __env__)}'

def exists(env):
    return env.Detect('rustc')
