from SCons.Tool import createLoadableModuleBuilder
from .SharedLibrary import shlib_symlink_emitter
from . import lib_emitter


def ldmod_symlink_emitter(target, source, env, **kw):
    return shlib_symlink_emitter(target, source, env, variable_prefix='LDMODULE')


def _get_ldmodule_stem(target, source, env, for_signature):
    """
    Get the basename for a library (so for libxyz.so, return xyz)
    :param target:
    :param source:
    :param env:
    :param for_signature:
    :return:
    """
    target_name = str(target)
    ldmodule_prefix = env.subst('$LDMODULEPREFIX')
    ldmodule_suffix = env.subst("$_LDMODULESUFFIX")

    if target_name.startswith(ldmodule_prefix):
        target_name = target_name[len(ldmodule_prefix):]

    if target_name.endswith(ldmodule_suffix):
        target_name = target_name[:-len(ldmodule_suffix)]

    return target_name


def _ldmodule_soversion(target, source, env, for_signature):
    """Function to determine what to use for SOVERSION"""

    if 'SOVERSION' in env:
        return '.$SOVERSION'
    elif 'LDMODULEVERSION' in env:
        ldmod_version = env.subst('$LDMODULEVERSION')
        # We use only the most significant digit of LDMODULEVERSION
        return '.' + ldmod_version.split('.')[0]
    else:
        return ''


def _ldmodule_soname(target, source, env, for_signature):
    if 'SONAME' in env:
        return '$SONAME'
    else:
        return "$LDMODULEPREFIX$_get_ldmodule_stem$_LDMODULESOVERSION${LDMODULESUFFIX}"


def setup_loadable_module_logic(env):
    """
    Just the logic for loadable modules

    For most platforms, a loadable module is the same as a shared
    library.  Platforms which are different can override these, but
    setting them the same means that LoadableModule works everywhere.

    :param env:
    :return:
    """

    createLoadableModuleBuilder(env)

    env['_get_ldmodule_stem'] = _get_ldmodule_stem
    env['_LDMODULESOVERSION'] = _ldmodule_soversion
    env['_LDMODULESONAME'] = _ldmodule_soname

    env['LDMODULENAME'] = '${LDMODULEPREFIX}$_get_ldmodule_stem${_LDMODULESUFFIX}'

    # This is the non versioned LDMODULE filename
    # If LDMODULEVERSION is defined then this will symlink to $LDMODULENAME
    env['LDMODULE_NOVERSION_SYMLINK'] = '${LDMODULEPREFIX}$_get_ldmodule_stem${LDMODULESUFFIX}'

    # This is the sonamed file name
    # If LDMODULEVERSION is defined then this will symlink to $LDMODULENAME
    env['LDMODULE_SONAME_SYMLINK'] = '$_LDMODULESONAME'

    env['_LDMODULEVERSION'] = "${LDMODULEVERSION and '.'+LDMODULEVERSION or ''}"
    env['_LDMODULEVERSIONFLAGS'] = '$LDMODULEVERSIONFLAGS -Wl,-soname=$_LDMODULESONAME'

    env['LDMODULEEMITTER'] = [lib_emitter, ldmod_symlink_emitter]

    env['LDMODULEPREFIX'] = '$SHLIBPREFIX'
    env['_LDMODULESUFFIX'] = '${_LDMODULEVERSION}${LDMODULESUFFIX}'
    env['LDMODULESUFFIX'] = '$SHLIBSUFFIX'

    env['LDMODULE'] = '$SHLINK'

    env['LDMODULEFLAGS'] = '$SHLINKFLAGS'

    env['LDMODULECOM'] = '$LDMODULE -o $TARGET $LDMODULEFLAGS $__LDMODULEVERSIONFLAGS $__RPATH $SOURCES ' \
                         '$_LIBDIRFLAGS $_LIBFLAGS '

    env['LDMODULEVERSION'] = '$SHLIBVERSION'
    env['LDMODULENOVERSIONSYMLINKS'] = '$SHLIBNOVERSIONSYMLINKS'