"""SCons.Tool.linkCommon

Common link/shared library logic
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
import os
from typing import Callable
from SCons.Util import is_List


def _call_linker_cb(env, callback, args, result=None):
    """Returns the result of env['LINKCALLBACKS'][callback](*args)
    if env['LINKCALLBACKS'] is a dictionary and env['LINKCALLBACKS'][callback]
    is callable. If these conditions are not met, return the value provided as
    the *result* argument. This function is mainly used for generating library
    info such as versioned suffixes, symlink maps, sonames etc. by delegating
    the core job to callbacks configured by current linker tool"""

    Verbose = False

    if Verbose:
        print('_call_linker_cb: args=%r' % args)
        print('_call_linker_cb: callback=%r' % callback)

    try:
        cbfun = env['LINKCALLBACKS'][callback]
    except (KeyError, TypeError):
        if Verbose:
            print('_call_linker_cb: env["LINKCALLBACKS"][%r] not found or can not be used' % callback)
        pass
    else:
        if Verbose:
            print('_call_linker_cb: env["LINKCALLBACKS"][%r] found' % callback)
            print('_call_linker_cb: env["LINKCALLBACKS"][%r]=%r' % (callback, cbfun))
        if isinstance(cbfun, Callable):
            if Verbose:
                print('_call_linker_cb: env["LINKCALLBACKS"][%r] is callable' % callback)
            result = cbfun(env, *args)
    return result


class _ShLibInfoSupport:
    @property
    def libtype(self):
        return 'ShLib'

    def get_lib_prefix(self, env, *args, **kw):
        return _call_env_subst(env, '$SHLIBPREFIX', *args, **kw)

    def get_lib_suffix(self, env, *args, **kw):
        return _call_env_subst(env, '$SHLIBSUFFIX', *args, **kw)

    def get_lib_version(self, env, *args, **kw):
        return _call_env_subst(env, '$SHLIBVERSION', *args, **kw)

    def get_lib_noversionsymlinks(self, env, *args, **kw):
        return _call_env_subst(env, '$SHLIBNOVERSIONSYMLINKS', *args, **kw)


class _LdModInfoSupport:
    @property
    def libtype(self):
        return 'LdMod'

    def get_lib_prefix(self, env, *args, **kw):
        return _call_env_subst(env, '$LDMODULEPREFIX', *args, **kw)

    def get_lib_suffix(self, env, *args, **kw):
        return _call_env_subst(env, '$LDMODULESUFFIX', *args, **kw)

    def get_lib_version(self, env, *args, **kw):
        return _call_env_subst(env, '$LDMODULEVERSION', *args, **kw)

    def get_lib_noversionsymlinks(self, env, *args, **kw):
        return _call_env_subst(env, '$LDMODULENOVERSIONSYMLINKS', *args, **kw)


class _ImpLibInfoSupport:
    @property
    def libtype(self):
        return 'ImpLib'

    def get_lib_prefix(self, env, *args, **kw):
        return _call_env_subst(env, '$IMPLIBPREFIX', *args, **kw)

    def get_lib_suffix(self, env, *args, **kw):
        return _call_env_subst(env, '$IMPLIBSUFFIX', *args, **kw)

    def get_lib_version(self, env, *args, **kw):
        version = _call_env_subst(env, '$IMPLIBVERSION', *args, **kw)
        if not version:
            try:
                lt = kw['implib_libtype']
            except KeyError:
                pass
            else:
                if lt == 'ShLib':
                    version = _call_env_subst(env, '$SHLIBVERSION', *args, **kw)
                elif lt == 'LdMod':
                    version = _call_env_subst(env, '$LDMODULEVERSION', *args, **kw)
        return version

    def get_lib_noversionsymlinks(self, env, *args, **kw):
        disable = None
        try:
            env['IMPLIBNOVERSIONSYMLINKS']
        except KeyError:
            try:
                lt = kw['implib_libtype']
            except KeyError:
                pass
            else:
                if lt == 'ShLib':
                    disable = _call_env_subst(env, '$SHLIBNOVERSIONSYMLINKS', *args, **kw)
                elif lt == 'LdMod':
                    disable = _call_env_subst(env, '$LDMODULENOVERSIONSYMLINKS', *args, **kw)
        else:
            disable = _call_env_subst(env, '$IMPLIBNOVERSIONSYMLINKS', *args, **kw)
        return disable


class _LibInfoGeneratorBase:
    """Generator base class for library-related info such as suffixes for
    versioned libraries, symlink maps, sonames etc. It handles commonities
    of SharedLibrary and LoadableModule
    """
    _support_classes = {'ShLib': _ShLibInfoSupport,
                        'LdMod': _LdModInfoSupport,
                        'ImpLib': _ImpLibInfoSupport}

    def __init__(self, libtype, infoname):
        self.libtype = libtype
        self.infoname = infoname

    @property
    def libtype(self):
        return self._support.libtype

    @libtype.setter
    def libtype(self, libtype):
        try:
            support_class = self._support_classes[libtype]
        except KeyError:
            raise ValueError('unsupported libtype %r' % libtype)
        self._support = support_class()

    def get_lib_prefix(self, env, *args, **kw):
        return self._support.get_lib_prefix(env, *args, **kw)

    def get_lib_suffix(self, env, *args, **kw):
        return self._support.get_lib_suffix(env, *args, **kw)

    def get_lib_version(self, env, *args, **kw):
        return self._support.get_lib_version(env, *args, **kw)

    def get_lib_noversionsymlinks(self, env, *args, **kw):
        return self._support.get_lib_noversionsymlinks(env, *args, **kw)

    def get_versioned_lib_info_generator(self, **kw):
        """
        Returns name of generator linker callback that will be used to generate
        our info for a versioned library. For example, if our libtype is 'ShLib'
        and infoname is 'Prefix', it would return 'VersionedShLibPrefix'.
        """
        try:
            libtype = kw['generator_libtype']
        except KeyError:
            libtype = self.libtype
        return 'Versioned%s%s' % (libtype, self.infoname)

    def generate_versioned_lib_info(self, env, args, result=None, **kw):
        callback = self.get_versioned_lib_info_generator(**kw)
        return _call_linker_cb(env, callback, args, result)


class _LibPrefixGenerator(_LibInfoGeneratorBase):
    """Library prefix generator, used as target_prefix in SharedLibrary and
    LoadableModule builders"""

    def __init__(self, libtype):
        super(_LibPrefixGenerator, self).__init__(libtype, 'Prefix')

    def __call__(self, env, sources=None, **kw):
        Verbose = False

        if sources and 'source' not in kw:
            kw2 = kw.copy()
            kw2['source'] = sources
        else:
            kw2 = kw

        prefix = self.get_lib_prefix(env, **kw2)
        if Verbose:
            print("_LibPrefixGenerator: input prefix=%r" % prefix)

        version = self.get_lib_version(env, **kw2)
        if Verbose:
            print("_LibPrefixGenerator: version=%r" % version)

        if version:
            prefix = self.generate_versioned_lib_info(env, [prefix, version], prefix, **kw2)

        if Verbose:
            print("_LibPrefixGenerator: return prefix=%r" % prefix)
        return prefix


ShLibPrefixGenerator = _LibPrefixGenerator('ShLib')
LdModPrefixGenerator = _LibPrefixGenerator('LdMod')
ImpLibPrefixGenerator = _LibPrefixGenerator('ImpLib')


class _LibSuffixGenerator(_LibInfoGeneratorBase):
    """Library suffix generator, used as target_suffix in SharedLibrary and
    LoadableModule builders"""

    def __init__(self, libtype):
        super(_LibSuffixGenerator, self).__init__(libtype, 'Suffix')

    def __call__(self, env, sources=None, **kw):
        Verbose = False

        if sources and 'source' not in kw:
            kw2 = kw.copy()
            kw2['source'] = sources
        else:
            kw2 = kw

        suffix = self.get_lib_suffix(env, **kw2)
        if Verbose:
            print("_LibSuffixGenerator: input suffix=%r" % suffix)

        version = self.get_lib_version(env, **kw2)
        if Verbose:
            print("_LibSuffixGenerator: version=%r" % version)

        if version:
            suffix = self.generate_versioned_lib_info(env, [suffix, version], suffix, **kw2)

        if Verbose:
            print("_LibSuffixGenerator: return suffix=%r" % suffix)
        return suffix


ShLibSuffixGenerator = _LibSuffixGenerator('ShLib')
LdModSuffixGenerator = _LibSuffixGenerator('LdMod')
ImpLibSuffixGenerator = _LibSuffixGenerator('ImpLib')


class _LibSymlinkGenerator(_LibInfoGeneratorBase):
    """Library symlink map generator. It generates a list of symlinks that
    should be created by SharedLibrary or LoadableModule builders"""

    def __init__(self, libtype):
        super(_LibSymlinkGenerator, self).__init__(libtype, 'Symlinks')

    def __call__(self, env, libnode, **kw):
        Verbose = False

        if libnode and 'target' not in kw:
            kw2 = kw.copy()
            kw2['target'] = libnode
        else:
            kw2 = kw

        if Verbose:
            print("_LibSymLinkGenerator: libnode=%r" % libnode.get_path())

        symlinks = None

        version = self.get_lib_version(env, **kw2)
        disable = self.get_lib_noversionsymlinks(env, **kw2)
        if Verbose:
            print('_LibSymlinkGenerator: version=%r' % version)
            print('_LibSymlinkGenerator: disable=%r' % disable)

        if version and not disable:
            prefix = self.get_lib_prefix(env, **kw2)
            suffix = self.get_lib_suffix(env, **kw2)
            symlinks = self.generate_versioned_lib_info(env, [libnode, version, prefix, suffix], **kw2)

        if Verbose:
            print('_LibSymlinkGenerator: return symlinks=%r' % StringizeLibSymlinks(symlinks))
        return symlinks


ShLibSymlinkGenerator = _LibSymlinkGenerator('ShLib')
LdModSymlinkGenerator = _LibSymlinkGenerator('LdMod')
ImpLibSymlinkGenerator = _LibSymlinkGenerator('ImpLib')


class _LibNameGenerator(_LibInfoGeneratorBase):
    """Generates "unmangled" library name from a library file node.

    Generally, it's thought to revert modifications done by prefix/suffix
    generators (_LibPrefixGenerator/_LibSuffixGenerator) used by a library
    builder. For example, on gnulink the suffix generator used by SharedLibrary
    builder appends $SHLIBVERSION to $SHLIBSUFFIX producing node name which
    ends with "$SHLIBSUFFIX.$SHLIBVERSION". Correspondingly, the implementation
    of _LibNameGenerator replaces "$SHLIBSUFFIX.$SHLIBVERSION" with
    "$SHLIBSUFFIX" in the node's basename. So that, if $SHLIBSUFFIX is ".so",
    $SHLIBVERSION is "0.1.2" and the node path is "/foo/bar/libfoo.so.0.1.2",
    the _LibNameGenerator shall return "libfoo.so". Other link tools may
    implement it's own way of library name unmangling.
    """

    def __init__(self, libtype):
        super(_LibNameGenerator, self).__init__(libtype, 'Name')

    def __call__(self, env, libnode, **kw):
        """Returns "demangled" library name"""
        Verbose = False

        if libnode and 'target' not in kw:
            kw2 = kw.copy()
            kw2['target'] = libnode
        else:
            kw2 = kw

        if Verbose:
            print("_LibNameGenerator: libnode=%r" % libnode.get_path())

        version = self.get_lib_version(env, **kw2)
        if Verbose:
            print('_LibNameGenerator: version=%r' % version)

        name = None
        if version:
            prefix = self.get_lib_prefix(env, **kw2)
            suffix = self.get_lib_suffix(env, **kw2)
            name = self.generate_versioned_lib_info(env, [libnode, version, prefix, suffix], **kw2)

        if not name:
            name = os.path.basename(libnode.get_path())

        if Verbose:
            print('_LibNameGenerator: return name=%r' % name)

        return name


ShLibNameGenerator = _LibNameGenerator('ShLib')
LdModNameGenerator = _LibNameGenerator('LdMod')
ImpLibNameGenerator = _LibNameGenerator('ImpLib')


class _LibSonameGenerator(_LibInfoGeneratorBase):
    """Library soname generator. Returns library soname (e.g. libfoo.so.0) for
    a given node (e.g. /foo/bar/libfoo.so.0.1.2)"""

    def __init__(self, libtype):
        super(_LibSonameGenerator, self).__init__(libtype, 'Soname')

    def __call__(self, env, libnode, **kw):
        """Returns a SONAME based on a shared library's node path"""
        Verbose = False

        if libnode and 'target' not in kw:
            kw2 = kw.copy()
            kw2['target'] = libnode
        else:
            kw2 = kw

        if Verbose:
            print("_LibSonameGenerator: libnode=%r" % libnode.get_path())

        soname = _call_env_subst(env, '$SONAME', **kw2)
        if not soname:
            version = self.get_lib_version(env, **kw2)
            if Verbose:
                print("_LibSonameGenerator: version=%r" % version)
            if version:
                prefix = self.get_lib_prefix(env, **kw2)
                suffix = self.get_lib_suffix(env, **kw2)
                soname = self.generate_versioned_lib_info(env, [libnode, version, prefix, suffix], **kw2)

        if not soname:
            # fallback to library name (as returned by appropriate _LibNameGenerator)
            soname = _LibNameGenerator(self.libtype)(env, libnode)
            if Verbose:
                print("_LibSonameGenerator: FALLBACK: soname=%r" % soname)

        if Verbose:
            print("_LibSonameGenerator: return soname=%r" % soname)

        return soname


