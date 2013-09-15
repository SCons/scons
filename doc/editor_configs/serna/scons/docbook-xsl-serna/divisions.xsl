<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<!-- ==================================================================== -->

<!-- The priority is set for exceeding /* template.
     Templates that contain page-sequence/flow should exceed
     the /* fallback.  -->

<dtm:doc dtm:idref="bp.root-mode"/>
<xsl:template match="/book|/part" priority="1" mode="root.mode" dtm:id="bp.root-mode">
  <fo:page-sequence                       
    master-reference="body"
    initial-page-number="1">
    <fo:flow flow-name="xsl-region-body">
      <xsl:apply-templates select="."/>
    </fo:flow>
  </fo:page-sequence>
</xsl:template>

<dtm:doc dtm:idref="set"/>
<xsl:template match="set" dtm:id="set">
  <xsl:variable name="preamble"
                select="*[not(self::book or self::setindex)]"/>
  <xsl:variable name="content" select="book|setindex"/>

  <fo:block>
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="set.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="book"/>
<xsl:template match="book" dtm:id="book">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|bookinfo"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle
                            or self::titleabbrev
                            or self::bookinfo)]"/>
  <fo:block>
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="book.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="part"/>
<xsl:template match="part" dtm:id="part">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|partinfo|docinfo"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle
                          or self::titleabbrev or self::partinfo
                          or self::docinfo)]"/>
  <fo:block>
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="part.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="titles"/>
<xsl:template match="title|subtitle|titleabbrev|bookinfo|othercredit|edition|setinfo" priority="-1" dtm:id="titles">
  <fo:block padding-bottom="1em">
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

</xsl:stylesheet>

