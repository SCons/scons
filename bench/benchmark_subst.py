#!/usr/bin/env python
"""
Performance benchmark for SCons.Subst optimizations.

Measures the impact of:
1. Dictionary merge consolidation (scons_subst)
2. Callable signature caching with lru_cache
3. Action hashability for cache efficiency
"""

import timeit
import sys
from SCons.Environment import Environment
from SCons.Action import CommandAction, FunctionAction

def benchmark_basic_subst():
    """Benchmark basic variable substitution."""
    env = Environment(CC='gcc', CCFLAGS='-O2', TARGET='prog', SOURCE='main.c')

    setup = """
from SCons.Environment import Environment
env = Environment(CC='gcc', CCFLAGS='-O2', TARGET='prog', SOURCE='main.c')
"""

    stmt = "env.subst('$CC $CCFLAGS -c -o $TARGET $SOURCE')"

    time_taken = timeit.timeit(stmt, setup=setup, number=10000)
    return time_taken

def benchmark_callable_subst():
    """Benchmark substitution with callable construction variables."""
    def my_func(target, source, env, for_signature):
        return "result"

    setup = """
from SCons.Environment import Environment
def my_func(target, source, env, for_signature):
    return "result"
env = Environment(MYVAR=my_func, CC='gcc')
"""

    # Multiple substitutions with the same callable to exercise caching
    stmt = """
for i in range(5):
    env.subst('$MYVAR $CC')
"""

    time_taken = timeit.timeit(stmt, setup=setup, number=1000)
    return time_taken

def benchmark_action_in_subst():
    """Benchmark substitution when construction variables contain Action objects."""
    setup = """
from SCons.Environment import Environment
from SCons.Action import CommandAction, FunctionAction
def my_action(target, source, env):
    return 0
env = Environment()
env['CMD_ACTION'] = CommandAction('echo test')
env['FUNC_ACTION'] = FunctionAction(my_action, {})
"""

    stmt = """
for i in range(3):
    env.subst('$CMD_ACTION $FUNC_ACTION')
"""

    time_taken = timeit.timeit(stmt, setup=setup, number=500)
    return time_taken

def benchmark_subst_list():
    """Benchmark subst_list with multiple variables."""
    setup = """
from SCons.Environment import Environment
env = Environment(
    CC='gcc',
    CCFLAGS=['-O2', '-Wall'],
    CPPDEFINES=['DEBUG', 'VERSION=1'],
    LIBPATH=['/usr/lib', '/usr/local/lib'],
)
"""

    stmt = "env.subst_list('$CC $CCFLAGS $CPPDEFINES -L$LIBPATH')"

    time_taken = timeit.timeit(stmt, setup=setup, number=5000)
    return time_taken

def benchmark_repeated_callables():
    """Benchmark repeated calls with same callable to measure cache benefit."""
    setup = """
from SCons.Environment import Environment
import SCons.Subst

# Create a callable to use
def expensive_func(target, source, env, for_signature):
    return "cached_result"

env = Environment(MYVAR=expensive_func)

# Clear the cache to start fresh
SCons.Subst._callable_matches_subst_args.cache_clear()
"""

    # Repeated substitutions with the same callable
    stmt = """
for i in range(100):
    env.subst('$MYVAR')
"""

    time_taken = timeit.timeit(stmt, setup=setup, number=100)
    return time_taken

if __name__ == '__main__':
    print("SCons.Subst Performance Benchmark")
    print("=" * 60)
    print()

    # Warm up
    benchmark_basic_subst()

    benchmarks = [
        ("Basic substitution (10k iterations)", benchmark_basic_subst),
        ("Callable substitution (1k iterations)", benchmark_callable_subst),
        ("Action in substitution (500 iterations)", benchmark_action_in_subst),
        ("Subst_list with multiple vars (5k iterations)", benchmark_subst_list),
        ("Repeated callable caching (10k calls total)", benchmark_repeated_callables),
    ]

    results = []
    for name, func in benchmarks:
        try:
            time_taken = func()
            results.append((name, time_taken))
            print(f"{name}")
            print(f"  Time: {time_taken:.4f}s")
            print()
        except Exception as e:
            print(f"{name}")
            print(f"  ERROR: {e}")
            print()

    print("=" * 60)
    print("Summary:")
    total_time = sum(t for _, t in results)
    print(f"Total benchmark time: {total_time:.4f}s")
    print()
    print("Key improvements:")
    print("1. Dictionary merge consolidation: Avoids unnecessary copies")
    print("   when no TARGET/SOURCE vars or overrides are needed")
    print()
    print("2. lru_cache for callable signatures: Caches expensive")
    print("   inspect.signature() calls with bounded memory (256 entries)")
    print()
    print("3. Action hashability: Makes all Action objects usable in")
    print("   caches and sets, enabling better optimization")
