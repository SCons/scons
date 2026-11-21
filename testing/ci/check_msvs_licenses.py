#!/usr/bin/env python
"""
Probe installed MSVS/MSVC versions for expired or invalid licenses.

For each installed Visual Studio version, attempts to build a minimal C program
using devenv/msdev. If the build fails, treats it as a likely license expiry
issue and prints the corresponding test file path (test/MSVS/vs-{version}-exec.py)
to stdout, one per line.

Output contract: plain stdout, one relative test path per line, on success.
Diagnostic messages go to stderr.

Usage:
  python testing/ci/check_msvs_licenses.py
  # Output: (empty if all licenses valid, or)
  # test/MSVS/vs-10.0-exec.py
  # test/MSVS/vs-14.3-exec.py
  # (etc. for any versions with expired/invalid licenses)
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _setup_sys_path():
    """Add the repo root to sys.path so SCons modules can be imported."""
    # <scons_root>/testing/ci/check_msvs_licenses.py
    syspathdir = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.insert(0, syspathdir)


def _get_version_info(version):
    """
    Determine project file extension and devenv/msdev build arguments for a version.

    Returns: (ext, [build_args...])
    - ext: 'dsp' for legacy msdev, 'vcproj' for VS8-9, 'vcxproj' for VS10+
    - build_args: list of arguments for devenv/msdev /build command
    """
    version_num = float(version.split('.')[0])
    if version_num < 8.0:
        return 'dsp', ['foo.dsp', '/MAKE', 'foo - Win32 Release']
    elif version_num < 10.0:
        return 'vcproj', ['foo.sln', '/build', 'Release']
    else:
        return 'vcxproj', ['foo.sln', '/build', 'Release']


def _probe_version(version, executable, scons_py, repo_root):
    """
    Probe whether a given MSVS version can successfully build a C program.

    Returns True if the build succeeds (license likely valid), False otherwise.
    """
    ext, build_args = _get_version_info(version)

    with tempfile.TemporaryDirectory() as workdir:
        probe_dir = Path(workdir)

        # Write minimal SConstruct to generate the project file
        scons_construct = f"""\
env = Environment(MSVS_VERSION='{version}')
env.MSVSProject(
    target='foo.{ext}',
    srcs=['foo.c'],
    buildtarget='foo.exe',
    variant='Release',
)
env.Program('foo.c')
"""
        (probe_dir / 'SConstruct').write_text(scons_construct)
        (probe_dir / 'foo.c').write_text('int main(void) { return 0; }\n')

        # Run SCons to generate the project file
        try:
            result = subprocess.run(
                [sys.executable, str(scons_py), '.'],
                cwd=str(probe_dir),
                capture_output=True,
                timeout=60,
            )
            if result.returncode != 0:
                return False
        except (subprocess.TimeoutExpired, Exception) as e:
            sys.stderr.write(f"Error generating project for {version}: {e}\n")
            return False

        # Run devenv/msdev to build the project
        try:
            result = subprocess.run(
                [str(executable)] + build_args,
                cwd=str(probe_dir),
                capture_output=True,
                timeout=120,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception) as e:
            sys.stderr.write(f"Error building with {version}: {e}\n")
            return False


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()

    # Set up sys.path to import SCons modules
    _setup_sys_path()

    try:
        from SCons.Tool.MSCommon.vs import query_versions, get_vs_by_version
    except ImportError as e:
        sys.stderr.write(f"Failed to import SCons modules: {e}\n")
        return 1

    repo_root = Path(__file__).parent.parent.parent.resolve()
    scons_py = repo_root / 'scripts' / 'scons.py'
    if not scons_py.exists():
        sys.stderr.write(f"scons.py not found at {scons_py}\n")
        return 1

    # Enumerate installed MSVS versions
    try:
        versions = query_versions()
    except Exception as e:
        sys.stderr.write(f"Failed to query installed MSVS versions: {e}\n")
        return 1

    if not versions:
        # No MSVS installed; nothing to exclude
        return 0

    # For each version, probe and collect unusable ones
    unusable_versions = []
    for version in versions:
        # Check if a test file exists for this version
        test_file = repo_root / 'test' / 'MSVS' / f'vs-{version}-exec.py'
        if not test_file.exists():
            # No test file for this version; skip
            continue

        try:
            msvs = get_vs_by_version(version)
            if not msvs:
                continue
            executable = msvs.get_executable()
            if not executable:
                continue
        except Exception as e:
            sys.stderr.write(f"Error resolving executable for {version}: {e}\n")
            continue

        # Probe the version
        if not _probe_version(version, executable, scons_py, repo_root):
            unusable_versions.append(version)

    # Print test paths for unusable versions
    for version in unusable_versions:
        print(f'test/MSVS/vs-{version}-exec.py')

    return 0


if __name__ == '__main__':
    sys.exit(main())
