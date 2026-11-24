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
After any documentation change, run all three scripts in this order -
`docs-validate.py` alone is not enough:

```bash
python bin/docs-update-generated.py         # regenerate doc/generated/*.mod, *.gen
python bin/docs-validate.py                 # validate XML against the SCons schema
python bin/docs-create-example-outputs.py   # rerun User Guide examples -> doc/generated/examples
```

Then check that the docs actually build:

```bash
python scripts/scons.py doc SKIP_DOC=pdf,api
```

`git diff doc/generated/examples` shows whether your change altered any
example output; some diffs are system-specific noise (see
`doc/overview.rst`).

- Individual XML files are not syntactically complete DocBook; they need the
  xincluded `.mod` and `.gen` files (from `doc` and `doc/generated`), the
  schema extension, and the framework in `bin/SConsDoc.py` (which also
  documents some of the extensions).
- Files in `doc/generated/` are produced by the scripts above and must never
  be edited directly. Project convention is *not* to commit changes to
  generated files as they happen; accumulated changes are committed during
  the release process. So run the scripts to verify your change, but don't
  stage the resulting `doc/generated/` changes.
