<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<dtm:doc dtm:idref="reference"/>
<xsl:template match="reference" dtm:id="reference">
  <xsl:variable name="preamble"
                select="docinfo|title|subtitle|titleabbrev|partintro"/>
  <xsl:variable name="content"
                select="*[not(self::docinfo or self::title or self::subtitle
                        or self::titleabbrev or self::partintro)]"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="reference.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="refentryinfo.refentry"/>
<xsl:template match="refentry/refentryinfo" dtm:id="refentryinfo.refentry"></xsl:template>

  <dtm:doc dtm:idref="partintro.reference"/>
  <xsl:template match="reference/partintro" dtm:id="partintro.reference">
    <fo:block>
      <xsl:if test="title">
        <xsl:call-template name="partintro.titlepage"/>
      </xsl:if>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

<dtm:doc dtm:idref="refentry.refmeta"/>
<xsl:template match="refentry|refmeta" dtm:id="refentry.refmeta">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="manvolnum"/>
<xsl:template match="manvolnum" dtm:id="manvolnum">
  <fo:inline>
    <xsl:text>(</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>)</xsl:text>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="refmiscinfo"/>
<xsl:template match="refmiscinfo" dtm:id="refmiscinfo">
</xsl:template>

<dtm:doc dtm:idref="refentrytitle"/>
<xsl:template match="refentrytitle" dtm:id="refentrytitle">
  <xsl:call-template name="inline.charseq"/>
</xsl:template>

<dtm:doc dtm:idref="refnamediv"/>
<xsl:template match="refnamediv" dtm:id="refnamediv">
  <fo:block>
    <xsl:choose>
      <xsl:when test="$refentry.generate.name != 0">
        <fo:block xsl:use-attribute-sets="refentry.title.properties">
          <xsl:call-template name="gentext">
            <xsl:with-param name="key" select="'refname'"/>
          </xsl:call-template>
        </fo:block>
      </xsl:when>

      <xsl:when test="$refentry.generate.title != 0">
        <fo:block xsl:use-attribute-sets="refentry.title.properties">
          <xsl:choose>
            <xsl:when test="../refmeta/refentrytitle">
              <xsl:apply-templates 
                select="../refmeta/refentrytitle[not(self::processing-instruction('se:choice'))]"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates 
                select="refname[not(self::processing-instruction('se:choice'))][1]"/>
            </xsl:otherwise>
          </xsl:choose>
        </fo:block>
      </xsl:when>
    </xsl:choose>
    <fo:block space-after="1em">
      <xsl:choose>
        <xsl:when test="../refmeta/refentrytitle">
          <xsl:apply-templates 
            select="../refmeta/refentrytitle"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates 
            select="refname[1]"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="refpurpose"/>
    </fo:block>
    <xsl:if test="string-length(refname) and count(refname) > 1">
      <fo:block>
        <xsl:for-each select="refname[not(self::processing-instruction('se:choice'))]">
          <xsl:apply-templates select="."/>
          <xsl:if test="following-sibling::refname[not(self::processing-instruction('se:choice'))][1]">
            <xsl:text>, </xsl:text>
          </xsl:if>
        </xsl:for-each>
      </fo:block>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="refname"/>
<xsl:template match="refname" dtm:id="refname">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="refpurpose"/>
<xsl:template match="refpurpose" dtm:id="refpurpose">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:text> </xsl:text>
      <xsl:call-template name="dingbat">
        <xsl:with-param name="dingbat">em-dash</xsl:with-param>
      </xsl:call-template>
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="refdescriptor"/>
<xsl:template match="refdescriptor" dtm:id="refdescriptor">
  <!-- todo: finish this -->
</xsl:template>

<dtm:doc dtm:idref="refclass"/>
<xsl:template match="refclass" dtm:id="refclass">
  <fo:block font-weight="bold">
    <xsl:if test="@role">
      <xsl:value-of select="@role"/>
      <xsl:text>: </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="refsynopsisdiv"/>
<xsl:template match="refsynopsisdiv" dtm:id="refsynopsisdiv">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle or self::titleabbrev)]"/>
  <fo:block
    xsl:use-attribute-sets="section.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="refsynopsisdiv.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="refsections"/>
<xsl:template match="refsection|refsect1|refsect2|refsect3" dtm:id="refsections">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle or self::titleabbrev)]"/>
  <fo:block
    xsl:use-attribute-sets="section.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="refsection.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

</xsl:stylesheet>
