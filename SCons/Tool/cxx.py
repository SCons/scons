"""SCons.Tool.c++

Tool-specific initialization for generic Posix C++ compilers.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

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

import os.path
import re

import SCons.Defaults
import SCons.Util

compilers = ['CC', 'c++']

CXXSuffixes = ['.cpp', '.cc', '.cxx', '.c++', '.C++', '.mm']
if SCons.Util.case_sensitive_suffixes('.c', '.C'):
    CXXSuffixes.append('.C')

def iscplusplus(source):
    if not source:
        # Source might be None for unusual cases like SConf.
        return 0
    for s in source:
        if s.sources:
            ext = os.path.splitext(str(s.sources[0]))[1]
            if ext in CXXSuffixes:
                return 1
    return 0

def gen_module_map_file(root, module_map):
    module_map_text = '$$root ' + str(root) + '\n'
    for module, file in module_map.items():
        module_map_text += str(module) + ' ' + str(file) + '\n'
    return module_map_text

#TODO filter out C++ whitespace and comments
module_decl_re = re.compile("(module;)?(.|\n)*export module (.*);");

def module_emitter(target, source, env):
    if("CXXMODULEPATH" in env):
        if("CXXMAPFILE" not in env):
            env["CXXMAPFILE"] = env.Textfile("$CXXMODULEPATH/module.map", gen_module_map_file(env["CXXMODULEPATH"], env.get("CXXMODULEMAP", {})))

        env.Depends(target, env["CXXMAPFILE"])

        export = module_decl_re.match(source[0].get_text_contents())
        if export:
            modulename = export[3].strip()
            if modulename not in env["CXXMODULEMAP"]:
                env["CXXMODULEMAP"][modulename] = modulename + env["CXXMODULESUFFIX"]
            target.append(env.File("$CXXMODULEPATH/" + env["CXXMODULEMAP"][modulename]))
    return (target, source, env)

def module_emitter_static(target, source, env):
    import SCons.Defaults
    return SCons.Defaults.StaticObjectEmitter(*module_emitter(target, source, env))

def module_emitter_shared(target, source, env):
    import SCons.Defaults
    return SCons.Defaults.SharedObjectEmitter(*module_emitter(target, source, env))

def generate(env):
    """
    Add Builders and construction variables for Visual Age C++ compilers
    to an Environment.
    """
    import SCons.Tool
    import SCons.Tool.cc
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in CXXSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)
        static_obj.add_emitter(suffix, module_emitter_static)
        shared_obj.add_emitter(suffix, module_emitter_shared)

    SCons.Tool.cc.add_common_cc_variables(env)

    if 'CXX' not in env:
        env['CXX']    = env.Detect(compilers) or compilers[0]
    env['CXXFLAGS']   = SCons.Util.CLVar('')
    env['CXXCOM']     = '$CXX -o $TARGET -c ${ CXXMODULEFLAGS if CXXMODULEPATH else "" } $CXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
    env['SHCXX']      = '$CXX'
    env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    env['SHCXXCOM']   = '$SHCXX -o $TARGET -c ${ CXXMODULEFLAGS if CXXMODULEPATH else "" } $SHCXXFLAGS $SHCCFLAGS $_CCCOMCOM $SOURCES'

    env['CPPDEFPREFIX']  = '-D'
    env['CPPDEFSUFFIX']  = ''
    env['INCPREFIX']  = '-I'
    env['INCSUFFIX']  = ''
    env['SHOBJSUFFIX'] = '.os'
    env['OBJSUFFIX'] = '.o'
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 0

    env['CXXFILESUFFIX'] = '.cc'

def exists(env):
    return env.Detect(env.get('CXX', compilers))

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
