<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                extension-element-prefixes="dtm"
                version='1.0'>

<!-- ==================================================================== -->

<dtm:doc dtm:idref="qandqset"/>
<xsl:template match="qandaset" dtm:id="qandqset">

  <fo:block>
    <xsl:apply-templates 
        select="title[not(self::processing-instruction('se:choice'))]"/>

    <xsl:apply-templates 
        select="*[not(self::title or self::qandadiv or self::qandaentry
                      or self::processing-instruction('se:choice'))]"/>
    <xsl:apply-templates 
        select="qandadiv[not(self::processing-instruction('se:choice'))]"/>

    <xsl:if test="qandaentry">
      <fo:list-block xsl:use-attribute-sets="list.block.spacing"
                     provisional-distance-between-starts="2.5em"
                     provisional-label-separation="0.2em">
        <xsl:apply-templates select="qandaentry"/>
      </fo:list-block>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="title.qandqset"/>
<xsl:template match="qandaset/title" dtm:id="title.qandqset">
  <xsl:variable name="enclsect" select="(ancestor::section
                                        | ancestor::simplesect
                                        | ancestor::sect5
                                        | ancestor::sect4
                                        | ancestor::sect3
                                        | ancestor::sect2
                                        | ancestor::sect1
                                        | ancestor::refsect3
                                        | ancestor::refsect2
                                        | ancestor::refsect1)[last()]"/>
  <xsl:variable name="sect.level">
    <xsl:call-template name="section.level">
      <xsl:with-param name="parent" select="$enclsect">
      </xsl:with-param>
    </xsl:call-template>
  </xsl:variable>
  <fo:block
    font-family="{$title.font.family}" 
    xsl:use-attribute-sets="component.title.properties">
    <xsl:apply-templates select="." mode="section.titles.mode">
      <xsl:with-param name="level" select="$sect.level + 1"/>
      <xsl:with-param name="heading" select="''">
      </xsl:with-param>
    </xsl:apply-templates>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="qandadiv"/>
<xsl:template match="qandadiv" dtm:id="qandadiv">
  <fo:block>
    <xsl:apply-templates 
      select="title[not(self::processing-instruction('se:choice'))]"/>
    <xsl:apply-templates 
      select="*[not(self::title or self::qandadiv or self::qandaentry
              or self::processing-instruction('se:choice'))]"/>
    <fo:block start-indent="{count(ancestor::qandadiv)*2}pc">
      <xsl:apply-templates 
        select="qandadiv"/>

      <xsl:if test="qandaentry[not(self::processing-instruction('se:choice'))]">
        <fo:list-block xsl:use-attribute-sets="list.block.spacing"
                       provisional-distance-between-starts="4em"
                       provisional-label-separation="0.2em">
          <xsl:apply-templates select="qandaentry"/>
        </fo:list-block>
      </xsl:if>
    </fo:block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="title.qandadiv"/>
<xsl:template match="qandadiv/title" dtm:id="title.qandadiv">
  <xsl:variable name="enclsect" select="(ancestor::section
                                        | ancestor::simplesect
                                        | ancestor::sect5
                                        | ancestor::sect4
                                        | ancestor::sect3
                                        | ancestor::sect2
                                        | ancestor::sect1
                                        | ancestor::refsect3
                                        | ancestor::refsect2
                                        | ancestor::refsect1)[last()]"/>

  <xsl:variable name="sect.level">
    <xsl:call-template name="section.level">
      <xsl:with-param name="parent" select="$enclsect">
      </xsl:with-param>
    </xsl:call-template>
  </xsl:variable>
  <fo:block
    font-family="{$title.font.family}" 
    xsl:use-attribute-sets="component.title.properties">
    <xsl:apply-templates select="." mode="section.titles.mode">
      <xsl:with-param name="level" select="$sect.level + 1 + count(ancestor::qandadiv)"/>
      <xsl:with-param name="heading" select="''">
      </xsl:with-param>
    </xsl:apply-templates>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="qandaentry"/>
<xsl:template match="qandaentry" dtm:id="qandaentry">
  <!-- We wrap the result into a block if we use Serna to see it in
       within one tag -->
  <xsl:choose>
    <xsl:when test="$use-serna-extensions">
      <fo:block>
        <xsl:apply-templates select="question"/>
        <xsl:apply-templates select="answer"/>
      </fo:block>
    </xsl:when>
    <xsl:otherwise>
        <xsl:apply-templates select="question"/>
        <xsl:apply-templates select="answer"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="question"/>
<xsl:template match="question" dtm:id="question">
  <xsl:variable name="deflabel">
    <xsl:choose>
      <xsl:when test="ancestor-or-self::*[@defaultlabel]">
        <xsl:value-of select="(ancestor-or-self::*[@defaultlabel])[last()]
                              /@defaultlabel"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="qanda.defaultlabel"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

    <fo:list-item xsl:use-attribute-sets="list.item.spacing">
      <fo:list-item-label end-indent="label-end()">
        <xsl:choose>
          <xsl:when test="$deflabel = 'none'">
            <fo:block> </fo:block>
          </xsl:when>
          <xsl:otherwise>
            <fo:block padding-bottom="1pt">
              <xsl:apply-templates 
                select="self::*[not(self::processing-instruction('se:choice'))]" 
                mode="label.markup"/>
              <xsl:if test="$deflabel = 'number'">
                <xsl:text>.</xsl:text>
              </xsl:if>
              <xsl:text> </xsl:text>
            </fo:block>
          </xsl:otherwise>
        </xsl:choose>
      </fo:list-item-label>
      <fo:list-item-body start-indent="body-start()">
        <fo:block font-weight="bold" padding-top="0pt">
          <xsl:apply-templates select="*[local-name(.)!='label']"/>
        </fo:block>
      </fo:list-item-body>
    </fo:list-item>
</xsl:template>

<dtm:doc dtm:idref="answer"/>
<xsl:template match="answer" dtm:id="answer">
      <xsl:variable name="deflabel">
        <xsl:choose>
          <xsl:when test="ancestor-or-self::*[@defaultlabel]">
            <xsl:value-of select="(ancestor-or-self::*[@defaultlabel])[last()]
                                  /@defaultlabel"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="qanda.defaultlabel"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <fo:list-item xsl:use-attribute-sets="list.item.spacing">
        <fo:list-item-label end-indent="label-end()">
          <xsl:choose>
            <xsl:when test="$deflabel = 'none'">
            </xsl:when>
            <xsl:otherwise>
              <fo:block padding-bottom="1pt">
                <xsl:apply-templates select="." mode="label.markup"/>
                <xsl:if test="$deflabel = 'number'">
                  <xsl:text>.</xsl:text>
                </xsl:if>
              </fo:block>
            </xsl:otherwise>
          </xsl:choose>
        </fo:list-item-label>
        <fo:list-item-body start-indent="body-start()">
          <fo:block>
            <xsl:apply-templates select="*[not(self::label)]"/>
          </fo:block>
        </fo:list-item-body>
      </fo:list-item>
</xsl:template>

<dtm:doc dtm:idref="label"/>
<xsl:template match="label" dtm:id="label">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

</xsl:stylesheet>
