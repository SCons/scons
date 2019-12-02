=======================
SCons Testing Framework
=======================

SCons uses extensive automated tests to ensure quality. The primary goal
is that users be able to upgrade from version to version without
any surprise changes in behavior.

In general, no change goes into SCons unless it has one or more new
or modified tests that demonstrably exercise the bug being fixed or
the feature being added.  There are exceptions to this guideline, but
they should be just that, ''exceptions''.  When in doubt, make sure
it's tested.

Test Organization
=================

There are three types of SCons tests:

*End-to-End Tests*
  End-to-end tests of SCons are Python scripts (``*.py``) underneath the
  ``test/`` subdirectory.  They use the test infrastructure modules in
  the ``testing/framework`` subdirectory. They build set up complete
  projects and call scons to execute them, checking that the behavior is
  as expected.

*Unit Tests*
  Unit tests for individual SCons modules live underneath the
  ``src/engine/`` subdirectory and are the same base name as the module
  to be tests, with ``Tests`` appended before the ``.py``. For example,
  the unit tests for the ``Builder.py`` module are in the
  ``BuilderTests.py`` script.  Unit tests tend to be based on assertions.

*External Tests*
  For the support of external Tools (in the form of packages, preferably),
  the testing framework is extended so it can run in standalone mode.
  You can start it from the top-level folder of your Tool's source tree,
  where it then finds all Python scripts (``*.py``) underneath the local
  ``test/`` directory.  This implies that Tool tests have to be kept in
  a folder named ``test``, like for the SCons core.


Contrasting End-to-End and Unit Tests
#####################################

In general, functionality with end-to-end tests
should be considered a hardened part of the public interface (that is,
something that a user might do) and should not be broken.  Unit tests
are now considered more malleable, more for testing internal interfaces
that can change so long as we don't break users' ``SConscript`` files.
(This wasn't always the case, and there's a lot of meaty code in many
of the unit test scripts that does, in fact, capture external interface
behavior.  In general, we should try to move those things to end-to-end
scripts as we find them.)

End-to-end tests are by their nature harder to debug.
You can drop straight into the Python debugger on the unit test
scripts by using the ``runtest.py --pdb`` option, but the end-to-end
tests treat an SCons invocation as a "black box" and just look for
external effects; simple methods like inserting ``print`` statements
in the SCons code itself can disrupt those external effects.
See `Debugging End-to-End Tests`_ for some more thoughts.

Naming Conventions
##################

The end-to-end tests, more or less, stick to the following naming
conventions:

#. All tests end with a .py suffix.

#. In the *General* form we use

   ``Feature.py``
       for the test of a specified feature; try to keep this description
       reasonably short

   ``Feature-x.py``
       for the test of a specified feature using option ``x``
#. The *command line option* tests take the form

   ``option-x.py``
       for a lower-case single-letter option

   ``option--X.py``
       upper-case single-letter option (with an extra hyphen, so the
       file names will be unique on case-insensitive systems)

   ``option--lo.py``
       long option; abbreviate the long option name to a few characters


Running Tests
=============

The standard set of SCons tests are run from the top-level source
directory by the ``runtest.py`` script.

Help is available through the ``-h`` option::

  $ python runtest.py -h

To simply run all the tests, use the ``-a`` option::

  $ python runtest.py -a

By default, ``runtest.py`` prints a count and percentage message for each
test case, along with the name of the test file.  If you need the output
to be more silent, have a look at the ``-q``, ``-s`` and ``-k`` options.

You may specifically list one or more tests to be run::

  $ python runtest.py src/engine/SCons/BuilderTests.py
  $ python runtest.py test/option-j.py test/Program.py

Folder names are allowed in the test list as well, so you can do::

  $ python runtest.py test/SWIG

to run all SWIG tests only.

You can also use the ``-f`` option to execute just the tests listed in
a test list file::

  $ cat testlist.txt
  test/option-j.py
  test/Program.py
  $ python runtest.py -f testlist.txt

One test must be listed per line, and any lines that begin with '#'
will be ignored (the intent being to allow you, for example, to comment
out tests that are currently passing and then uncomment all of the tests
in the file for a final validation run).

If more than one test is run, the ``runtest.py`` script prints a summary
of how many tests passed, failed, or yielded no result, and lists any
unsuccessful tests.

The above invocations all test against the scons files underneath the ``src/``
subdirectory, and do not require that a packaging build of SCons be performed
first.  This is the most common mode: make some changes, and test in
place the effects.
The ``runtest.py`` script supports additional options to run
tests against unpacked packages in the ``build/test-*/`` subdirectories.

If you are testing a separate Tool outside of the SCons source tree, you
have to call the ``runtest.py`` script in *external* (stand-alone) mode::

  $ python ~/scons/runtest.py -e -a

This ensures that the testing framework doesn't try to access SCons
classes needed for some of the *internal* test cases.

