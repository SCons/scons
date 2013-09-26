<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm xse"
                version='1.0'>

<dtm:doc dtm:idref="set.toc"/>
<xsl:template name="set.toc" dtm:id="set.toc">
  <xsl:param name="toc-context" select="."/>
  <xsl:variable name="nodes" select="book|setindex"/>

  <fo:block 
    xsl:use-attribute-sets="title.content.properties component.title.properties">
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'tableofcontents'"/>
    </xsl:call-template>
  </fo:block>

  <xsl:if test="$nodes">
    <fo:block xsl:use-attribute-sets="toc.margin.properties">
      <xsl:apply-templates select="$nodes" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="division.toc"/>
<xsl:template name="division.toc" dtm:id="division.toc">
  <xsl:param name="toc-context" select="."/>
  <xsl:variable name="nodes"
                select="$toc-context/part
                        |$toc-context/reference
                        |$toc-context/preface
                        |$toc-context/chapter
                        |$toc-context/appendix
                        |$toc-context/article
                        |$toc-context/bibliography
                        |$toc-context/glossary
                        |$toc-context/index"/>
  <fo:block 
    xsl:use-attribute-sets="title.content.properties component.title.properties">
      <fo:inline>
        <xsl:call-template name="gentext">
          <xsl:with-param name="key" select="'tableofcontents'"/>
        </xsl:call-template>
      </fo:inline>
  </fo:block>

  <xsl:if test="$nodes">
    <fo:block 
      xsl:use-attribute-sets="toc.margin.properties">
      <xsl:apply-templates select="$nodes" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="component.toc"/>
<xsl:template name="component.toc" dtm:id="component.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:variable name="nodes" select="section|sect1|refentry
                                     |article|bibliography|glossary
                                     |appendix"/>
  <!-- fo:block 
    xsl:use-attribute-sets="title.content.properties section.title.level1.properties">
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'toc'"/>
    </xsl:call-template>
  </fo:block -->

  <xsl:if test="$nodes">
    <fo:block xsl:use-attribute-sets="toc.margin.properties">
      <xsl:apply-templates select="$nodes" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="toc.line"/>
<xsl:template name="toc.line" dtm:id="toc.line">
  <xsl:variable name="label">
    <xsl:apply-templates select="." mode="label.markup" xse:apply-serna-fold-template="false"/>
  </xsl:variable>
  <xsl:variable name="is.component">
    <xsl:call-template name="is.component">
    </xsl:call-template>
  </xsl:variable>

  <fo:block 
    end-indent="{$toc.indent.width}pt">
    <xsl:if test="$is.component = 1 or 
                  local-name(.) = 'part' or local-name(.) = 'book'">
      <xsl:attribute name="font-weight">
        <xsl:text>bold</xsl:text>
      </xsl:attribute>
    </xsl:if>
    <fo:inline>
      <xsl:if test="$label != ''">
        <xsl:copy-of select="$label"/>
        <xsl:value-of select="$autotoc.label.separator"/>
      </xsl:if>
      <xsl:apply-templates select="." mode="title.markup" xse:apply-serna-fold-template="false"/>
    </fo:inline>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="bs.toc"/>
<xsl:template match="book|setindex" mode="toc" dtm:id="bs.toc">
  <xsl:param name="toc-context" select="."/>
  <xsl:call-template name="toc.line"/>

  <xsl:variable name="nodes" select="glossary|bibliography|preface|chapter
                                     |reference|part|article|appendix|index"/>

  <xsl:if test="$toc.section.depth &gt; 0 and $nodes">
    <fo:block start-indent="{count(ancestor::*)*$toc.indent.width}pt">
      <xsl:apply-templates select="$nodes" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="part.toc"/>
<xsl:template match="part" mode="toc" dtm:id="part.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:variable name="nodes" select="chapter|appendix|preface|reference|article"/>

  <xsl:if test="$toc.section.depth &gt; 0 and $nodes">
    <fo:block start-indent="{count(ancestor::*)*$toc.indent.width}pt">
      <xsl:apply-templates select="$nodes" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="rb.toc"/>
