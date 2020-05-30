SourceSignatures.py is the "new" test, only makes sure scons actually
fails in the presence of the method or setoption call.

The Old directory is the former tests from the deprecated state,
preserved here for reference; the presence of an sconstest.skip file
means they are never executed.
