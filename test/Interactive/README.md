Testing interactive mode is tricky.

In the tests, commands are issued to the interactive shell by first
opening a session with test.start(), then user typing is simulated by
doing test.send(text).

Computers move faster than humans, so control returns to the test program
immediately after a send() - probably long before SCons has executed
the requested command. Since you want to check outcomes, it's necessary
to busy-wait until the operation has completed. The framework provides
test.wait_for() for this purpose - it doesn't return until the requested
path exists, so it's good for actions which cause a file to be created.

Unfortunately, waiting on certain actions seems to be unreliable, plus
some situations don't have direct support. For example, a test which
cleans then rebuilds doesn't have a way in the testing API to wait for
a file to not exist (clean). Based on recent experience, waiting for
a non-trivial build may not work either.  Past developers seem to have
run into this, so many tests employ a trick: in addition to the actual
testing targets, define rules for a couple of dummy targets:

    Command('1', [], Touch('$TARGET'))
    Command('2', [], Touch('$TARGET'))

Then, instead of waiting on the result of a step under test, immediately
issue a second command to build a dummy target, and wait on that target,
like in this sample from test/Interactive/Default.py:

    scons = test.start(arguments='-Q --interactive')
    scons.send("build\n")
    scons.send("build 1\n")
    test.wait_for(test.workpath('1'))
    test.must_match(test.workpath('foo.out'), "foo.in 1\n")

So while the first build should produce "foo.out", we don't wait for
that, but rather for the dummy file "1" from the second command; then
the condition test can be executed as normal.

It's not entirely clear why waiting for the "real" target is less
reliable, so just leaving this README as a breadcrumb for future
developers.
