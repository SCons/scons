"""SCons.Tool.gcc

Tool-specific initialization for MinGW (http://www.mingw.org/)

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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import os
import SCons.Tool
import SCons.Util
import string

# This is what we search for to find mingw:
key_program = 'mingw32-gcc'

def find(env):
    # First search in the SCons path and then the OS path:
    return env.WhereIs(key_program) or SCons.Util.WhereIs(key_program)

def shlib_generator(target, source, env, for_signature):
    cmd = ['$SHLINK', '$SHLINKFLAGS'] 

    dll = env.FindIxes(target, 'SHLIBPREFIX', 'SHLIBSUFFIX')
    if dll: cmd.extend(['-o', dll])

    cmd.extend(['$SOURCES', '$_LIBDIRFLAGS', '$_LIBFLAGS'])

    implib = env.FindIxes(target, 'LIBPREFIX', 'LIBSUFFIX')
    if implib: cmd.append('-Wl,--out-implib,'+str(implib))

    def_target = env.FindIxes(target, 'WIN32DEFPREFIX', 'WIN32DEFSUFFIX')
    if def_target: cmd.append('-Wl,--output-def,'+str(def_target))

    return [cmd]

def shlib_emitter(target, source, env):
    dll = env.FindIxes(target, 'SHLIBPREFIX', 'SHLIBSUFFIX')
    no_import_lib = env.get('no_import_lib', 0)

    if not dll:
        raise SCons.Errors.UserError, "A shared library should have exactly one target with the suffix: %s" % env.subst("$SHLIBSUFFIX")
    
    if not no_import_lib and \
       not env.FindIxes(target, 'LIBPREFIX', 'LIBSUFFIX'):

        # Append an import library to the list of targets.
        target.append(env.ReplaceIxes(dll,  
                                      'SHLIBPREFIX', 'SHLIBSUFFIX',
                                      'LIBPREFIX', 'LIBSUFFIX'))

    # Append a def file target if there isn't already a def file target
    # or a def file source. There is no option to disable def file
    # target emitting, because I can't figure out why someone would ever
    # want to turn it off.
    def_source = env.FindIxes(source, 'WIN32DEFPREFIX', 'WIN32DEFSUFFIX')
    def_target = env.FindIxes(target, 'WIN32DEFPREFIX', 'WIN32DEFSUFFIX')
    if not def_source and not def_target:
        target.append(env.ReplaceIxes(dll,  
                                      'SHLIBPREFIX', 'SHLIBSUFFIX',
                                      'WIN32DEFPREFIX', 'WIN32DEFSUFFIX'))
    
    return (target, source)
                         

shlib_action = SCons.Action.CommandGenerator(shlib_generator)

res_builder = SCons.Builder.Builder(action='$RCCOM', suffix='.o')

def generate(env, platform):
    
    mingw = find(env)
    if mingw:
        dir = os.path.dirname(mingw)

        # The mingw bin directory must be added to the path:
        path = env['ENV'].get('PATH', [])
        if not path: 
            path = []
        if SCons.Util.is_String(path):
            path = string.split(path, os.pathsep)

        env['ENV']['PATH'] = string.join([dir] + path, os.pathsep)
        

    # Most of mingw is the same as gcc and friends...
    gnu_tools = ['gcc', 'g++', 'gnulink', 'ar', 'gas']
    for tool in gnu_tools:
        SCons.Tool.Tool(tool, platform)(env,platform)

    #... but a few things differ:
    env['CC'] = 'gcc'
    env['SHCCFLAGS'] = '$CCFLAGS'
    env['CXX'] = 'g++'
    env['SHCXXFLAGS'] = '$CXXFLAGS'
    env['SHLINKFLAGS'] = '$LINKFLAGS -shared'
    env['SHLINKCOM']   = shlib_action
    env['SHLIBEMITTER']= shlib_emitter
    env['LINK'] = 'g++'
    env['AS'] = 'as'
    env['WIN32DEFPREFIX']        = ''
    env['WIN32DEFSUFFIX']        = '.def'
    env['SHOBJSUFFIX'] = '.o'
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

    env['RC'] = 'windres'
    env['RCFLAGS'] = ''
    env['RCINCFLAGS'] = '$( ${_concat(RCINCPREFIX, CPPPATH, RCINCSUFFIX, locals(), globals(), RDirs)} $)'
    env['RCINCPREFIX'] = '--include-dir '
    env['RCINCSUFFIX'] = ''
    env['RCCOM'] = '$RC $RCINCFLAGS $RCFLAGS -i $SOURCE -o $TARGET'
    env.CScan.add_skey('.rc')
    env['BUILDERS']['RES'] = res_builder
    
    # Some setting from the platform also have to be overridden:
    env['OBJSUFFIX'] = '.o'
    env['LIBPREFIX'] = 'lib'
    env['LIBSUFFIX'] = '.a'

def exists(env):
    return find(env)
