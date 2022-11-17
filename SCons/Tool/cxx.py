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
import SCons.Scanner

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
module_decl_re = re.compile("(module;)?(.|\n)*export module (.*);")

def module_emitter(target, source, env):
    if("CXXMODULEPATH" in env):
        env["__CXXMODULEINIT__"](env)

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

#TODO filter out C++ whitespace and comments
module_import_re = re.compile(r"\s*(?:(?:export)?\s*import\s*(\S*)\s*;)|(?:(export)?\s*module\s*(\S*)\s*;)")


class CxxModuleScanner(SCons.Scanner.Current):
    def scan(self, node, env, path):
        result = self.c_scanner(node, env, path)

        if not env.get("CXXMODULEPATH"):
            return result

        imports = module_import_re.findall(node.get_text_contents())
        for module, export, impl in imports:
            if not module:
                if not export and impl:  # module implementation unit depends on module interface
                    module = impl
                else:
                    continue
            is_header_unit = False
            if(module[0] == "<" or module[0] == '"'):
                module_id_prefix = "@system-header/" if module[0] == "<" else "@header/"
                cmi = module_id_prefix + module[1:-1] + "$CXXMODULESUFFIX"
                is_header_unit = True
            else:
                cmi = env["CXXMODULEMAP"].get(
                    module, module+"$CXXMODULESUFFIX")
            cmi = env.File("$CXXMODULEPATH/" + cmi)

            if(is_header_unit and not cmi.has_builder()):
                source = self.c_scanner.find_include(
                    (module[0], module[1:-1]), node.dir, path)
                if source[0]:
                    source = source[0]
                else:
                    source = env.Value(module[1:-1])
                env.CxxHeaderUnit(
                    cmi, source,
                    CXXCOMOUTPUTSPEC="$CXXSYSTEMHEADERFLAGS" if module[0] == "<" else "$CXXUSERHEADERFLAGS",
                    CPPPATH = [node.dir, "$CPPPATH"] if module[0] == '"' else "$CPPPATH",
                    CXXMODULEIDPREFIX=module_id_prefix
                )
            result.append(cmi)
        return result

    def __init__(self, *args, **kwargs):
        from SCons.Scanner import FindPathDirs
        super().__init__(self.scan, recursive = True, path_function = FindPathDirs("CPPPATH"), *args, **kwargs)
        from SCons.Tool import CScanner
        self.c_scanner = CScanner

def generate(env):
    """
    Add Builders and construction variables for Visual Age C++ compilers
    to an Environment.
    """
    import SCons.Tool
    import SCons.Tool.cc
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
    from SCons.Tool import SourceFileScanner

    for suffix in CXXSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)
        static_obj.add_emitter(suffix, module_emitter_static)
        shared_obj.add_emitter(suffix, module_emitter_shared)
        SourceFileScanner.add_scanner(suffix, CxxModuleScanner())

    header_unit = SCons.Builder.Builder(action="$CXXCOM",
                                        source_scanner=CxxModuleScanner())
    env["BUILDERS"]["CxxHeaderUnit"] = header_unit

    SCons.Tool.cc.add_common_cc_variables(env)

    if 'CXX' not in env:
        env['CXX']    = env.Detect(compilers) or compilers[0]
    env['CXXFLAGS']   = SCons.Util.CLVar('')
    env['CXXCOMOUTPUTSPEC'] = '-o $TARGET'
    env['CXXCOM']     = '$CXX $CXXCOMOUTPUTSPEC -c ${ CXXMODULEFLAGS if CXXMODULEPATH else "" } $CXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
    env['CXXMODULEMAP'] = {}
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
