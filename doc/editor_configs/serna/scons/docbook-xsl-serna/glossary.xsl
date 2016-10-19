<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<dtm:doc dtm:idref="glossary"/>
<xsl:template match="glossary" dtm:id="glossary">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|glossaryinfo"/>
  <xsl:variable name="content"
                select="not-a-node"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="glossary.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
    <xsl:call-template name="make-glossary"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="make-glossary"/>
<xsl:template name="make-glossary" dtm:id="make-glossary">
  <xsl:param name="divs" select="glossdiv"/>
  <xsl:param name="entries" select="glossentry"/>

  <xsl:variable name="width">
    <xsl:value-of select="$glossterm.width"/>
  </xsl:variable>

  <xsl:variable name="presentation">
    <xsl:value-of select="$glossary.presentation"/>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="$presentation = 'list'">
      <xsl:apply-templates select="$divs" mode="glossary.as.list">
        <xsl:with-param name="width" select="$width"/>
      </xsl:apply-templates>
      <xsl:if test="$entries">
        <fo:list-block provisional-distance-between-starts="{$width}"
                       provisional-label-separation="{$glossterm.separation}"
                       xsl:use-attribute-sets="normal.para.spacing">
          <xsl:apply-templates select="$entries" mode="glossary.as.list"/>
        </fo:list-block>
      </xsl:if>
    </xsl:when>
    <xsl:when test="$presentation = 'blocks'">
      <xsl:apply-templates select="$divs" mode="glossary.as.blocks"/>
      <xsl:apply-templates select="$entries" mode="glossary.as.blocks"/>
    </xsl:when> 
    <xsl:when test="$glossary.as.blocks != 0">
      <xsl:apply-templates select="$divs" mode="glossary.as.blocks"/>
      <xsl:apply-templates select="$entries" mode="glossary.as.blocks"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates select="$divs" mode="glossary.as.list">
        <xsl:with-param name="width" select="$width"/>
      </xsl:apply-templates>
      <xsl:if test="$entries">
        <fo:list-block provisional-distance-between-starts="{$width}"
                       provisional-label-separation="{$glossterm.separation}"
                       xsl:use-attribute-sets="normal.para.spacing">
          <xsl:apply-templates select="$entries" mode="glossary.as.list"/>
        </fo:list-block>
      </xsl:if>
    </xsl:otherwise>
  </xsl:choose>
<!--  <xsl:apply-templates select="*[not(local-name()='glossdiv')]"/> -->
</xsl:template>

<dtm:doc dtm:idref="glosslist"/>
<xsl:template match="glosslist" dtm:id="glosslist">

  <xsl:variable name="width">
    <xsl:value-of select="$glossterm.width"/>
  </xsl:variable>

  <xsl:variable name="presentation">
    <xsl:value-of select="$glossary.presentation"/>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="$presentation = 'list'">
      <fo:list-block provisional-distance-between-starts="{$width}"
                     provisional-label-separation="{$glossterm.separation}"
                     xsl:use-attribute-sets="normal.para.spacing">
        <xsl:apply-templates mode="glossary.as.list"/>
      </fo:list-block>
    </xsl:when>
    <xsl:when test="$presentation = 'blocks'">
      <xsl:apply-templates mode="glossary.as.blocks"/>
    </xsl:when>
    <xsl:when test="$glosslist.as.blocks != 0">
      <xsl:apply-templates mode="glossary.as.blocks"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:list-block provisional-distance-between-starts="{$width}"
                     provisional-label-separation="{$glossterm.separation}"
                     xsl:use-attribute-sets="normal.para.spacing">
        <xsl:apply-templates mode="glossary.as.list"/>
      </fo:list-block>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- ==================================================================== -->
