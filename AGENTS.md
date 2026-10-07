# AGENTS.md

Context file for AI agents working on scons.

**Dual Format**: This file combines Category A (Operations Manual) and Category B (Context Guide) for comprehensive agent guidance.

## Project Overview

scons is a Python project using Python (setuptools).

**Key Info:**
- **Primary Language:** Python
- **Build System:** Python (setuptools)
- **Test Framework:** unittest
- **Total Files:** 4396
- **Test Files:** 1811
- **AI Readiness Score:** 93/100 (Agent-Optimized)

---

## 🚨 AI Policy & Operations

Extracted from CONTRIBUTING.md - operational constraints and procedures.

### AI Policy

- `SCons Developer's Guidelines <https://scons.org/guidelines.html>`_
- standard described at https://spec.editorconfig.org/. Many editors
- will use this file by default, and apply the editing standards
- described therein.  Many other editors do know about the standard,
- of translating to pure docbook, then using standard tools to

### Key Requirements

- as there is a web interface (does require an account).
- don't need to worry about the packaging parts when working
- new file, then the packaging bits may need to know about it.
- but require some configuration to enable enforcement. There's a
- to see the editors that require a plugin.  Be aware those lists

### Development Procedures

- of forms: a Python-installable package (source distribution
- and installable wheel file, which get uploaded to the Python
- There are also tests and tools in the tree.
- The *full* development cycle is not just to test code changes directly,
- but also to package SCons, unpack the package, install SCons in a test

### Known Workarounds & Caveats

- workarounds for the problem you are running into::



## 🏗️ Architecture & Context Guide

This section provides architectural context and agent-understanding for the codebase.

### Prerequisites

- **Python:** >=3.9 (or applicable language version)
- **Package Manager:** pip or uv
- **Test Runner:** unittest



### Project Structure

```
scons/
├── pyproject.toml
├── setup.py
├── Makefile
├── src/                  # Source code
├── tests/                # Test suite (1811 files)
└── README.md             # Project documentation
```

### Architecture Overview

#### Key Components
- **Main Entry:** main.c, main.js, main.js
- **Test Suite:** 1811 test files
- **Build Configuration:** pyproject.toml, setup.py, Makefile

#### Design Principles

1. **Modularity** - Code organized by functionality with clear separation of concerns
2. **Testability** - Comprehensive test coverage across critical paths
3. **Clarity** - Explicit naming and structure for AI agent understanding
4. **Consistency** - Uniform patterns and conventions throughout codebase
5. **Maintainability** - Well-documented code with clear intent

### Directory Map

| Directory | Purpose |
|-----------|----------|
| `scripts/` | Build and utility scripts |
| `src/` | Source code |
| `test/` | Test suite |


### Development Workflow

#### Initial Setup

```bash
git clone https://github.com/scons/scons.git
cd scons
pip install -e .
```

#### Development Commands

**Running Tests:**
```bash
python3 -m unittest discover  # Run all tests
python3 -m unittest test_module.TestClass  # Run specific test
python3 -m unittest -v        # Verbose output
```

#### Code Quality
```bash
# Format and lint tools (if configured)
# ruff check .              # Check code style
# ruff format .             # Format code
```

### Code Style & Conventions

- **Naming:** Use Python conventions (snake_case for functions, PascalCase for classes)
- **Type Hints:** Yes (strongly encouraged)
- **Error Handling:** Yes - handle errors at boundaries; let exceptions propagate when another layer owns recovery
- **Logging:** Yes
- **Testing:** Yes - write tests alongside code changes

### Testing Strategy

**Framework:** unittest
**Test Files:** 1811 found

Before committing:
1. Run the full test suite: `pytest`
2. Ensure all tests pass
3. Check type hints: `mypy .`
4. Format code: `ruff format .`

### Writing Documentation

When updating docs:
1. Always include explanatory text before code snippets
2. Describe *why* and *what* before showing *how*
3. Keep sections focused on a single concept
4. Use clear, concrete examples

## Known Gotchas & Warnings

- There are lots of places we could use help - please don't
- to chat.  You don't have to use the Discord app,
- don't need to worry about the packaging parts when working
- you don't actually need to build or install SCons; you just edit and
- Since SCons is written entirely in Python, you don't have to "build"
- which will build and package SCons itself, which you probably don't want
- to this editable version, and you don't have to be "in" this tree
- development cycle to validate that your changes don't break existing
- you submit to SCons don't break existing functionality and have adequate
- If you don't have SCons already installed on your system,

### Contributing Guidelines

This project has a detailed contribution guide at **`CONTRIBUTING.rst`**.

**Key Requirements:**
- **DCO Sign-off Required**: Every commit must be signed with `git commit -s`
- **Performance Work**: Requires benchmarks and performance metrics in PR description

**Before submitting:**
1. Read `CONTRIBUTING.rst` in full
2. Check recent merged PRs for patterns
3. Follow the specific requirements above

### Common Patterns

When contributing to this project:
1. Read existing code in the area you're modifying
2. Follow the established patterns and style
3. Write tests for new functionality
4. Use clear, descriptive variable and function names
5. Add docstrings for public APIs
6. Update tests when changing behavior

### What We Value

✅ Well-tested code with clear intent
✅ Consistent code style and naming conventions
✅ Code that is easy for AI agents to understand
✅ Clear, descriptive commit messages
✅ Modular, reusable components
✅ Comprehensive documentation

### What We Avoid

❌ Large functions doing multiple things
❌ Commented-out dead code
❌ Inconsistent naming or patterns
❌ Unclear error messages
❌ Unexplained magic numbers or strings
❌ Skipped tests or test TODOs

### AI Readiness Dimensions (Scoring)

This project is evaluated across 8 dimensions:

1. **Architecture** (20/100) - Code organization and modularity
2. **Testing** (15/100) - Test coverage and quality
3. **Dependencies** (12/100) - Dependency management
4. **Conventions** (8/100) - Consistent patterns
5. **Entry Points** (10/100) - Clear main/start locations
6. **Security** (10/100) - Input validation and error handling
7. **Build** (10/100) - Clear build/setup instructions
8. **Documentation** (8/100) - Code and project documentation

### Next Steps

Before making changes:
1. Read relevant source files to understand the existing code
2. Look at existing tests for similar functionality
3. Follow the patterns you see in the codebase
4. Write tests for your changes
5. Run `pytest` to verify nothing breaks
6. Run code quality checks: `ruff check . && mypy .`
7. Format your code: `ruff format .`

---

*Generated by Braxis - keeping AI agents in sync with your code*

