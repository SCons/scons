# SCons Architecture

Read this when you need to find where something lives in the engine, or
before changing core behavior (nodes, signatures, scheduling, substitution).

## Core engine (`SCons/`)

- `Script/` - CLI entry point (`Main.py:main()`), option parsing (`SConsOptions.py`), SConscript execution.
- `Environment.py` - `Environment` class; construction variable management.
- `Builder.py` + `Action.py` - define how targets are built and what commands execute.
- `Node/` - dependency graph: `FS.py` (File, Dir, Entry), `Alias.py`, `Python.py`.
- `Taskmaster/` - parallel job scheduling and task execution.
- `SConsign.py` - `.sconsign.dblite` persistence (by default a single file at the build top, keyed by dir path).
- `Subst.py` - variable substitution (`$CC`, `$CFLAGS`, etc.).
- `Scanner/` - dependency scanners (C/C++ `#include`, etc.).
- `CacheDir.py` - shared build-artifact cache.
- `SConf.py` - `Configure()` logic.
- `Warnings.py` - warning hierarchy (stderr via `warn()`).
- `Tool/` - compiler/linker integrations (CC, CXX, MSVC, Ninja, Docbook, etc.).

## Behavior worth knowing

- `.sconsign.dblite` persists across builds; deleting build dirs from disk
  doesn't clear sconsign entries.
- `Configure()` writes its log to `$CONFIGURELOG`, default `#/config.log`
  (top of the project).

## CI

- GitHub Actions: `runtest.yml` (test suite), `runtest-next.yml`
  (pre-release Python, non-blocking), `scons-package.yml` (packaging).
- AppVeyor (Windows): `.appveyor.yml`, scripts in `.appveyor/`.
