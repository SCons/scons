"""SCons.Scanner.C

This module implements the depenency scanner for C/C++ code. 

"""

__revision__ = "Scanner/C.py __REVISION__ __DATE__ __DEVELOPER__"


import SCons.Scanner
import re
import os.path

angle_re = re.compile('^[ \t]*#[ \t]*include[ \t]+<([\\w./\\\\]+)>', re.M)
quote_re = re.compile('^[ \t]*#[ \t]*include[ \t]+"([\\w./\\\\]+)"', re.M)

def CScan():
    "Return a Scanner instance for scanning C/C++ source files"
    return SCons.Scanner.Scanner(scan)

def find_files(filenames, paths):
    """
    find_files([str], [str]) -> [str]

    filenames - a list of filenames to find
    paths - a list of paths to search in

    returns - the fullnames of the files

    Only the first fullname found is returned for each filename, and any
    file that aren't found are ignored.
    """
    fullnames = []
    for filename in filenames:
        for path in paths:
            fullname = os.path.join(path, filename)
            if os.path.exists(fullname):
                fullnames.append(fullname)
                break

    return fullnames

def scan(filename, env):
    """
    scan(str, Environment) -> [str]

    the C/C++ dependency scanner function

    This function is intentionally simple. There are two rules it
    follows:
    
    1) #include <foo.h> - search for foo.h in CPPPATH followed by the
        directory 'filename' is in
    2) #include \"foo.h\" - search for foo.h in the directory 'filename' is
       in followed by CPPPATH

    These rules approximate the behaviour of most C/C++ compilers.

    This scanner also ignores #ifdef and other preprocessor conditionals, so
    it may find more depencies than there really are, but it never misses
    dependencies.
    """

    if hasattr(env, "CPPPATH"):
        paths = env.CPPPATH
    else:
        paths = []
        
    file = open(filename)
    contents = file.read()
    file.close()

    angle_includes = angle_re.findall(contents)
    quote_includes = quote_re.findall(contents)

    source_dir = os.path.dirname(filename)
    
    deps = (find_files(angle_includes, paths + [source_dir])
            + find_files(quote_includes, [source_dir] + paths))

    return deps

    
    
    

    
