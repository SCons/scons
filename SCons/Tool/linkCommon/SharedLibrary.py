from SCons.Errors import UserError
from SCons.Tool import createSharedLibBuilder
from SCons.Util import CLVar
from . import lib_emitter, EmitLibSymlinks, StringizeLibSymlinks


def shlib_symlink_emitter(target, source, env, **kw):
    verbose = False

    if "variable_prefix" in kw:
        var_prefix = kw["variable_prefix"]
    else:
        var_prefix = "SHLIB"

    do_symlinks = env.subst("$%sNOVERSIONSYMLINKS" % var_prefix)
    if do_symlinks in ["1", "True", "true", True]:
        return target, source

    shlibversion = env.subst("$%sVERSION" % var_prefix)
    if shlibversion:
        if verbose:
            print("shlib_symlink_emitter: %sVERSION=%s" % (var_prefix, shlibversion))

        libnode = target[0]
        shlib_soname_symlink = env.subst(
            "$%s_SONAME_SYMLINK" % var_prefix, target=target, source=source
        )
        shlib_noversion_symlink = env.subst(
            "$%s_NOVERSION_SYMLINK" % var_prefix, target=target, source=source
        )

        if verbose:
            print("shlib_soname_symlink    :%s" % shlib_soname_symlink)
            print("shlib_noversion_symlink :%s" % shlib_noversion_symlink)
            print("libnode                 :%s" % libnode)

        shlib_soname_symlink = env.File(shlib_soname_symlink)
        shlib_noversion_symlink = env.File(shlib_noversion_symlink)

        symlinks = []
        if shlib_soname_symlink != libnode:
            # If soname and library name machine, don't symlink them together
            symlinks.append((env.File(shlib_soname_symlink), libnode))
        
        symlinks.append((env.File(shlib_noversion_symlink), libnode))

        if verbose:
            print(
                "_lib_emitter: symlinks={!r}".format(
                    ", ".join(
                        ["%r->%r" % (k, v) for k, v in StringizeLibSymlinks(symlinks)]
                    )
                )
            )

        if symlinks:
            # This does the actual symlinking
            EmitLibSymlinks(env, symlinks, target[0])

            # This saves the information so if the versioned shared library is installed
            # it can faithfully reproduce the correct symlinks
            target[0].attributes.shliblinks = symlinks

    return target, source


def _soversion(target, source, env, for_signature):
    """Function to determine what to use for SOVERSION"""

    if "SOVERSION" in env:
        return ".$SOVERSION"
    elif "SHLIBVERSION" in env:
        shlibversion = env.subst("$SHLIBVERSION")
        # We use only the most significant digit of SHLIBVERSION
        return "." + shlibversion.split(".")[0]
    else:
        return ""


def _soname(target, source, env, for_signature):
    if "SONAME" in env:
        # Now verify that SOVERSION is not also set as that is not allowed
        if "SOVERSION" in env:
            raise UserError(
                "Ambiguous library .so naming, both SONAME: %s and SOVERSION: %s are defined. "
                "Only one can be defined for a target library."
                % (env["SONAME"], env["SOVERSION"])
            )
        return "$SONAME"
    else:
        return "$SHLIBPREFIX$_get_shlib_stem${SHLIBSUFFIX}$_SHLIBSOVERSION"


def _get_shlib_stem(target, source, env, for_signature):
    """
    Get the basename for a library (so for libxyz.so, return xyz)
    :param target:
    :param source:
    :param env:
    :param for_signature:
    :return:
    """
    verbose = True

    target_name = str(target.name)
    shlibprefix = env.subst("$SHLIBPREFIX")
    shlibsuffix = env.subst("$_SHLIBSUFFIX")

    if verbose and not for_signature:
        print(
            "_get_shlib_stem: target_name:%s shlibprefix:%s shlibsuffix:%s"
            % (target_name, shlibprefix, shlibsuffix)
        )

    if target_name.startswith(shlibprefix):
        target_name = target_name[len(shlibprefix) :]

    if target_name.endswith(shlibsuffix):
        target_name = target_name[: -len(shlibsuffix)]

    if verbose and not for_signature:
        print("_get_shlib_stem: target_name:%s AFTER" % (target_name,))

    return target_name


def _get_shlib_dir(target, source, env, for_signature):
    """
    Get the directory the shlib is in.
    """
    if target.dir and str(target.dir) != ".":
        print("target.dir:%s" % target.dir)
        return "%s/" % str(target.dir)
    else:
        return ""


def setup_shared_lib_logic(env):
    """
    Just the logic for shared libraries
    :param env:
    :return:
    """
    createSharedLibBuilder(env)

    env["_get_shlib_stem"] = _get_shlib_stem
    env["_get_shlib_dir"] = _get_shlib_dir
    env["_SHLIBSOVERSION"] = _soversion
    env["_SHLIBSONAME"] = _soname

    env["SHLIBNAME"] = "${_get_shlib_dir}${SHLIBPREFIX}$_get_shlib_stem${_SHLIBSUFFIX}"

    # This is the non versioned shlib filename
    # If SHLIBVERSION is defined then this will symlink to $SHLIBNAME
    env[
        "SHLIB_NOVERSION_SYMLINK"
    ] = "${_get_shlib_dir}${SHLIBPREFIX}$_get_shlib_stem${SHLIBSUFFIX}"

    # This is the sonamed file name
    # If SHLIBVERSION is defined then this will symlink to $SHLIBNAME
    env["SHLIB_SONAME_SYMLINK"] = "${_get_shlib_dir}$_SHLIBSONAME"

    # Note this is gnu style
    env["SHLIBSONAMEFLAGS"] = "-Wl,-soname=$_SHLIBSONAME"
    env["_SHLIBVERSION"] = "${SHLIBVERSION and '.'+SHLIBVERSION or ''}"
    env["_SHLIBVERSIONFLAGS"] = "$SHLIBVERSIONFLAGS -Wl,-soname=$_SHLIBSONAME"

    env["SHLIBEMITTER"] = [lib_emitter, shlib_symlink_emitter]

    env["SHLIBPREFIX"] = "lib"
    env["_SHLIBSUFFIX"] = "${SHLIBSUFFIX}${_SHLIBVERSION}"

    env["SHLINKFLAGS"] = CLVar("$LINKFLAGS -shared")

    env[
        "SHLINKCOM"
    ] = "$SHLINK -o $TARGET $SHLINKFLAGS $__SHLIBVERSIONFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS"
    env["SHLINKCOMSTR"] = "$SHLINKCOM"
    env["SHLINK"] = "$LINK"