<!-- Format glossary as a list -->
<dtm:doc dtm:elements="glossdiv" dtm:idref="glossdiv.glossary-as-list glossdiv.glossary-as-blocks"/>
<xsl:template match="glossdiv" mode="glossary.as.list" dtm:id="glossdiv.glossary-as-list">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|glossaryinfo"/>
  <xsl:variable name="content"
                select="not-a-node"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">

    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="glossdiv.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
    
    <xsl:variable name="width" select="$glossterm.width"/>
    
    <fo:list-block provisional-distance-between-starts="{$width}"
        provisional-label-separation="{$glossterm.separation}"
        xsl:use-attribute-sets="normal.para.spacing">
      <xsl:apply-templates select="glossentry" mode="glossary.as.list"/>
    </fo:list-block>

  </fo:block>
</xsl:template>

<!--
GlossEntry ::=
  GlossTerm, Acronym?, Abbrev?,
  (IndexTerm)*,
  RevHistory?,
  (GlossSee | GlossDef+)
-->
<dtm:doc dtm:elements="glossentry" dtm:idref="glossentry.glossary-as-list glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry" mode="glossary.as.list" dtm:id="glossentry.glossary-as-list">

  <fo:list-item xsl:use-attribute-sets="normal.para.spacing">

    <fo:list-item-label end-indent="label-end()">
      <fo:block>
        <xsl:choose>
          <xsl:when test="$glossentry.show.acronym = 'primary'">
            <xsl:choose>
              <xsl:when test="acronym|abbrev">
                <xsl:apply-templates select="acronym|abbrev[not(self::processing-instruction('se:choice'))]" mode="glossary.as.list"/>
                <xsl:text> (</xsl:text>
                <xsl:apply-templates select="glossterm" mode="glossary.as.list"/>
                <xsl:text>)</xsl:text>
              </xsl:when>
              <xsl:otherwise>
                <xsl:apply-templates select="glossterm" mode="glossary.as.list"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>

          <xsl:when test="$glossentry.show.acronym = 'yes'">
            <xsl:apply-templates select="glossterm" mode="glossary.as.list"/>

            <xsl:if test="acronym[not(self::processing-instruction('se:choice'))]|abbrev[not(self::processing-instruction('se:choice'))]">
              <xsl:text> (</xsl:text>
              <xsl:apply-templates select="acronym|abbrev" mode="glossary.as.list"/>
              <xsl:text>)</xsl:text>
            </xsl:if>
          </xsl:when>

          <xsl:otherwise>
            <xsl:apply-templates select="glossterm" mode="glossary.as.list"/>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:apply-templates select="indexterm[not(self::processing-instruction('se:choice'))]"/>
      </fo:block>
    </fo:list-item-label>

    <fo:list-item-body start-indent="body-start()">
      <xsl:apply-templates select="glosssee|glossdef" mode="glossary.as.list"/>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

<dtm:doc dtm:elements="glossentry/glossterm" dtm:idref="glossterm.glossentry.glossary-as-list glossterm.glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry/glossterm" mode="glossary.as.list" dtm:id="glossterm.glossentry.glossary-as-list">
  <fo:inline>
    <xsl:apply-templates/>
  </fo:inline>
  <xsl:if test="following-sibling::glossterm">, </xsl:if>
</xsl:template>

<dtm:doc dtm:elements="glossentry/acronym" dtm:idref="acronym.glossentry.glossary-as-list acronym.glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry/acronym" mode="glossary.as.list" dtm:id="acronym.glossentry.glossary-as-list">
  <fo:inline>
    <xsl:apply-templates/>
  </fo:inline>
  <xsl:if test="following-sibling::acronym|following-sibling::abbrev">, </xsl:if>
</xsl:template>

<dtm:doc dtm:elements="glossentry/abbrev" dtm:idref="abbrev.glossentry.glossary-as-list abbrev.glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry/abbrev" mode="glossary.as.list" dtm:id="abbrev.glossentry.glossary-as-list">
  <fo:inline>
    <xsl:apply-templates/>
  </fo:inline>
  <xsl:if test="following-sibling::acronym|following-sibling::abbrev">, </xsl:if>