<xsl:template match="refentry|book" mode="toc" dtm:id="rb.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>
</xsl:template>

<dtm:doc dtm:idref="pcaa.toc"/>
<xsl:template match="preface|chapter|appendix|article"
              mode="toc" dtm:id="pcaa.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:variable name="nodes" select="section|sect1"/>

  <xsl:if test="$toc.section.depth &gt; 0 and $nodes">
    <fo:block start-indent="{count(ancestor::*)*$toc.indent.width}pt">
      <xsl:apply-templates select="$nodes" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="sect1.toc"/>
<xsl:template match="sect1" mode="toc" dtm:id="sect1.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:if test="$toc.section.depth &gt; 1 and sect2">
    <fo:block 
      start-indent="{count(ancestor::*)*$toc.indent.width}pt">
      <xsl:apply-templates select="sect2" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="sect2.toc"/>
<xsl:template match="sect2" mode="toc" dtm:id="sect2.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:variable name="reldepth"
                select="count(ancestor::*)-count($toc-context/ancestor::*)"/>

  <xsl:if test="$toc.section.depth &gt; 2 and sect3">
    <fo:block
      start-indent="{$reldepth*$toc.indent.width}pt">
      <xsl:apply-templates select="sect3" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="sect3.toc"/>
<xsl:template match="sect3" mode="toc" dtm:id="sect3.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:variable name="reldepth"
                select="count(ancestor::*)-count($toc-context/ancestor::*)"/>

  <xsl:if test="$toc.section.depth &gt; 3 and sect4">
    <fo:block
      start-indent="{$reldepth*$toc.indent.width}pt">
      <xsl:apply-templates select="sect4" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="sect4.toc"/>
<xsl:template match="sect4" mode="toc" dtm:id="sect4.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:variable name="reldepth"
                select="count(ancestor::*)-count($toc-context/ancestor::*)"/>

  <xsl:if test="$toc.section.depth &gt; 4 and sect5">
    <fo:block
      start-indent="{$reldepth*$toc.indent.width}pt">
      <xsl:apply-templates select="sect5" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="sect5.toc"/>
<xsl:template match="sect5" mode="toc" dtm:id="sect5.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>
</xsl:template>

<dtm:doc dtm:idref="section.toc"/>
<xsl:template match="section" mode="toc" dtm:id="section.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:variable name="depth" select="count(ancestor::section) + 1"/>
  <xsl:variable name="reldepth"
                select="count(ancestor::*)-count($toc-context/ancestor::*)"/>

  <xsl:if test="$toc.section.depth &gt;= $depth">
    <xsl:call-template name="toc.line"/>

    <xsl:if test="$toc.section.depth &gt; $depth and section">
      <fo:block
        start-indent="{$reldepth*$toc.indent.width}pt">
        <xsl:apply-templates select="section" mode="toc" xse:apply-serna-fold-template="false">
          <xsl:with-param name="toc-context" select="$toc-context"/>
        </xsl:apply-templates>
      </fo:block>
    </xsl:if>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="bg.toc"/>
<xsl:template match="bibliography|glossary"
              mode="toc" dtm:id="bg.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>
</xsl:template>

<dtm:doc dtm:idref="reference.toc"/>
<xsl:template match="reference" mode="toc" dtm:id="reference.toc">
  <xsl:param name="toc-context" select="."/>

  <xsl:call-template name="toc.line"/>

  <xsl:if test="$toc.section.depth &gt; 0 and refentry">
    <fo:block 
              start-indent="{count(ancestor::*)*$toc.indent.width}pt">
      <xsl:apply-templates select="refentry" mode="toc" xse:apply-serna-fold-template="false">
        <xsl:with-param name="toc-context" select="$toc-context"/>
      </xsl:apply-templates>
    </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="title.toc"/>
<xsl:template match="title" mode="toc" dtm:id="title.toc">
  <xsl:apply-templates xse:apply-serna-fold-template="false"/>
</xsl:template>

</xsl:stylesheet>

