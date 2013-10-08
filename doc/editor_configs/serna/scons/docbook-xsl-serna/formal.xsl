<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<dtm:doc dtm:idref="formal.object.content"/>
<xsl:template name="formal.object.content" dtm:id="formal.object.content">
  <xsl:param name="placement"/>
    
    <xsl:if test="$placement = 'before'">
      <xsl:call-template name="formal.object.heading">
        <xsl:with-param name="placement" select="$placement"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:apply-templates/>
    <xsl:if test="$placement != 'before'">
      <xsl:call-template name="formal.object.heading">
        <xsl:with-param name="placement" select="$placement"/>
      </xsl:call-template>
    </xsl:if>
    
</xsl:template>

<dtm:doc dtm:idref="formal.object"/>
<xsl:template name="formal.object" dtm:id="formal.object">
  <xsl:param name="placement" select="'before'"/>

  <fo:block xsl:use-attribute-sets="formal.object.properties">
    <xsl:call-template name="formal.object.content">
      <xsl:with-param name="placement" select="$placement"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="formal.object.heading"/>
<xsl:template name="formal.object.heading" dtm:id="formal.object.heading">
  <xsl:param name="object" select="."/>
  <xsl:param name="placement" select="'before'"/>

  <xsl:if test="$object/title[not(self::processing-instruction('se:choice'))]">
  <fo:block xsl:use-attribute-sets="formal.title.properties">
    <xsl:choose>
      <xsl:when test="$placement = 'before'">
        <xsl:attribute
               name="keep-with-next.within-column">always</xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute
               name="keep-with-previous.within-column">always</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates select="$object/title" mode="formal.title.mode">
      <xsl:with-param name="key" select="local-name($object)"/>
    </xsl:apply-templates>
  </fo:block>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="informal.object"/>
<xsl:template name="informal.object" dtm:id="informal.object">
  <xsl:choose>
    <xsl:when test="local-name(.) = 'equation'">
      <fo:block
                xsl:use-attribute-sets="equation.properties">
        <xsl:apply-templates/>
      </fo:block>
    </xsl:when>
    <xsl:when test="local-name(.) = 'procedure'">
      <fo:block
                xsl:use-attribute-sets="procedure.properties">
        <xsl:apply-templates/>
      </fo:block>
    </xsl:when>
    <xsl:otherwise>
      <fo:block>
        <xsl:apply-templates/>
      </fo:block>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="semiformal.object"/>
<xsl:template name="semiformal.object" dtm:id="semiformal.object">
  <xsl:param name="placement" select="'before'"/>
  <xsl:choose>
    <xsl:when test="./title">
      <xsl:call-template name="formal.object">
        <xsl:with-param name="placement" select="$placement"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="informal.object"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="figure"/>
<xsl:template match="figure" dtm:id="figure">
  <xsl:variable name="param.placement"
                select="substring-after(normalize-space($formal.title.placement),
                                        concat(local-name(.), ' '))"/>

  <xsl:variable name="placement">
    <xsl:choose>
      <xsl:when test="contains($param.placement, ' ')">
        <xsl:value-of select="substring-before($param.placement, ' ')"/>
      </xsl:when>
      <xsl:when test="$param.placement = ''">before</xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$param.placement"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:call-template name="formal.object">
    <xsl:with-param name="placement" select="$placement"/>
  </xsl:call-template>

</xsl:template>

<dtm:doc dtm:idref="example"/>
<xsl:template match="example" dtm:id="example">
  <xsl:variable name="param.placement"
                select="substring-after(normalize-space($formal.title.placement),
                                        concat(local-name(.), ' '))"/>

  <xsl:variable name="placement">
    <xsl:choose>
      <xsl:when test="contains($param.placement, ' ')">
        <xsl:value-of select="substring-before($param.placement, ' ')"/>
      </xsl:when>
      <xsl:when test="$param.placement = ''">before</xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$param.placement"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:call-template name="formal.object">
    <xsl:with-param name="placement" select="$placement"/>
  </xsl:call-template>

</xsl:template>

<dtm:doc dtm:idref="equation"/>
<xsl:template match="equation" dtm:id="equation">
  <xsl:variable name="param.placement"
                select="substring-after(normalize-space($formal.title.placement),
                                        concat(local-name(.), ' '))"/>

  <xsl:variable name="placement">
    <xsl:choose>
      <xsl:when test="contains($param.placement, ' ')">
        <xsl:value-of select="substring-before($param.placement, ' ')"/>
      </xsl:when>
      <xsl:when test="$param.placement = ''">before</xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$param.placement"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:call-template name="semiformal.object">
    <xsl:with-param name="placement" select="$placement"/>
  </xsl:call-template>

</xsl:template>

<dtm:doc dtm:idref="title.figure"/>
<xsl:template match="figure/title" dtm:id="title.figure"></xsl:template>

<dtm:doc dtm:idref="titleabbrev.figure"/>
<xsl:template match="figure/titleabbrev" dtm:id="titleabbrev.figure"></xsl:template>

<dtm:doc dtm:idref="title.table"/>
<xsl:template match="table/title" dtm:id="title.table"></xsl:template>

<dtm:doc dtm:idref="titleabbrev.table"/>
<xsl:template match="table/titleabbrev" dtm:id="titleabbrev.table"></xsl:template>

<dtm:doc dtm:idref="textobject.table"/>
<xsl:template match="table/textobject" dtm:id="textobject.table"></xsl:template>

<dtm:doc dtm:idref="title.example"/>
<xsl:template match="example/title" dtm:id="title.example"></xsl:template>

<dtm:doc dtm:idref="titleabbrev.example"/>
<xsl:template match="example/titleabbrev" dtm:id="titleabbrev.example"></xsl:template>

<dtm:doc dtm:idref="title.equation"/>
<xsl:template match="equation/title" dtm:id="title.equation"></xsl:template>

<dtm:doc dtm:idref="titleabbrev.equation"/>
<xsl:template match="equation/titleabbrev" dtm:id="titleabbrev.equation"></xsl:template>

<dtm:doc dtm:idref="informalfigure"/>
<xsl:template match="informalfigure" dtm:id="informalfigure">
  <xsl:call-template name="informal.object"/>
</xsl:template>

<dtm:doc dtm:idref="informalexample"/>
<xsl:template match="informalexample" dtm:id="informalexample">
  <xsl:call-template name="informal.object"/>
</xsl:template>

<dtm:doc dtm:idref="textobject.informaltable"/>
<xsl:template match="informaltable/textobject" dtm:id="textobject.informaltable"></xsl:template>

<dtm:doc dtm:idref="informalequation"/>
<xsl:template match="informalequation" dtm:id="informalequation">
  <xsl:call-template name="informal.object"/>
</xsl:template>

</xsl:stylesheet>