</xsl:template>

<dtm:doc dtm:elements="glossentry/glosssee" dtm:idref="glosssee.glossentry.glossary-as-list glosssee.glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry/glosssee" mode="glossary.as.list" dtm:id="glosssee.glossentry.glossary-as-list">
  <xsl:variable name="otherterm" select="@otherterm"/>
  <fo:block>
    <xsl:call-template name="gentext.template">
      <xsl:with-param name="context" select="'glossary'"/>
      <xsl:with-param name="name" select="'see'"/>
    </xsl:call-template>
    <xsl:apply-templates mode="glossary.as.list"/>
    <xsl:choose>
      <xsl:when test="@otherterm">
        <xsl:value-of select="id(@otherterm)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>.</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="glossentry/glossdef" dtm:idref="glossdef.glossentry.glossary-as-list glossdef.glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry/glossdef" mode="glossary.as.list" dtm:id="glossdef.glossentry.glossary-as-list">
  <fo:block>
    <xsl:apply-templates select="*[local-name(.) != 'glossseealso']"/>
    <xsl:if test="glossseealso">
      <fo:block>
        <xsl:call-template name="gentext.template">
          <xsl:with-param name="context" select="'glossary'"/>
          <xsl:with-param name="name" select="'seealso'"/>
        </xsl:call-template>
        <xsl:apply-templates select="glossseealso" mode="glossary.as.list"/>
      </fo:block>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="glossentry/glossdef/para[1]|glossentry/glossdef/simpara[1]" dtm:idref="para1.glossentry.glossary-as-list para1.glossentry.glossary-as-blocks"/>
<xsl:template match="glossentry/glossdef/para[1]|glossentry/glossdef/simpara[1]"
              mode="glossary.as.list" dtm:id="para1.glossentry.glossary-as-list">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="glossseealso" dtm:idref="glossseealso.glossary-as-list glossseealso.glossary-as-blocks"/>
<xsl:template match="glossseealso" mode="glossary.as.list" dtm:id="glossseealso.glossary-as-list">
  <fo:inline>
    <xsl:apply-templates mode="glossary.as.list"/>
    <xsl:choose>
      <xsl:when test="@otherterm">
        <xsl:value-of select="id(@otherterm)"/>
      </xsl:when>
      <xsl:when test="position() = last()">
        <xsl:text>.</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>, </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </fo:inline>
</xsl:template>

<!-- ==================================================================== -->
<!-- Format glossary blocks -->

<xsl:template match="glossdiv" mode="glossary.as.blocks" dtm:id="glossdiv.glossary-as-blocks">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev|glossaryinfo"/>
  <xsl:variable name="content"
                select="*[not(self::title or self::subtitle
                            or self::titleabbrev)]"/>
  <fo:block 
    xsl:use-attribute-sets="component.block.properties">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="glossdiv.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
    </xsl:call-template>

    <xsl:apply-templates select="glossentry" mode="glossary.as.blocks"/>

  </fo:block>
</xsl:template>


<!--
GlossEntry ::=
  GlossTerm, Acronym?, Abbrev?,
  (IndexTerm)*,
  RevHistory?,
  (GlossSee | GlossDef+)
