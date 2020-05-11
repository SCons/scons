<?xml version='1.0'?>
<!--

  __COPYRIGHT__

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->

<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fo="http://www.w3.org/1999/XSL/Format"
	version="1.0">

<xsl:import href="../../SCons/Tool/docbook/docbook-xsl-1.76.1/fo/docbook.xsl"/>

<xsl:include href="scons_title.xsl"/>
<xsl:param name="l10n.gentext.default.language" select="'en'"/>
<xsl:param name="section.autolabel" select="1"/>
<xsl:param name="section.label.includes.component.label" select="1"/>
<xsl:param name="paper.type" select="'letter'"/>
<xsl:param name="body.start.indent">0pt</xsl:param>
<xsl:param name="shade.verbatim" select="1"/>
<xsl:param name="variablelist.term.break.after" select="1"/>
<xsl:param name="variablelist.term.separator"/>

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

<xsl:attribute-set name="variablelist.term.properties">
  <xsl:attribute name="font-weight">bold</xsl:attribute>
</xsl:attribute-set>

<xsl:template match="variablelist">
  <xsl:variable name="presentation">
    <xsl:call-template name="pi.dbfo_list-presentation"/>
  </xsl:variable>
  <xsl:apply-templates select="." mode="vl.as.blocks"/>
</xsl:template>

<!-- Prevent our EPUB cover image from getting printed to the PDF -->
<xsl:template match="mediaobject[@role = 'cover']">
</xsl:template>

</xsl:stylesheet>