ShLibSonameGenerator = _LibSonameGenerator('ShLib')
LdModSonameGenerator = _LibSonameGenerator('LdMod')


def StringizeLibSymlinks(symlinks):
    """Converts list with pairs of nodes to list with pairs of node paths
    (strings). Used mainly for debugging."""
    if is_List(symlinks):
        try:
            return [(k.get_path(), v.get_path()) for k, v in symlinks]
        except (TypeError, ValueError):
            return symlinks
    else:
        return symlinks


def EmitLibSymlinks(env, symlinks, libnode, **kw):
    """Used by emitters to handle (shared/versioned) library symlinks"""
    Verbose = False

    # nodes involved in process... all symlinks + library
    nodes = list(set([x for x, y in symlinks] + [libnode]))

    clean_targets = kw.get('clean_targets', [])
    if not is_List(clean_targets):
        clean_targets = [clean_targets]

    for link, linktgt in symlinks:
        env.SideEffect(link, linktgt)
        if Verbose:
            print("EmitLibSymlinks: SideEffect(%r,%r)" % (link.get_path(), linktgt.get_path()))
        clean_list = [x for x in nodes if x != linktgt]
        env.Clean(list(set([linktgt] + clean_targets)), clean_list)
        if Verbose:
            print("EmitLibSymlinks: Clean(%r,%r)" % (linktgt.get_path(), [x.get_path() for x in clean_list]))


