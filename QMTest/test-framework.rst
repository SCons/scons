=======================
SCons Testing Framework
=======================

SCons uses extensive automated tests to try to ensure quality. The primary goal
is that users should be able to upgrade from version to version without any surprise
changes in behavior.

In general, no change goes into SCons unless it has one or more new or modified
tests that demonstrably exercise the bug being fixed or the feature being added.
There are exceptions to this guideline, but they should be just that, ''exceptions''.
When in doubt, make sure it's tested.

Test Organization
=================

There are three types of SCons tests:

*End-to-End Tests*
  End-to-end tests of SCons are all Python scripts (``*.py``) underneath
  the ``test/`` subdirectory.  They use the test infrastructure modules in the
  ``QMTest`` subdirectory.

*Unit Tests*
  Unit tests for individual SCons modules live underneath the
  ``src/engine/`` subdirectory and are the same base name as the module
  with ``Tests.py`` appended--for example, the unit tests for the
  ``Builder.py`` module are in the ``BuilderTests.py`` script.

*External Tests*
  For the support of external Tools (in the form of packages, preferably), the
  testing framework got extended, such that it can run in standalone mode.
  You can start it from the top-level folder of your Tool's source tree,
  where it then finds all Python scripts (``*.py``) underneath the
  local ``test/`` directory.
  This implies that Tool tests have to be kept in a folder named ``test``,
  like for the SCons core.
  

Contrasting End-to-End and Unit Tests
#####################################

In general, anything that we've put into an end-to-end test script should
be considered a hardened part of the interface (that is, it's something
that a user might do) and should not be broken.  Unit tests are now
considered more malleable, more for testing internal interfaces that
can change so long as we don't break users' ``SConscript`` files.  (This
wasn't always the case, and there's a lot of meaty code in many of the
unit test scripts that does, in fact, capture external interface
behavior.  In general, we should try to move those things to end-to-end
scripts as we find them.)

It's more difficult to debug end-to-end tests.  You can actually go
straight into the Python debugger on the unit test scripts by using the
``runtest.py --pdb`` option, but the end-to-end tests treat an SCons
invocation as a "black box" and just look for external effects.
Simple ``print`` statements within the SCons code itself often don't help
debug end-to-end because they end up in SCons output that gets compared
against expected output and cause a test failure.  Probably the most
effective technique is to use the internal ``SCons.Debug.Trace()`` function,
which prints output to ``/dev/tty`` on Linux/UNIX systems and ``con`` on
Windows systems, so you can see what's going on.

Naming conventions
##################

The end-to-end tests, more or less, stick to the following naming conventions:

1. All tests end with a .py suffix.

2. In the *General* form we use

   ``Feature.py``
       for the test of a specified feature; try to
       keep this description reasonably short

   ``Feature-x.py``
       for the test of a specified feature using
       option ``x``

3. The *command line option* tests take the form

   ``option-x.py``
       for a lower-case single-letter option

   ``option--X.py``
       upper-case single-letter option
       (with an extra hyphen, so the file names will
       be unique on case-insensitive systems)

   ``option--lo.py``  
       long option; abbreviate the long
       option name to a few characters


Running Tests
=============

The standard set of SCons tests are run from the top-level source directory
by the ``runtest.py`` script.
There is a ``--qmtest`` option that checks whether the ``QMTest`` package
is installed on your system. If it can be found, then the ``runtest.py`` script
will use it to carry out the tests.

Help is available through the ``-h`` option:

::

  $ python runtest.py -h

To simply run all the tests, use the ``-a`` option:

::

  $ python runtest.py -a

By default, ``runtest.py`` prints a count and percentage message for each test
case, along with the name of the test file.
If you need the output to be more silent, have a look at the ``-q``, ``-s`` and
``-k`` options.

You may specifically list one or more tests to be run:

::

  $ python runtest.py src/engine/SCons/BuilderTests.py
  $ python runtest.py test/option-j.py test/Program.py

Folder names are allowed arguments as well, so you can do a

::

  $ python runtest.py test/SWIG

to run all SWIG tests only.

You can also use the ``-f`` option to execute just the tests listed in a specified
text file:

::

  $ cat testlist.txt
  test/option-j.py
  test/Program.py
  $ python runtest.py -f testlist.txt


One test must be listed per line, and any lines that begin with '#'
will be ignored (the intent being to allow you, for example,
to comment out tests that
are currently passing and then uncomment all of the tests in the file
for a final validation run).

If more than one test is run, the ``runtest.py`` script prints a summary
of how many tests passed, failed, or yielded no result, and lists any
unsuccessful tests.

