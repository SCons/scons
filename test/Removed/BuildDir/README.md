BuildDir/Old contains old tests which used the now removed BuildDir
function, env.BuildDir method, and build_dir argument to SConscript,
preserved here for reference; the presence of an sconstest.skip file
means they are never executed.

The "new" tests verify failure using these symbols.
