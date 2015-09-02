"""SCons.Tool.cyglink

Customization of gnulink for Cygwin (http://www.cygwin.com/)

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""
import re
import os

import SCons.Action
import SCons.Util
import SCons.Tool

import gnulink

def _lib_generator(target, source, env, for_signature, **kw):
    try: cmd = kw['cmd']
    except KeyError: cmd = SCons.Util.CLVar(['$SHLINK']) 

    try: vp = kw['varprefix']
    except KeyError: vp = 'SHLIB'

    dll = env.FindIxes(target, '%sPREFIX' % vp, '%sSUFFIX' % vp)
    if dll: cmd.extend(['-o', dll])

    cmd.extend(['$SHLINKFLAGS', '$__%sVERSIONFLAGS' % vp, '$__RPATH'])

    implib = env.FindIxes(target, 'IMPLIBPREFIX', 'IMPLIBSUFFIX')
    if implib:
        cmd.extend([
            '-Wl,--out-implib='+implib.get_string(for_signature),
            '-Wl,--export-all-symbols',
            '-Wl,--enable-auto-import',
            '-Wl,--whole-archive', '$SOURCES',
            '-Wl,--no-whole-archive', '$_LIBDIRFLAGS', '$_LIBFLAGS'
            ])
    else:
        cmd.extend(['$SOURCES', '$_LIBDIRFLAGS', '$_LIBFLAGS'])
    
    return [cmd]


def shlib_generator(target, source, env, for_signature):
    return _lib_generator(target, source, env, for_signature,
                          varprefix='SHLIB',
                          cmd = SCons.Util.CLVar(['$SHLINK']))

def ldmod_generator(target, source, env, for_signature):
    return _lib_generator(target, source, env, for_signature,
                          varprefix='LDMODULE',
                          cmd = SCons.Util.CLVar(['$LDMODULE']))

def _lib_emitter(target, source, env, **kw):
    Verbose = False

    try: vp = kw['varprefix']
    except KeyError: vp = 'SHLIB'

    try: libtype = kw['libtype']
    except KeyError: libtype = 'ShLib'
        
    dll = env.FindIxes(target, '%sPREFIX' % vp, '%sSUFFIX' % vp)
    no_import_lib = env.get('no_import_lib', 0)

    if not dll or len(target) > 1:
        raise SCons.Errors.UserError("A shared library should have exactly one target with the suffix: %s" % env.subst("$%sSUFFIX" % vp))
    
    # Remove any "lib" after the prefix
    pre = env.subst('$%sPREFIX' % vp)
    if dll.name[len(pre):len(pre)+3] == 'lib':
        dll.name = pre + dll.name[len(pre)+3:]

    orig_target = target
    target = [env.fs.File(dll)]
    target[0].attributes.shared = 1

    # Append an import lib target
    if not no_import_lib:
        # Create list of target libraries as strings
        target_strings = env.ReplaceIxes(orig_target[0],
                                         '%sPREFIX' % vp, '%sSUFFIX' % vp,
                                         'IMPLIBPREFIX', 'IMPLIBSUFFIX')
        
        implib_target = env.fs.File(target_strings)
        if Verbose:
            print "_lib_emitter: implib_target=%r" % str(implib_target) 
        implib_target.attributes.shared = 1
        target.append(implib_target)

    symlinks = SCons.Tool.ImpLibSymlinkGenerator(env, implib_target,
                                                 implib_libtype=libtype,
                                                 generator_libtype=libtype+'ImpLib')
    if Verbose:
        print "_lib_emitter: implib symlinks=%r" % symlinks
    if symlinks:
        SCons.Tool.EmitLibSymlinks(env, symlinks, implib_target)
        implib_target.attributes.shliblinks = symlinks

    return (target, source)

def shlib_emitter(target, source, env):
    return _lib_emitter(target, source, env, varprefix='SHLIB', libtype='ShLib')

def ldmod_emitter(target, source, env):
    return _lib_emitter(target, source, env, varprefix='LDMODULE', libtype='LdMod')
                         
def _versioned_lib_suffix(env, suffix, version):
    """Generate versioned shared library suffix from a unversioned one.
       If suffix='.dll', and version='0.1.2', then it returns '-0-1-2.dll'"""
    Verbose = False
    if Verbose:
        print "_versioned_lib_suffix: suffix= ", suffix
        print "_versioned_lib_suffix: version= ", version
    cygversion = re.sub('\.', '-', version)
    if not suffix.startswith('-' + cygversion):
        suffix = '-' + cygversion + suffix
    if Verbose:
        print "_versioned_lib_suffix: return suffix= ", suffix
    return suffix

def _versioned_implib_name(env, libnode, version, suffix, **kw):
    import link
    generator = SCons.Tool.ImpLibSuffixGenerator
    libtype = kw['libtype']
    return link._versioned_lib_name(env, libnode, version, suffix, generator, implib_libtype=libtype)

def _versioned_implib_symlinks(env, libnode, version, suffix, **kw):
    """Generate link names that should be created for a versioned shared lirbrary.
       Returns a dictionary in the form { linkname : linktarget }
    """
    Verbose = False

    if Verbose:
        print "_versioned_implib_symlinks: str(libnode)=%r" % str(libnode)
        print "_versioned_implib_symlinks: version=%r" % version

    try: libtype = kw['libtype']
    except KeyError: libtype = 'ShLib'

    symlinks = {}

    linkdir = os.path.dirname(str(libnode))
    if Verbose:
        print "_versioned_implib_symlinks: linkdir=%r" % linkdir

    name = SCons.Tool.ImpLibNameGenerator(env, libnode,
                                          implib_libtype=libtype,
                                          generator_libtype=libtype+'ImpLib')
    if Verbose:
        print "_versioned_implib_symlinks: name=%r" % name

    major = version.split('.')[0]

    link0 = os.path.join(str(linkdir), name)

    symlinks[link0] = str(libnode)

    if Verbose:
        print "_versioned_implib_symlinks: return symlinks=%r" % symlinks

    return symlinks

shlib_action = SCons.Action.Action(shlib_generator, generator=1)
ldmod_action = SCons.Action.Action(ldmod_generator, generator=1)

def generate(env):
    """Add Builders and construction variables for cyglink to an Environment."""
    gnulink.generate(env)

    env['LINKFLAGS']   = SCons.Util.CLVar('-Wl,-no-undefined')

    env['SHLINKCOM'] = shlib_action
    env['LDMODULECOM'] = ldmod_action
    env.Append(SHLIBEMITTER = [shlib_emitter])
    env.Append(LDMODULEEMITTER = [ldmod_emitter])

    env['SHLIBPREFIX']         = 'cyg'
    env['SHLIBSUFFIX']         = '.dll'

    env['IMPLIBPREFIX']        = 'lib'
    env['IMPLIBSUFFIX']        = '.dll.a'

    # Variables used by versioned shared libraries
    env['_SHLIBVERSIONFLAGS']      = '$SHLIBVERSIONFLAGS'
    env['_LDMODULEVERSIONFLAGS']   = '$LDMODULEVERSIONFLAGS'

    # SHLIBVERSIONFLAGS and LDMODULEVERSIONFLAGS are same as in gnulink...

    env['GenerateVersionedShLibSuffix']          = _versioned_lib_suffix
    env['GenerateVersionedLdModSuffix']          = _versioned_lib_suffix
    env['GenerateVersionedImpLibSuffix']         = _versioned_lib_suffix
    env['GenerateVersionedShLibImpLibName']      = lambda *args: _versioned_implib_name(*args, libtype='ShLib')
    env['GenerateVersionedLdModImpLibName']      = lambda *args: _versioned_implib_name(*args, libtype='LdMod')
    env['GenerateVersionedShLibImpLibSymlinks']  = lambda *args: _versioned_implib_symlinks(*args, libtype='ShLib')
    env['GenerateVersionedLdModImpLibSymlinks']  = lambda *args: _versioned_implib_symlinks(*args, libtype='LdMod')

    def trydel(env, key):
        try: del env[key]
        except KeyError: pass

    # these variables were set by gnulink but are not used in cyglink
    trydel(env,'_SHLINKSONAME')
    trydel(env,'_LDMODULESONAME')
    trydel(env,'ShLibSonameGenerator')
    trydel(env,'LdModSonameGenerator')
    trydel(env,'GenerateVersionedShLibSymlinks')
    trydel(env,'GenerateVersionedLdModSymlinks')
    trydel(env,'GenerateVersionedShLibSoname')
    trydel(env,'GenerateVersionedLdModSoname')

def exists(env):
    return gnulink.exists(env)


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
