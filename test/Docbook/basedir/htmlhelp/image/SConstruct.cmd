# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

DefaultEnvironment(tools=[])
env = Environment(DOCBOOK_PREFER_XSLTPROC=1, tools=['docbook'])
DOCBOOK_XSLTPROC = ARGUMENTS.get('DOCBOOK_XSLTPROC', "")
if DOCBOOK_XSLTPROC:
    env['DOCBOOK_XSLTPROC'] = DOCBOOK_XSLTPROC
env.Append(DOCBOOK_XSLTPROCFLAGS=['--novalid', '--nonet'])
env.DocbookHtmlhelp('manual', xsl='htmlhelp.xsl', base_dir='output/')

