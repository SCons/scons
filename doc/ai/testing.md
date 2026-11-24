# Testing SCons

Read this, and `testing/framework/test-framework.rst`, before creating or
modifying a test.

## Test types

| Type | Location | Pattern |
|------|----------|---------|
| E2E  | `test/**/*.py` (~1400 files, ~200 feature dirs) | `TestSCons` (subclass of `TestCmd`): `test.file_fixture()` / `dir_fixture()`, `test.run()`, `test.must_match()` / `must_contain()` / `must_exist()`, `test.pass_test()` |
| Unit | `SCons/**/*Tests.py` | Standard `unittest.TestCase` alongside the module; may use `TestCmd`/`TestSCons` for setup |

- `runtest.py` adds `SCons/` and `testing/` to `PYTHONPATH` automatically.
- E2E tests run in a fresh temp workdir per test.
- Test framework sources: `testing/framework/` - `TestSCons.py`,
  `TestCommon.py`, `TestCmd.py`.

## Rules

- New features need tests; bug fixes need a regression test.
- **Unit vs. E2E:** if a unit test can fully cover the change, that is
  sufficient. If verifying the change requires running tools - real ones,
  or mocks such as the fake compilers/linkers in `test/fixture/`
  (`mycompile.py`, `mylink.py`, ...) - add E2E tests, alongside unit tests
  where those are also useful.
- Tests needing an external tool (compiler, etc.) must check for it
  (`test.where_is()`) and call `test.skip_test()` if absent - never assume it
  is installed. Many e2e tests skip on a given platform; that is normal.
- Use `SCons.Debug.Trace()` for print debugging (won't interfere with test
  output capture).

## Fixtures

Put static test inputs (`SConstruct`, sources, helper scripts) in fixture
files instead of having the test write them with `test.write()`:

- **3 or fewer files:** keep them in a `fixture/` directory next to the test
  and copy each with `test.file_fixture()`, e.g.
  `test.file_fixture('fixture/SConstruct-foo', 'SConstruct')`.
- **More than 3 files:** put them in a directory named after the test inside
  that `fixture/` directory and copy it with `test.dir_fixture()`, e.g.
  `test/Foo/bar.py` uses `test.dir_fixture('fixture/bar')`.
- **Content that depends on test-time values** (e.g. `_python_`): first try
  keeping the file a static fixture and passing the value at run time, e.g.
  `ARGUMENTS.get('PYTHON')` in the `SConstruct` plus
  `test.run(arguments=f'PYTHON={_python_}')` (see "When not to use a
  fixture" in `test-framework.rst`). Fall back to `test.write()` for that
  file only if that's impractical; the test's other static files still go in
  fixtures.
- **Building strings with run-time content** (when a static fixture or
  passing the value via `ARGUMENTS` doesn't work): prefer f-strings over
  the older `"""...%(name)s...""" % locals()` style, even though most
  existing tests still use the old style. Fall back to `%`-formatting when an
  f-string would need lots of doubled braces, e.g. SConstruct text full of
  `${TARGET}`-style substitutions or dict literals. Python 3.9 (the minimum)
  also forbids reusing the enclosing quote character or backslashes inside
  f-string expressions.
- **Existing tests that write their files inline:** don't convert them to
  fixtures on your own; ask the user first.
- `runtest.py` collects every `*.py` under `test/` as a test. If a fixture
  directory contains `.py` files, add `sconstest.skip` (skip the whole
  directory) or list them in `.exclude_tests` (see "Selecting tests" in
  `test-framework.rst`).
