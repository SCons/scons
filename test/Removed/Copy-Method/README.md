Copy-Method.py is the "new" test for env.Copy, making sure we
get an AttributeError.

The Old directory is the former tests from the deprecated state,
preserved here for reference; the presence of an sconstest.skip file
means they are never executed.
