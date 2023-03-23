#!/usr/bin/python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Mock yacc/bison command for testing yacc tool with options
"""

import argparse
import os
import sys
from pathlib import Path


# Sentinels to make sure we pick the defaults
HEADER_DEFAULT = "_header_compute"
GRAPH_DEFAULT = "_graph_compute"
REPORT_DEFAULT = "_report_compute"


def make_side_effect(path, text, outfile):
    if path == HEADER_DEFAULT:
        file, ext = os.path.splitext(outfile)
        if ext in [".y", ".yacc"]:
            path = file + ".h"
        elif ext in [".ym"]:
            path = file + ".h.m"
        elif ext in [".yy"]:
            path = file + ".hpp"
        else:  # just guess
            path = file + ".h"
    if path == GRAPH_DEFAULT:
        path = os.path.splitext(outfile)[0] + ".gv"
    if path == REPORT_DEFAULT:
        path = os.path.splitext(outfile)[0] + ".output"

    p = Path(path)
    if str(p.parent) != ".":
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open(mode="wb") as f:
        f.write(text)


def fake_yacc():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("-g", "--graph", nargs="?", const=GRAPH_DEFAULT)
    parser.add_argument("-d", dest="graph", action="store_const", const=HEADER_DEFAULT)
    parser.add_argument("-v", "--verbose", action="store_const", const=REPORT_DEFAULT)
    parser.add_argument("-x", action="store_true")  # accept, do nothing
    parser.add_argument("-H", "--header", "--defines", nargs="?", const=HEADER_DEFAULT)
    parser.add_argument("-o", "--output", dest="out", required=True)
    parser.add_argument("-I", dest="i_arguments", default=[], action="append")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    # print(f"DEBUG: {args}")

    # Synthesize "opt_string", which, when this script used getopt, was
    # collected in the arg processing loop - from some arguments. The tests
    # expect this to be subbed in for YACCFLAGS in making the output file.
    opt_list = []
    skip = False
    for arg in sys.argv[1:]:
        if skip:
            skip = False
        elif arg == "-o":
            skip = True
        elif arg.startswith("-I"):
            pass
        else:
            opt_list.append(arg)
    # The original didn't use the file argument(s) so we have to get rid of.
    for file in args.files:
        if file in opt_list:
            opt_list.remove(file)
    opt_string = " ".join(opt_list)

    # Now we need to do something similar for i_arguments, which is easier
    i_arguments = " ".join(args.i_arguments)

    with open(args.out, "wb") as ofp:
        for file in args.files:
            with open(file, "rb") as ifp:
                contents = ifp.read()
            contents = contents.replace(b"YACCFLAGS", opt_string.encode())
            contents = contents.replace(b"YACC", b"myyacc.py")
            contents = contents.replace(b"I_ARGS", i_arguments.encode())
            ofp.write(contents)

    # Make extra output files
    if args.header:
        make_side_effect(args.header, b"yacc header\n", args.out)
    if args.graph:
        make_side_effect(args.graph, b"yacc graph\n", args.out)
    if args.verbose:
        make_side_effect(args.verbose, b"yacc debug\n", args.out)


if __name__ == "__main__":
    fake_yacc()
    sys.exit(0)