Note that as each test is run, it is executed in a temporary directory
created just for that test, which is by default removed when the
test is complete.  This ensures that your source directories
don't get clobbered with temporary files and changes from the test runs.
If the test itself needs to know the directory, it can be obtained
as ``test.workdir``, or more commonly by calling ``test.workpath``,
a function which takes a path-component argument and returns the path to
that path-component in the testing directory.

The use of an ephemeral test directory means that you can't simply change
into a folder to "debug things" after a test has gone wrong.
For a way around this, check out the ``PRESERVE`` environment variable.
It can be seen in action in `How to Convert Old Tests to Use Fixures`_ below.

Not Running Tests
=================

If you simply want to check which tests would get executed, you can call
the ``runtest.py`` script with the ``-l`` option combined with whichever
test finding options (see below) you intend to use. Example:

  $ python runtest.py -l test/scons-time

``runtest.py`` also has ``-n`` option, which prints the command line for
each test which would have been run, but doesn't actually execute them::

  $ python runtest.py -n -a

Finding Tests
=============

When started in *standard* mode::

  $ python runtest.py -a

``runtest.py`` assumes that it is run from the SCons top-level source
directory.  It then dives into the ``src`` and ``test`` folders, where
it tries to find filenames

``*Test.py``
  for the ``src`` folder

``*.py``
  for the ``test`` folder

When using fixtures, you may quickly end up in a position where you have
supporting Python script files in a subfolder, but they shouldn't get
picked up as test scripts.  In this case you have two options:

#. Add a file with the name ``sconstest.skip`` to your subfolder. This
   lets ``runtest.py`` skip the contents of the directory completely.
#. Create a file ``.exclude_tests`` in each folder in question, and in
   it list line-by-line the files to get excluded from testing.

The same rules apply when testing external Tools by using the ``-e``
option.


Example End-to-End Test Script
==============================

To illustrate how the end-to-end test scripts work, let's walk through
a simple "Hello, world!" example::

  #!python
  import TestSCons

  test = TestSCons.TestSCons()

  test.write('SConstruct', """\
  Program('hello.c')
  """)

  test.write('hello.c', """\
  #include <stdio.h>

  int
  main(int argc, char *argv[])
  {
        printf("Hello, world!\\n");
        exit (0);
  }
  """)

  test.run()

  test.run(program='./hello', stdout="Hello, world!\n")

  test.pass_test()


``import TestSCons``
  Imports the main infrastructure for writing SCons tests.  This is
  normally the only part of the infrastructure that needs importing.
  Sometimes other Python modules are necessary or helpful, and get
  imported before this line.

``test = TestSCons.TestSCons()``
  This initializes an object for testing.  A fair amount happens under
  the covers when the object is created, including:

  * A temporary directory is created for all the in-line files that will
    get created.

  * The temporary directory's removal is arranged for when
    the test is finished.

  * The test does ``os.chdir()`` to the temporary directory.

``test.write('SConstruct', ...)``
  This line creates an ``SConstruct`` file in the temporary directory,
  to be used as input to the ``scons`` run(s) that we're testing.
  Note the use of the Python triple-quote syntax for the contents
  of the ``SConstruct`` file.  Because input files for tests are all
  created from in-line data like this, the tests can sometimes get
  a little confusing to read, because some of the Python code is found

``test.write('hello.c', ...)``
  This lines creates an ``hello.c`` file in the temporary directory.
  Note that we have to escape the newline in the
  ``"Hello, world!\\n"`` string so that it ends up as a single
  backslash in the ``hello.c`` file on disk.

``test.run()``
  This actually runs SCons.  Like the object initialization, things
  happen under the covers:

  * The exit status is verified; the test exits with a failure if
    the exit status is not zero.
  * The error output is examined, and the test exits with a failure
    if there is any.

``test.run(program='./hello', stdout="Hello, world!\n")``
  This shows use of the ``TestSCons.run()`` method to execute a program
  other than ``scons``, in this case the ``hello`` program we just
  presumably built.  The ``stdout=`` keyword argument also tells the
  ``TestSCons.run()`` method to fail if the program output does not
  match the expected string ``"Hello, world!\n"``.  Like the previous
  ``test.run()`` line, it will also fail the test if the exit status is
  non-zero, or there is any error output.

``test.pass_test()``
  This is always the last line in a test script.  If we get to
  this line, it means we haven't bailed out on a failure or skip,
  so the result was good. It prints ``PASSED``
  on the screen and makes sure we exit with a ``0`` status to indicate
  the test passed.  As a side effect of destroying the ``test`` object,
  the created temporary directory will be removed.

Working with Fixtures
=====================

In the simple example above, the files to set up the test are created
on the fly by the test program. We give a filename to the ``TestSCons.write()``
method, and a string holding its contents, and it gets written to the test
folder right before starting..