def CreateLibSymlinks(env, symlinks):
    """Physically creates symlinks. The symlinks argument must be a list in
    form [ (link, linktarget), ... ], where link and linktarget are SCons
    nodes.
    """

    Verbose = False
    for link, linktgt in symlinks:
        linktgt = link.get_dir().rel_path(linktgt)
        link = link.get_path()
        if Verbose:
            print("CreateLibSymlinks: preparing to add symlink %r -> %r" % (link, linktgt))
        # Delete the (previously created) symlink if exists. Let only symlinks
        # to be deleted to prevent accidental deletion of source files...
        if env.fs.islink(link):
            env.fs.unlink(link)
            if Verbose:
                print("CreateLibSymlinks: removed old symlink %r" % link)
        # If a file or directory exists with the same name as link, an OSError
        # will be thrown, which should be enough, I think.
        env.fs.symlink(linktgt, link)
        if Verbose:
            print("CreateLibSymlinks: add symlink %r -> %r" % (link, linktgt))
    return 0


def LibSymlinksActionFunction(target, source, env):
    for tgt in target:
        symlinks = getattr(getattr(tgt, 'attributes', None), 'shliblinks', None)
        if symlinks:
            CreateLibSymlinks(env, symlinks)
    return 0


def LibSymlinksStrFun(target, source, env, *args):
    cmd = None
    for tgt in target:
        symlinks = getattr(getattr(tgt, 'attributes', None), 'shliblinks', None)
        if symlinks:
            if cmd is None: cmd = ""
            if cmd: cmd += "\n"
            cmd += "Create symlinks for: %r" % tgt.get_path()
            try:
                linkstr = ', '.join(["%r->%r" % (k, v) for k, v in StringizeLibSymlinks(symlinks)])
            except (KeyError, ValueError):
                pass
            else:
                cmd += ": %s" % linkstr
    return cmd


def _call_env_subst(env, string, *args, **kw):
    kw2 = {}
    for k in ('raw', 'target', 'source', 'conv', 'executor'):
        try:
            kw2[k] = kw[k]
        except KeyError:
            pass
    return env.subst(string, *args, **kw2)