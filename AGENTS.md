# SCons - Software Construction Tool

Run all commands from the repo root. SCons runs straight from the source
tree; avoid having a separately installed `scons` in the same environment,
as it can shadow the tree you are testing. Python >= 3.9 required.

## Task guides - read before the matching task

| Before you... | Read |
|---|---|
| create or modify a test | [doc/ai/testing.md](doc/ai/testing.md) and `testing/framework/test-framework.rst` |
| change user-facing behavior, add builders/variables/functions/tools, or edit `doc/` | [doc/ai/documentation.md](doc/ai/documentation.md) |
| look for where something lives, or change core engine behavior | [doc/ai/architecture.md](doc/ai/architecture.md) |

## Build & Run

```bash
python scripts/scons.py            # build packages (wheels, tarballs, zips → build/)
python scripts/scons.py doc        # docs only
python scripts/scons.py [args]     # run SCons from source (no install needed)
```

## Dependencies

Development dependencies are PEP 735 `[dependency-groups]` in
`pyproject.toml` (not extras, so `pip install scons[dev]` does not work):
`dev` for tests, `pkg` for `dev` plus packaging and doc tooling.

```bash
pip install --group dev              # pip >= 25.1 (or: uv sync --group dev)
pip install -r requirements-dev.txt  # equivalent, any pip
```

## Testing

```bash
python runtest.py SCons/SConfTests.py              # unit test
python runtest.py test/Configure/ConfigureDryRunError.py  # e2e test
python runtest.py test/Configure   # every test under a directory
python runtest.py -a -j 0          # all tests (~1400 e2e + unit), parallel
python runtest.py --retry          # re-run failures from the last run (failed_tests.log)
python runtest.py -l               # list tests without running
```

New features need tests; bug fixes need a regression test. A unit test alone
is enough if it fully covers the change. If verifying the change requires
running tools (real or mocked), add E2E tests too.

## Lint & Type

```bash
python -m ruff check .              # lint (target-version py39)
python -m ruff format --check .     # formatting check
python -m mypy SCons/               # type check
```

Ruff and mypy skip `test/`, `testing/`, `bin/`, `doc/` and others (see
`pyproject.toml`). `.editorconfig`: 4-space indent, 88-char lines for
Python/SConstruct/SConscript, LF line endings.

## Contributing Changes

- **Changelog:** every user-visible change needs entries in both
  `CHANGES.txt` and `RELEASE.txt`, in the unreleased section at the top,
  under a `From <Your Name>:` block (add one if missing). `NEWS.d/` is not
  in active use; don't add files there.
- **Commits:** sign off (`git commit -s`). For AI-assisted changes add an
  `Assisted-by:` trailer, e.g. `Assisted-by: <tool> (<model>)`. The human
  submitter is the author and is responsible for the change (see the AI
  section of `CONTRIBUTING.rst`).
- **PR checklist** (`.github/PULL_REQUEST_TEMPLATE.md`): tests added/updated,
  `CHANGES.txt` + `RELEASE.txt` updated, docs updated.
- **Don't edit:** `__version__` in `SCons/__init__.py` (release process
  only) or files in `doc/generated/` (regenerated at release).