This simple technique can be seen throughout most of the end-to-end
tests as it was the original technique provided to test developers,
but it is definitely not the preferred way to write a new test.
To develop this way, you first need to create the necessary files and
get them to work, then convert them to an embedded string form, which may
involve lots of extra escaping.  These embedded files are then tricky
to maintain.  As a test grows multiple steps, it becomes less easy to
read, since the embedded strings aren't quite the final files, and
the volume of test code obscures the flow of the testing steps.
Additionally, as SCons moves more to the use of code checkers and
formatters to detect problems and keep a standard coding style for
better readability, note that these techniques don't look inside
strings, so they're either left out or lots of manual work has to be done.

In testing parlance, a fixture is a repeatable test setup.  The SCons
test harness allows the use of saved files or directories to be used
in that sense: "the fixture for this test is foo", instead of writing
a whole bunch of strings to create files. Since these setups can be
reusable across multiple tests, the *fixture* terminology applies well.

Note: fixtures must not be treated by SCons as runnable tests. To exclude
them, see instructions in the above section named "Finding Tests".

Directory Fixtures
##################

The test harness method ``dir_fixture(srcdir, [dstdir])``
copies the contents of the specified folder ``srcdir`` from
the directory of the called test script to the current temporary test
directory.  The ``srcdir`` name may be a list, in which case the elements
are concatenated with the ``os.path.join()`` method.  The ``dstdir``
is assumed to be under the temporary working directory, it gets created
automatically, if it does not already exist.

If ``srcdir`` represents an absolute path, it is used as-is. Otherwise,
if the harness was invoked with the environment variable ``FIXTURE_DIRS``
set, the test instance will present that list of directories to search
as ``self.fixture_dirs``, each of these are additionally searched for
a directory with the name of ``srcdir``.

A short syntax example::

  test = TestSCons.TestSCons()
  test.dir_fixture('image')
  test.run()

would copy all files and subfolders from the local ``image`` folder
to the temporary directory for the current test, then run it.

To see a real example for this in action, refer to the test named
``test/packaging/convenience-functions/convenience-functions.py``.

File Fixtures
#############

Similarly, the method ``file_fixture(srcfile, [dstfile])``
copies the file ``srcfile`` from the directory of the called script,
to the temporary test directory.  The ``dstfile`` is assumed to be
under the temporary working directory, unless it is an absolute path
name.  If ``dstfile`` is specified, its target directory gets created
automatically if it doesn't already exist.

If ``srcfile`` represents an absolute path, it is used as-is. Otherwise,
any passed in fixture directories are used as additional places to
search, as for the ``dir_fixture`` case.

With the following code::

  test = TestSCons.TestSCons()
  test.file_fixture('SConstruct')
  test.file_fixture(['src','main.cpp'],['src','main.cpp'])
  test.run()

The files ``SConstruct`` and ``src/main.cpp`` are copied to the
temporary test directory. Notice the second ``file_fixture`` line
preserves the path of the original, otherwise ``main.cpp``
would have landed in the top level of the test directory.

Again, a reference example can be found in the current revision
of SCons, it is ``test/packaging/sandbox-test/sandbox-test.py``.

For even more examples you should check out
one of the external Tools, e.g. the *Qt4* Tool at
https://bitbucket.org/dirkbaechle/scons_qt4. Also visit the SCons Tools
Index at https://github.com/SCons/scons/wiki/ToolsIndex for a complete
list of available Tools, though not all may have tests yet.

How to Convert Old Tests to Use Fixures
#######################################

Tests using the inline ``TestSCons.write()`` method can fairly easily be
converted to the fixture based approach. For this, we need to get at the
files as they are written to each temporary test folder.

``runtest.py`` checks for the existence of an environment
variable named ``PRESERVE``. If it is set to a non-zero value, the testing
framework preserves the test folder instead of deleting it, and prints
its name to the screen.

So, you should be able to give the commands::

  $ PRESERVE=1 python runtest.py test/packaging/sandbox-test.py

assuming Linux and a bash-like shell. For a Windows ``cmd`` shell, use
``set PRESERVE=1`` (that will leave it set for the duration of the
``cmd`` session, unless manually cleared).

The output will then look something like this::

  1/1 (100.00%) /usr/bin/python -tt test/packaging/sandbox-test.py
  PASSED
  Preserved directory /tmp/testcmd.4060.twlYNI

You can now copy the files from that folder to your new
*fixture* folder. Then, in the test script you simply remove all the
tedious ``TestSCons.write()`` statements and replace them by a single
``TestSCons.dir_fixture()``.

Finally, don't forget to clean up and remove the temporary test
directory. ``;)``

