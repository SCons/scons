This tree contains tests for formerly deprecated behaviors
that have since been removed.

If there is a runnable test (i.e. a test that verifies a
particular old behavior actually fails if called), it is
here or in a subdirectory and is left selectable by the
test framework.

If there is a test that cannot be run, it will be in a
subdirectory named Old, which will contain a sconstest.skip
file, ensuring those test files are never loaded by the
test framework.

