<?xml version='1.0'?>

<!--
SPDX-FileCopyrightText: Copyright The SCons Foundation (https://scons.org)
SPDX-License-Identifier: MIT
-->

<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fo="http://www.w3.org/1999/XSL/Format"
	version="1.0">

<xsl:import href="../../SCons/Tool/docbook/docbook-xsl-1.76.1/html/chunk.xsl"/>

<xsl:param name="base.dir" select="'scons-user/'"/>
<xsl:param name="l10n.gentext.default.language" select="'en'"/>
<xsl:param name="section.autolabel" select="1"/>
<xsl:param name="section.label.includes.component.label" select="1"/>
<xsl:param name="html.stylesheet" select="'scons.css'"/>
<xsl:param name="generate.toc">
/appendix toc,title
article/appendix  nop
/article  toc,title
book      toc,title,figure,table,example,equation
/chapter  toc,title
part      toc,title
/preface  toc,title
reference toc,title
/sect1    toc
/sect2    toc
/sect3    toc
/sect4    toc
/sect5    toc
/section  toc
set       toc,title
</xsl:param>

<!-- Prevent our EPUB cover image from getting included -->
<xsl:template match="mediaobject[@role = 'cover']">
</xsl:template>

</xsl:stylesheet>

