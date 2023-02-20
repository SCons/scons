# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

DefaultEnvironment(tools=[])
env = Environment(DOCBOOK_PREFER_XSLTPROC=1, tools=['docbook'])
env.DocbookHtmlChunked('manual', xsl='html.xsl', base_dir='output/')
