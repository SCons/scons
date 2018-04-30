This directory contains testing infrastructure.  Note that not all of
the pieces here are local to SCons.

    README.txt

        What you're looking at right now.

    SConscript

        Configuration for our packaging build, to copy the necessary
        parts of the infrastructure into a build directory.

    TestCmd.py
    TestCmdTests.py
    TestCommon.py
    TestCommonTests.py

        The TestCmd infrastructure for testing external commands.
        These are for generic command testing, are used by some
        other projects, and are developed separately from SCons.
        (They're developed by SK, but still...)

        We've captured the unit tests (Test*Tests.py) for these files
        along with the actual modules themselves to make it a little
        easier to hack on them for our purposes.  Note, however,
        that any SCons-specific functionality should be implemented
        in one of the

    TestRuntest.py

        Test infrastructure for our runtest.py script.

    TestSCons.py

        Test infrastructure for SCons itself.

    TestSConsMSVS.py

        Test infrastructure for SCons' Visual Studio support.

    TestSCons_time.py

        Test infrastructure for the scons-time.py script.

    TestSConsign.py

        Test infrastructure for the sconsign.py script.

__COPYRIGHT__
__FILE__ __REVISION__ __DATE__ __DEVELOPER__
