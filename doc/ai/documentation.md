# SCons Documentation

Read this before changing user-facing behavior, adding builders,
construction variables, functions or tools, or editing anything under `doc/`.

## Where docs live

- User-facing docs for a module live in an `.xml` file next to it
  (e.g. `SCons/Environment.xml`, `SCons/Tool/gcc.xml`). New builders,
  construction variables, functions and tools are documented there, not in
  `doc/generated/`.
- `doc/` holds the user guide (`doc/user`), man page (`doc/man`), tooling and
  the extended DocBook schema (`doc/xsd`). `doc/overview.rst` describes the
  toolchain.
- `doc/generated/scons-ai.md` is the man page rendered as Markdown. It is
  large (~500 KB): search it for the documented behavior of a function,
  option or construction variable rather than reading it whole.

## Building and validating

The doc build requires the `pkg` dependency group (`requirements-pkg.txt`).
To validate that the DocBook XML builds:

```bash
python bin/docs-validate.py
python scripts/scons.py doc SKIP_DOC=pdf,api
```

- Individual XML files are not syntactically complete DocBook; they need the
  xincluded `.mod` and `.gen` files (from `doc` and `doc/generated`), the
  schema extension, and the framework in `bin/SConsDoc.py` (which also
  documents some of the extensions).
- Files in `doc/generated/` are built on demand
  (`python bin/docs-update-generated.py`) and must never be edited directly.
  Project convention is *not* to commit changes to generated files as they
  happen; accumulated changes are committed during the release process.
