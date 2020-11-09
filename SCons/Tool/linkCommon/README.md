

# Versioned Shared Library and Loadable modules requirements

The following env variables can affect the command line and created files for these

* `SHLIBVERSION` - If this is not set, the all of the following will be ignored?
* `SONAME`
* `SOVERSION`
* `APPLELINK_NO_CURRENT_VERSION`    (applelink only)
* `APPLELINK_CURRENT_VERSION`       (applelink only)
* `APPLELINK_COMPATIBILITY_VERSION` (applelink only)

In most cases the linker will create a file named as

`${SHLIBPREFIX}lib_name${SHLIBVERSION}${SHLIBSUFFIX}`

Which will have a soname baked into it as one of the

* `${SONAME}`
* `${SHLIBPREFIX}lib_name${SOVERSION}${SHLIBSUFFIX}`
* `-Wl,-soname=$_SHLIBSONAME` (for gnulink as similar)
* (for applelink only)
   * `${SHLIBPREFIX}lib_name${major version only from SHLIBVERSION}${SHLIBSUFFIX}`
   * `-Wl,-compatibility_version,%s`
   * `-Wl,-current_version,%s`
   
For **applelink** the version has to follow these rules to verify that the version # is valid.

* For version # = X[.Y[.Z]]
* where X 0-65535
* where Y either not specified or 0-255
* where Z either not specified or 0-255

   
For most platforms this will lead to a series of symlinks eventually pointing to the actual shared library (or loadable module file).
1. `${SHLIBPREFIX}lib_name${SHLIBSUFFIX} -> ${SHLIBPREFIX}lib_name${SHLIBVERSION}${SHLIBSUFFIX}`
1. `${SHLIBPREFIX}lib_name${SOVERSION}${SHLIBSUFFIX} -> ${SHLIBPREFIX}lib_name${SHLIBVERSION}${SHLIBSUFFIX}`

These symlinks are stored by the emitter in the following
`target[0].attributes.shliblinks = symlinks`
This means that those values are fixed a the time SharedLibrary() is called (generally)

For **openbsd** the following rules for symlinks apply

   * OpenBSD uses x.y shared library versioning numbering convention and doesn't use symlinks to backwards-compatible libraries


The current code provides the following hooks a compiler can use to customize:

```        
        'VersionedShLibSuffix': _versioned_lib_suffix,
        'VersionedLdModSuffix': _versioned_lib_suffix,
        'VersionedShLibSymlinks': _versioned_shlib_symlinks,
        'VersionedLdModSymlinks': _versioned_ldmod_symlinks,
        'VersionedShLibName': _versioned_shlib_name,
        'VersionedLdModName': _versioned_ldmod_name,
        'VersionedShLibSoname': _versioned_shlib_soname,
        'VersionedLdModSoname': _versioned_ldmod_soname,
```


User can request:
env.SharedLibrary('a',sources, SHLIBVERSION)
env.SharedLibrary('liba.so',sources, SHLIBVERSION)
Ideally we'll keep the 'a' for use in constructing all follow on. To do this we have to do it in the Builder() or at
least prevent  BuilderBase._create_nodes() from discarding this info if it's available.


Firstly check if [SH|LD]LIBNOVERSIONSYMLINKS defined or if [SH|LD]LIBVERSION is not defined, if so we do nothing special

The emitter can calculate the filename stem 'a' above and store it on the target node. Then also create the symlinks
and store those on the node. We should have all the information needed by the time the emitter is called.
Same should apply for loadable modules..
This should be vastly simpler.
Unfortunately we cannot depend on the target having an OverrideEnvironment() which we could populate all the related
env variables in the emitter...
Maybe we can force one at that point?


SOVERSION can be specified, if not, then defaults to major portion of SHLIBVERSION
SONAME can be specified, if not defaults to ${SHLIBPREFIX}lib_name${SOVERSION}

NOTE: mongodb uses Append(SHLIBEMITTER=.. )  for their libdeps stuff. (So test 
with that once you have new logic working)


TODO:
1. Generate proper naming for:
   * shared library (altered by emitter if SHLIBVERSION is set)
   * soname'd library (for symlink) - SHLIB_SONAME_SYMLINK
   * non versioned shared library (for symlink) - SHLIB_NOVERSION_SYMLINK
2. in emitter also, actually create the symlinks (if SHLIBVERSION is set) and 
   add to node.attributes.symlinks. (note bsd doesn't do this so skip if on bsd)
3. We need to check somewhere if SONAME and SOVERSION are both set and thrown an error. 
   Probably in the emitter to it will traceback to where the SharedLibrary() which
   yielded the issue is located.
4. Generate proper linker soname compiler construct (-Wl,soname=libxyz.1.so for example)

hrm.. tricky.
SHLIBSUFFIX needs to have .${SHLIBVERSION}${SHLIBSUFFIX} as it's value when 
fixing a sharedlibrary()'s target file name (from a -> liba.1.2.3.so)
But when creating the symlinks for the rest, we need to drop the versioned SHLIBSUFFIX