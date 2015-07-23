<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                extension-element-prefixes="dtm"
                version='1.0'>

<dtm:doc dtm:idref="appendix"/>
<xsl:template match="appendix" dtm:id="appendix">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|appendixinfo|docinfo"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle
                            or self::titleabbrev
                            or self::appendixinfo or self::docinfo)]"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="appendix.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>


<dtm:doc dtm:idref="article"/>
<xsl:template match="article" dtm:id="article">
  <xsl:variable name="preamble"
                select="title|subtitle|articleinfo|artheader"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle
                        or self::articleinfo or self::artheader)]"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="article.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="preface"/>
<xsl:template match="preface" dtm:id="preface">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|docinfo|prefaceinfo"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle or self::titleabbrev
                              or self::docinfo or self::prefaceinfo)]"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="preface.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="chapter"/>
<xsl:template match="chapter" dtm:id="chapter">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|docinfo|chapterinfo"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle or self::titleabbrev
                              or self::docinfo or self::chapterinfo)]"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="chapter.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="sections"/>
<xsl:template match="section|sect1|sect2|sect3|sect4|sect5" dtm:id="sections">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|sectioninfo|sect1info
                        |sect2info|sect3info|sect4info|sect5info"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle or self::titleabbrev
                        or self::sectioninfo or self::sect1info 
                        or self::sect2info or self::sect3info 
                        or self::sect4info or self::sect5info)]"/>
  <fo:block 
    xsl:use-attribute-sets="section.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="section.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="simplesect"/>
<xsl:template match="simplesect" dtm:id="simplesect">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle or self::titleabbrev)]"/>
  <fo:block
    xsl:use-attribute-sets="section.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="simplesect.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

</xsl:stylesheet>
