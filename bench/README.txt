# __COPYRIGHT__

This subdirectory contains a harness and various timing tests that we've
used to decide on the most efficient implementation of various pieces
of the code base.  We're checking these in here so that they're always
available in case we have to revisit these decisions.

NOTE:  This harness is for horse-racing specific snippets of Python
code to select the best implementation to use within a given function
or subsystem.  It's not intended for end-to-end testing of SCons itself.

Contents of the directory:

    README.txt

        What you're reading right now.

    bench.py

        The harness for running the timing tests that make up
        the rest of the directory's contents.  Use it to run
        one of the timing tests as follows:

                python bench.py FILE

        Various command-line options control the number of runs, the
        number of iterations on each run, etc.  Help for the command-line
        options is available:

                python bench.py -h

    is_types.py
    lvars-gvars.py
    [etc.]

        The rest of the files in this directory should each contain a
        specific timing test, consisting of various functions to be run
        against each other, and test data to be passed to the functions.

        Yes, this list of files will get out of date.