The above invocations all test directly the files underneath the ``src/``
subdirectory, and do not require that a packaging build be performed first.
The ``runtest.py`` script supports additional options to run tests against
unpacked packages in the ``build/test-*/`` subdirectories.

If you are testing a separate Tool outside of the SCons source tree, you have
to call the ``runtest.py`` script in *external* (stand-alone) mode::

  $ python ~/scons/runtest.py -e -a

.  This ensures that the testing framework doesn't try to access SCons classes
needed for some of the *internal* test cases.

Note, that the actual tests are carried out in a temporary folder each, which gets
deleted afterwards. This ensures that your source directories don't get clobbered
with temporary files from the test runs. It also means that you can't simply change
into a folder to "debug things" after a test has gone wrong. For a way around this,
check out the ``PRESERVE`` environment variable. It can be seen in action in
`How to convert old tests`_ below.

Not Running Tests
=================

If you simply want to check which tests would get executed, you can call the
``runtest.py`` script with the ``-l`` option::

  $ python runtest.py -l

Then there is also the ``-n`` option, which prints the command line for each
single test, but doesn't actually execute them::

  $ python runtest.py -n

Finding Tests
=============

When started in *standard* mode

::

  $ python runtest.py -a


, ``runtest.py`` assumes that it is run from the SCons top-level source directory.
It then dives into the ``src`` and ``test`` folders, where it tries to find filenames

    ``*Test.py``
        for the ``src`` directory, and
  
    ``*.py``
        for the ``test`` folder.

When using fixtures, you may quickly end up in a position where you have supporting
Python script files in a subfolder, but they shouldn't get picked up as test scripts.
In this case you have two options:

1. Add a file with the name ``sconstest.skip`` to your subfolder. This lets
   ``runtest.py`` skip the contents of the directory completely.
2. Create a file ``.exclude_tests`` in each folder in question, and in it list
   line-by-line the files to get excluded from testing.

The same rules apply when testing external Tools by using the ``-e`` option.


"Hello, world!" SCons Test Script
=================================

To illustrate how the end-to-end test scripts work,
let's walk through a simple "Hello, world!" example:

