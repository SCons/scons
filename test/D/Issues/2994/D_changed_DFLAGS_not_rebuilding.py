# Test to check for issue reported in tigris bug 2994
# http://scons.tigris.org/issues/show_bug.cgi?id=2994
#

import TestSCons

test = TestSCons.TestSCons()

dmd_present = test.detect_tool('dmd', prog='dmd')
ldc_present = test.detect_tool('ldc',prog='ldc2')
gdc_present = test.detect_tool('gdc',prog='gdc')

if not (dmd_present or ldc_present or gdc_present):
    test.skip_test("Could not load dmd ldc or gdc Tool; skipping test(s).\n")


test.dir_fixture('image')
test.run()
test.fail_test('main.o' not in test.stdout())
test.run(arguments='change=1')
test.fail_test('is up to date' in test.stdout())

test.pass_test()
