# SCons - Software Construction Tool

## Build & Run

```bash
python scripts/scons.py            # build packages (wheels, tarballs, zips → build/)
python scripts/scons.py doc        # docs only
python scripts/scons.py [args]     # run SCons from source (no install needed)
```
SCons builds itself. The repo root `SConstruct` is the build script for packaging.

## Testing

```bash
python runtest.py -a               # all tests
python runtest.py SCons/SConfTests.py              # unit test
python runtest.py test/Configure/ConfigureDryRunError.py  # e2e test
python runtest.py --retry          # re-run last failures (reads failed_tests.log)
python runtest.py -j 0             # parallel (cpu_count)
python runtest.py -t               # print timing
```

For more complete testing, the dependency set `[dev]` from `pyproject.toml`
is useful.

```bash
python bin/docs-validate.py
python scripts/scons.py doc SKIP_DOC=pdf,api
```

| Type | Location | Pattern |
|------|----------|---------|
| E2E  | `test/**/*.py` | Custom `TestSCons` (subclass of `TestCmd`) with `test.run()` / `test.pass_test()` |
| Unit | `SCons/*Tests.py` | Standard `unittest.TestCase`, also use `TestCmd`/`TestSCons` for setup |

The test runner (`runtest.py`) adds `SCons/` and `testing/` to `PYTHONPATH` automatically. E2E tests create a temp workdir per run. Use `SCons.Debug.Trace()` for print debugging (won't interfere with test output capture).

## Codebase Architecture

**Core engine (`SCons/`):**
- `Script/Main.py` - entry point (`main()`).
- `Environment.py` - `Environment` class; construction variable management.
- `Builder.py` + `Action.py` - define how targets are built and what commands execute.
- `Node/` — dependency graph: `FS.py` (File, Dir, Entry), `Alias.py`, `Python.py`.
- `Taskmaster/` - parallel job scheduling and task execution.
- `SConsign.py` - `.sconsign.dblite` persistence (single file at build top, keyed by dir path).
- `Subst.py` - variable substitution (`$CC`, `$CFLAGS`, etc.).
- `Scanner/` - dependency scanners (C/C++ `#include`, etc.).
- `CacheDir.py` - shared build-artifact cache.
- `SConf.py` - `Configure()` logic.
- `Warnings.py` - warning hierarchy (stderr via `warn()`).
- `Tool/` - compiler/linker integrations (CC, CXX, MSVC, Ninja, Docbook, etc.).
- `Script/` - CLI entry points, option parsing (`SConsOptions.py`).
- `Platform/` - OS-specific adaptations.
- `Variables/` - `PathVariable`, `BoolVariable`, etc., for build configuration.

**Tests:**
- `testing/framework/` — `TestSCons.py`, `TestCmd.py` (e2e test base classes).
- `test/` — ~200+ e2e tests organized by feature.
- `SCons/*Tests.py` — unit tests alongside source, standard `unittest.TestCase`.

**Documentation:**
-  `doc` documentation sources, tools, extended DocBook schema
-  `SCons/*.xml` - module-specific documentation sources

## Documentation

The doc build requires the dependency set `[doc]` from `pyproject.toml`.
For validating just that the Docbook xml documents build, use

```bash
python bin/docs-validate.py
python scripts/scons.py doc SKIP_DOC=pdf,api
```

Individual xml files are not syntactically complete DocBook,
they require the context of xincluded files (`.mod` and `.gen`
from `doc` and `doc/generated`), the SCons schema extension
(`doc/xsd`), and the framework from `bin/SConsDoc.py`,
which also contains information on some of the extensions.

## Lint & Type

```bash
python -m ruff check .              # lint (target-version py37, skips test/ bench/ doc/ etc.)
python -m ruff format --check .     # formatting check
python -m mypy SCons/               # type check
```

`.editorconfig` enforces: indent 4 spaces, 88-char line limit (Python/SConstruct/SConscript), LF line endings, trailing comma, parentheses for multiline.

## Conventions

- Git commits signed off (`git commit -s`). Add `Assisted-by:` to message for AI-generated changes.
- Version in `SCons/__init__.py` (`__version__`) - automatically generated, do not edit.
- CI: GitHub Actions (`runtest.yml` - test suite; `scons-package.yml` — packaging), AppVeyor (Windows, legacy).
- Python >= 3.7 required.
- Config log for `Configure()` lives at `config.log` in the build dir.
- `.sconsign.dblite` persists across builds; deleting build dirs from disk doesn't clear sconsign entries.
