import argparse
import os
import sys
import time

def _scons_msvc_cache(skip_populate=False, skip_display=False):

    # <scons_root>/testing/ci/script.py
    syspathdir = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.insert(0, syspathdir)

    from SCons.Environment import Environment
    from SCons.Tool.MSCommon.common import CONFIG_CACHE

    if not skip_populate:
        Environment(tools=["msvc"])

    if not skip_display:
        print(f"SCONS_CACHE_MSVC_CONFIG={CONFIG_CACHE!r}")
        if os.path.exists(CONFIG_CACHE):
            with open(CONFIG_CACHE, "r") as fh:
                for line in fh:
                    sys.stdout.write(line)
                print()

def _setup():

    if not sys.platform.startswith("win32"):
        return

    if not os.environ.get("SCONS_CACHE_MSVC_CONFIG"):
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-populate", action="store_true", default=False, dest="skip_populate")
    parser.add_argument("--skip-display", action="store_true", default=False, dest="skip_display")

    args = parser.parse_args()

    try:
        _scons_msvc_cache(skip_populate=args.skip_populate, skip_display=args.skip_display)
    except Exception as e:
        print(f"exception: {type(e).__name__}")

if __name__ == "__main__":
    beg_time = time.time()
    _setup()
    print(f"Execution time: {time.time() - beg_time:.1f} seconds")