For more complex testing scenarios you can use ``file_fixture`` with
the option to rename (that is, supplying a second argument, which is
the name to give the fixture file being copied).  For example some test
files write multiple ``SConstruct`` files across the full run.
These files can be given different names - perhaps using a sufffix -
and then sucessively copied to the final name as needed::

  test.file_fixture('fixture/SConstruct.part1', 'SConstruct')
  # more setup, then run test
  test.file_fixture('fixture/SConstruct.part2', 'SConstruct')
  # etc.


When Not to Use a Fixture
#########################

Note that some files are not appropriate for use in a fixture as-is:
fixture files should be static. If the creation of the file involves
interpolating data discovered during the run of the test script,
that process should stay in the script.  Here is an example of this
kind of usage that does not lend itself to a fixture::

  import TestSCons
  _python_ = TestSCons._python_

  test.write('SConstruct', """
  cc = Environment().Dictionary('CC')
  env = Environment(LINK=r'%(_python_)s mylink.py',
                    LINKFLAGS=[],
                    CC=r'%(_python_)s mycc.py',
                    CXX=cc,
                    CXXFLAGS=[])
  env.Program(target='test1', source='test1.c')
  """ % locals())

Here the value of ``_python_`` is picked out of the script's
``locals`` dictionary - which works because we've set it above -
and interpolated using a mapping key into the string that will
be written to ``SConstruct``. A fixture would be hard to use
here because we don't know the value of `_python_` until runtime.

The other files created in this test may still be candidates for
use as fixture files, however.

Debugging End-to-End Tests
==========================

Most of the end to end tests have expectations for standard output
and error embedded in the tests. The expectation could be either
that there is nothing on that stream, or that it will contain
very specific text which the test matches against. So adding
``print()`` calls, or ``sys.stderr.write()`` or similar will
emit data that the tests do not expect, and thus cause further
failures - possibly even obscuring the original error.
Say you have three different tests in a script, and the third
one is unexpectedly failing. You add some debug prints to the
part of scons that is involved, and now the first test of the
three starts failing, aborting the test run before it gets
to the third test you were trying to debug.

Still, there are some techniques to help debugging.

The first step should be to run the tests so the harness
emits more information, without forcing more information into
the test stdout/stderr which will confuse result evaulation.
``runtest.py`` has several verbose levels which can be used
for this purpose:

  python runtest.py --verbose=2 test/foo.py

You can also use the internal
``SCons.Debug.Trace()`` function, which prints output to
``/dev/tty`` on Linux/UNIX systems and ``con`` on Windows systems,
so you can see what's going on.

If you do need to add informational messages in scons code
to debug a problem, you can use logging and send the messages
to a file instead, so they don't interrupt the test expectations.

Part of the technique discussed in the section
`How to Convert Old Tests to Use Fixures`_ can also be helpful
for debugging purposes.  If you have a failing test, try::

  $ PRESERVE=1 python runtest.py test/failing-test.py

You can now go to the save directory reported from this run
and invoke the test manually to see what it is doing, without
the presence of the test infrastructure which would otherwise
"swallow" output you may be interested in. In this case,
adding debug prints may be more useful.


Test Infrastructure
===================

The main test API in the ``TestSCons.py`` class.  ``TestSCons``
is a subclass of ``TestCommon``, which is a subclass of ``TestCmd``.
All those classes are defined in python files of the same name
in ``testing/framework``. Start in
``testing/framework/TestCmd.py`` for the base API definitions, like how
to create files (``test.write()``) and run commands (``test.run()``).

Use ``TestSCons`` for the end-to-end tests in ``test``, but use
``TestCmd`` for the unit tests in the ``src`` folder.

The match functions work like this:

``TestSCons.match_re``
  match each line with a RE

  * Splits the lines into a list (unless they already are)
  * splits the REs at newlines (unless already a list) and puts ^..$ around each
  * then each RE must match each line.  This means there must be as many
    REs as lines.

``TestSCons.match_re_dotall``
  match all the lines against a single RE

  * Joins the lines with newline (unless already a string)
  * joins the REs with newline (unless it's a string) and puts ``^..$``
    around the whole  thing
  * then whole thing must match with python re.DOTALL.

Use them in a test like this::

  test.run(..., match=TestSCons.match_re, ...)

or::

  test.must_match(..., match=TestSCons.match_re, ...)

Avoiding Tests Based on Tool Existence
======================================

Here's a simple example::

  #!python
  intelc = test.detect_tool('intelc', prog='icpc')
  if not intelc:
      test.skip_test("Could not load 'intelc' Tool; skipping test(s).\n")

See ``testing/framework/TestSCons.py`` for the ``detect_tool`` method.
It calls the tool's ``generate()`` method, and then looks for the given
program (tool name by default) in ``env['ENV']['PATH']``.

The ``where_is`` method can be used to look for programs that
are do not have tool specifications. The existing test code
will have many samples of using either or both of these to detect
if it is worth even proceeding with a test.
