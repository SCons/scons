# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Setup epydoc builder

Obsolete: epydoc no longer maintained.
"""

from SCons.Script import Delete, Touch, WhereIs

epydoc_cli = WhereIs('epydoc')

if not epydoc_cli:
    try:
        import epydoc
    except ImportError:
        epydoc = None
    else:
        # adding Epydoc builder using imported module
        def epydoc_builder_action(target, source, env):
            """
            Take a list of `source` files and build docs for them in
            `target` dir.

            `target` and `source` are lists.

            Uses OUTDIR and EPYDOCFLAGS environment variables.

            http://www.scons.org/doc/2.0.1/HTML/scons-user/x3594.html
            """

            # the epydoc build process is the following:
            # 1. build documentation index
            # 2. feed doc index to writer for docs

            from epydoc.docbuilder import build_doc_index
            from epydoc.docwriter.html import HTMLWriter
            # from epydoc.docwriter.latex import LatexWriter

            # first arg is a list where can be names of python package dirs,
            # python files, object names or objects itself
            docindex = build_doc_index([str(src) for src in source])
            if docindex is None:
                return -1

            if env['EPYDOCFLAGS'] == '--html':
                html_writer = HTMLWriter(docindex,
                                         docformat='restructuredText',
                                         prj_name='SCons',
                                         prj_url='http://www.scons.org/')
                try:
                    html_writer.write(env['OUTDIR'])
                except OSError: # If directory cannot be created or any file cannot
                                # be created or written to.
                    return -2

            """
            # PDF support requires external Linux utilites, so it's not crossplatform.
            # Leaving for now.
            # http://epydoc.svn.sourceforge.net/viewvc/epydoc/trunk/epydoc/src/epydoc/cli.py

            elif env['EPYDOCFLAGS'] == '--pdf':
                pdf_writer = LatexWriter(docindex,
                                         docformat='restructuredText',
                                         prj_name='SCons',
                                         prj_url='http://www.scons.org/')
            """
            return 0

        epydoc_commands = [
            Delete('$OUTDIR'),
            epydoc_builder_action,
            Touch('$TARGET'),
        ]

else:
    # epydoc_cli is found
    epydoc_commands = [
        Delete('$OUTDIR'),
        '$EPYDOC $EPYDOCFLAGS --debug --output $OUTDIR --docformat=restructuredText --name SCons --url http://www.scons.org/ $SOURCES',
        Touch('$TARGET'),
    ]