-->
<xsl:template match="glossentry" mode="glossary.as.blocks" dtm:id="glossentry.glossary-as-blocks">
  <fo:block xsl:use-attribute-sets="list.block.spacing">

    <xsl:choose>
      <xsl:when test="$glossentry.show.acronym = 'primary'">
        <xsl:choose>
          <xsl:when test="acronym|abbrev">
            <xsl:apply-templates select="acronym|abbrev" mode="glossary.as.blocks"/>
            <xsl:text> (</xsl:text>
            <xsl:apply-templates select="glossterm" mode="glossary.as.blocks"/>
            <xsl:text>)</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="glossterm" mode="glossary.as.blocks"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <xsl:when test="$glossentry.show.acronym = 'yes'">
        <xsl:apply-templates select="glossterm" mode="glossary.as.blocks"/>

        <xsl:if test="acronym[not(self::processing-instruction('se:choice'))]|abbrev[not(self::processing-instruction('se:choice'))]">
          <xsl:text> (</xsl:text>
          <xsl:apply-templates select="acronym|abbrev" mode="glossary.as.blocks"/>
          <xsl:text>)</xsl:text>
        </xsl:if>
      </xsl:when>

      <xsl:otherwise>
        <xsl:apply-templates select="glossterm[not(self::processing-instruction('se:choice'))]" mode="glossary.as.blocks"/>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:apply-templates select="indexterm[not(self::processing-instruction('se:choice'))]"/>
    <fo:block margin-left="0.25in">
      <xsl:apply-templates select="glosssee|glossdef" mode="glossary.as.blocks"/>
    </fo:block>
  </fo:block>
</xsl:template>

<xsl:template match="glossentry/glossterm" mode="glossary.as.blocks" dtm:id="glossterm.glossentry.glossary-as-blocks">
  <fo:inline>
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::glossterm">, </xsl:if>
  </fo:inline>
</xsl:template>

<xsl:template match="glossentry/acronym" mode="glossary.as.blocks" dtm:id="acronym.glossentry.glossary-as-blocks">
  <fo:inline>
  <xsl:apply-templates/>
  <xsl:if test="following-sibling::acronym|following-sibling::abbrev">, </xsl:if>
  </fo:inline>
</xsl:template>

<xsl:template match="glossentry/abbrev" mode="glossary.as.blocks" dtm:id="abbrev.glossentry.glossary-as-blocks">
  <fo:inline>
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::acronym|following-sibling::abbrev">, </xsl:if>
  </fo:inline>
</xsl:template>

<xsl:template match="glossentry/glosssee" mode="glossary.as.blocks" dtm:id="glosssee.glossentry.glossary-as-blocks">
  <fo:inline>
  <xsl:variable name="otherterm" select="@otherterm"/>

  <xsl:call-template name="gentext.template">
    <xsl:with-param name="context" select="'glossary'"/>
    <xsl:with-param name="name" select="'see'"/>
  </xsl:call-template>
  <xsl:apply-templates mode="glossary.as.blocks"/>
  <xsl:text>.</xsl:text>
  </fo:inline>
</xsl:template>

<xsl:template match="glossentry/glossdef" mode="glossary.as.blocks" dtm:id="glossdef.glossentry.glossary-as-blocks">
  <xsl:apply-templates select="*[local-name(.) != 'glossseealso']"/>
  <xsl:if test="glossseealso">
    <fo:block>
      <xsl:call-template name="gentext.template">
        <xsl:with-param name="context" select="'glossary'"/>
        <xsl:with-param name="name" select="'seealso'"/>
      </xsl:call-template>
      <xsl:apply-templates select="glossseealso" mode="glossary.as.blocks"/>
    </fo:block>
  </xsl:if>
</xsl:template>

<xsl:template match="glossentry/glossdef/para[1]|glossentry/glossdef/simpara[1]"
              mode="glossary.as.blocks" dtm:id="para1.glossentry.glossary-as-blocks">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<xsl:template match="glossseealso" mode="glossary.as.blocks" dtm:id="glossseealso.glossary-as-blocks">
  <fo:inline>

  <xsl:variable name="otherterm" select="@otherterm"/>

  <xsl:apply-templates mode="glossary.as.blocks"/>

  <xsl:choose>
    <xsl:when test="position() = last()">
      <xsl:text>.</xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text>, </xsl:text>
    </xsl:otherwise>
  </xsl:choose>
  </fo:inline>
</xsl:template>

</xsl:stylesheet>
