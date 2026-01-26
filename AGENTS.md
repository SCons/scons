# SCons - Software Construction Tool

## Project Overview
SCons is an open-source software construction tool (build tool) implemented in Python. It is designed to be easier to use and more reliable than the traditional `make` utility. SCons configuration files are Python scripts, allowing users to use the full power of Python to solve build problems.

**Key Features:**
*   Configuration files are Python scripts.
*   Built-in support for C, C++, D, Java, Fortran, Yacc, Lex, Qt, SWIG, and TeX/LaTeX.
*   Reliable dependency analysis (implicit and explicit).
*   Support for parallel builds.
*   Cross-platform (Linux, POSIX, Windows, macOS).

## Building and Running

### Prerequisites
*   Python 3.7 or higher.
*   Development dependencies: `python -m pip install -r requirements-dev.txt`

### Running SCons (Development)
You do not need to install SCons to run it from the source tree.

**Linux/macOS:**
```bash
python scripts/scons.py [arguments]
```

**Windows:**
```cmd
py -3 scripts\scons.py [arguments]
```

### Building SCons
SCons uses itself to build its own packages.

**Full Build (Packages & Docs):**
```bash
python scripts/scons.py
```
This produces artifacts (wheels, tarballs, zips) in the `build/` directory.

**Build Documentation Only:**
```bash
python scripts/scons.py doc
```

## Testing
The project uses a custom test runner script, `runtest.py`.

**Run All Tests:**
```bash
python runtest.py -a
```

**Run Specific Tests:**
```bash
python runtest.py SCons/BuilderTests.py       # Unit test
python runtest.py test/option/option-j.py     # End-to-end test
```

**Run Failed Tests (Retry):**
```bash
python runtest.py --retry
```

**Test Types:**
*   **Unit Tests:** Located in `SCons/` alongside the source files (e.g., `SCons/Builder.py` -> `SCons/BuilderTests.py`).
*   **End-to-End Tests:** Located in the `test/` directory. These run SCons against sample projects.

## Development Conventions

*   **Code Style:** Follows Python PEP 8 (mostly). The project includes a `.editorconfig` file.
*   **Version Control:** Git is used. Commits should be signed off (`git commit -s`).
*   **Debugging:**
    *   Use `--debug=pdb` when running SCons to drop into the Python debugger.
    *   Use `SCons.Debug.Trace()` for print debugging in a way that doesn't interfere with test output capturing.
*   **Directory Structure:**
    *   `SCons/`: Core engine source code and unit tests.
    *   `test/`: End-to-end system tests.
    *   `scripts/`: Wrapper scripts (e.g., `scons.py`).
    *   `bin/`: Development utilities.
    *   `doc/`: Documentation source (DocBook/XML).
    *   `template/`: Templates for file generation.
    *   `testing/framework`: Test framework used by the end-to-end tests.

## AI Contribution Policy
If contributing AI-generated code:
1.  You take full responsibility for the code quality and license.
2.  Disclose AI use in the commit message (e.g., `Assisted-by: ModelName`).
