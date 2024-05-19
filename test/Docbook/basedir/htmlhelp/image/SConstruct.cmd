# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

DefaultEnvironment(tools=[])
env = Environment(DOCBOOK_PREFER_XSLTPROC=1, tools=['docbook'])
env.DocbookHtmlhelp('manual', xsl='htmlhelp.xsl', base_dir='output/')