::

  #!python
  import TestSCons

  test = TestSCons.TestSCons()

  test.write('SConstruct', """\
  Program('hello.c')
  """)

  test.write('hello.c', """\
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
  Imports the main infrastructure for writing SCons tests.  This is normally the only part of the infrastructure that needs importing.  Sometimes other Python modules are necessary or helpful, and get imported before this line.

``test = TestSCons.TestSCons()``
  This initializes an object for testing.  A fair amount happens under the covers when the object is created, including:

    * A temporary directory is created for all the in-line files that will get created.
    * The temporary directory's removal is arranged for when the test is finished.
    * We ``os.chdir()`` to the temporary directory.

``test.write('SConstruct', ...``
  This line creates an ``SConstruct`` file in the temporary directory, to be used as input to the ``scons`` run(s) that we're testing.  Note the use of the Python triple-quote syntax for the contents of the ``SConstruct`` file.  Because input files for tests are all created from in-line data like this, the tests can sometimes get a little confusing to read, because some of the Python code is found

``test.write('hello.c', ...``
  This lines creates an ``hello.c`` file in the temporary directory.  Note that we have to escape the ``\\n`` in the ``"Hello, world!\\n"`` string so that it ends up as a single backslash in the ``hello.c`` file on disk.

``test.run()``
  This actually runs SCons.  Like the object initialization, things happen under the covers:

    * The exit status is verified; the test exits with a failure if the exit status is not zero.
    * The error output is examined, and the test exits with a failure if there is any

``test.run(program='./hello', stdout="Hello, world!\n")``
  This shows use of the ``TestSCons.run()`` method to execute a program other than ``scons``, in this case the ``hello`` program we just presumably built.  The ``stdout=`` keyword argument also tells the ``TestSCons.run()`` method to fail if the program output does not match the expected string ``"Hello, world!\n"``.  Like the previous ``test.run()`` line, it will also fail the test if the exit status is non-zero, or there is any error output.

``test.pass_test()``
  This is always the last line in a test script.  It prints ``PASSED`` on the screen and makes sure we exit with a ``0`` status to indicate the test passed.  As a side effect of destroying the ``test`` object, the created temporary directory will be removed.

Working with fixtures
=====================

In the simple example above, we have seen how to create files in the temporary test directory.
We give a filename to the ``TestSCons.write()`` method, together with its contents, and it gets
written to the test folder right before its start.

This technique can still be seen throughout most of the end-to-end tests, but there is a better
way. It's much easier to edit, create and maintain real files, instead of copy/pasting
content to/from a Python script. If the test files get longer, the test script
gets longer and is harder to read.

Against this, we now have the possibility to copy single files or the contents of a
local folder to the test directory. Since we can reuse these files/folders to setup
several tests, we call them *fixtures* in the following.

Directory fixtures
##################

The function ``dir_fixture(self, srcdir, dstdir=None)`` in the ``TestCmd`` class
copies the contents of the specified folder ``srcdir`` from
the directory of the called test script, to the current
temporary test directory.
The ``srcdir`` name may be a list, in which case the elements are
concatenated with the ``os.path.join()`` method.  The ``dstdir`` is
assumed to be under the temporary working directory, it gets
created automatically, if it does not already exist.

A short syntax example::

  test = TestSCons.TestSCons()
  test.dir_fixture('image')
  test.run()  

would copy all files and subfolders from the local ``image`` folder, to
the temporary directory for the current test.

If you'd like to see a real example for this in action, refer to the test
named ``test/packaging/convenience-functions/convenience-functions.py``.
  
File fixtures
#############

Like for directory fixtures, ``file_fixture(self, srcfile, dstfile=None)``
copies the file ``srcfile`` from the directory of
the called script, to the temporary test directory.
The ``dstfile`` is assumed to be under the temporary working
directory, unless it is an absolute path name.
If ``dstfile`` is specified, its target directory gets created
automatically if it doesn't already exist.

With a::

  test = TestSCons.TestSCons()
  test.file_fixture('SConstruct')
  test.file_fixture(['src','main.cpp'],['src','main.cpp'])
  test.run()  

you would copy the files ``SConstruct`` and ``src/main.cpp`` to the temporary
test folder, prior to running the test itself.

Again, a reference example can be found in the current *default* revision of
SCons, it is ``test/packaging/sandbox-test/sandbox-test.py``.

For even more examples you should check out one of the external Tools, e.g. the
*Qt4* Tool at https://bitbucket.org/dirkbaechle/scons_qt4. Also visit the SCons
Tools Index at http://www.scons.org/wiki/ToolsIndex for a complete
list of available Tools, though not all may have tests yet.

How to convert old tests
########################

We now show how to convert a test, still using the ``TestSCons.write()`` method, to
the fixture based approach. For this, we need to get at the files as they
are written to each temporary test folder.

Luckily, ``runtest.py`` checks for the existence of an environment variable named
``PRESERVE``. If it is set to a non-zero value, the testing framework doesn't delete
the test folder as ususal, but prints its name to the screen.

So, you should be able to give the commands 

::

  $ export PRESERVE=1
  $ python runtest.py test/packaging/sandbox-test.py

, assuming Linux and a bash-like shell.
  
The output should then look something like this::

  1/1 (100.00%) /usr/bin/python -tt test/packaging/sandbox-test.py
  PASSED
  Preserved directory /tmp/testcmd.4060.twlYNI

and you see that the test files have been kept in the folder ``/tmp/testcmd.4060.twlYNI``, 
where you can now copy them from to your new *fixture* folder. Then, in the test
script you simply remove all the tedious ``TestSCons.write()`` statements and
replace them by a single ``TestSCons.dir_fixture()``.

Finally, you shouldn't forget to clean up and remove the temporary test directory. ``;)``

Test Infrastructure
===================

The test API is in ``QMTest/TestSCons.py``.  ``TestSCons`` is a subclass of
``TestCommon``, which is a subclass of ``TestCmd``; all those python files are
in ``QMTest``. Start in ``QMTest/TestCmd.py`` for the base API definitions,
like how to create files (``test.write()``) and run commands (``test.run()``).

You want to use ``TestSCons`` for the end-to-end tests in ``test``, but ``TestCmd``
for the unit tests in the ``src`` folder.

The match functions work like this:

TestSCons.match_re:: match each line with a RE
  * Splits the lines into a list (unless they already are)
  * splits the REs at newlines (unless already a list) and puts ^..$ around each
  * then each RE must match each line.  This means there must be as many REs as lines.

TestSCons.match_re_dotall:: match all the lines against a single RE
  * Joins the lines with newline (unless already a string)
  * joins the REs with newline (unless it's a string) and puts ^..$ around the whole thing
  * then whole thing must match with python re.DOTALL.

Use them in a test like this::

  test.run(..., match=TestSCons.match_re, ...)

or::

  test.must_match(..., match=TestSCons.match_re, ...)

Avoiding Tests based on Tool existence
======================================

Here's an easy sample::

  #!python
  intelc = test.detect_tool('intelc', prog='icpc')
  if not intelc:
      test.skip_test("Could not load 'intelc' Tool; skipping test(s).\n")

See ``QMTest/TestSCons.py`` for the ``detect_tool`` method.  It calls the tool's
``generate()`` method, and then looks for the given prog (tool name by default) in
``env['ENV']['PATH']``.


