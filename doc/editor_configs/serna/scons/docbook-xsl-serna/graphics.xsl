<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                extension-element-prefixes="dtm"
                version='1.0'>

<xsl:template name="mediaobject.filename" dtm:id="media.filename">
  <xsl:param name="object"></xsl:param>

  <xsl:variable name="data" select="$object/videodata
                                    |$object/imagedata
                                    |$object/audiodata
                                    |$object"/>

    <xsl:choose>
      <xsl:when test="$data[@fileref]">
        <xsl:value-of select="$data/@fileref"/>
      </xsl:when>
      <xsl:when test="$data[@entityref]">
        <xsl:value-of select="unparsed-entity-uri($data/@entityref)"/>
      </xsl:when>
      <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="screenshot"/>
<xsl:template match="screenshot" dtm:id="screenshot">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="screeninfo"/>
<xsl:template match="screeninfo" dtm:id="screeninfo">
   <xsl:if test="$show.preamble.editing">
     <fo:block xsl:use-attribute-sets="preamble.attributes">
       <xsl:call-template name="gentext.template">
         <xsl:with-param name="name" select="'draftarea'"/>
         <xsl:with-param name="context" select="'empty'"/>
       </xsl:call-template>
       <xsl:text> "</xsl:text>
       <xsl:value-of select="local-name(.)"/>
       <xsl:text>" </xsl:text>
     <xsl:apply-templates/>
     </fo:block>
   </xsl:if>
</xsl:template>

<!-- ==================================================================== -->
<!-- Override these templates for FO -->
<!-- ==================================================================== -->

<xsl:template name="process.image" dtm:id="image.process">
  <!-- When this template is called, the current node should be  -->
  <!-- a graphic, inlinegraphic, audiodata, imagedata, or videodata. -->
  <!-- All those elements have the same set of attributes, so we -->
  <!-- can handle them all in one place.                         -->

  <xsl:variable name="scalefit">
    <xsl:choose>
      <xsl:when test="$ignore.image.scaling != 0">0</xsl:when>
      <xsl:when test="@contentwidth or @contentdepth">0</xsl:when>
      <xsl:when test="@scale">0</xsl:when>
      <xsl:when test="@scalefit"><xsl:value-of select="@scalefit"/></xsl:when>
      <xsl:when test="@width or @depth">1</xsl:when>
      <xsl:otherwise>0</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="scale">
    <xsl:choose>
      <xsl:when test="$ignore.image.scaling != 0">0</xsl:when>
      <xsl:when test="@contentwidth or @contentdepth">1.0</xsl:when>
      <xsl:when test="@scale">
        <xsl:value-of select="@scale div 100.0"/>
      </xsl:when>
      <xsl:otherwise>1.0</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="filename">
    <xsl:choose>
      <xsl:when test="local-name(.) = 'graphic'
                      or local-name(.) = 'inlinegraphic'">
        <!-- handle legacy graphic and inlinegraphic by new template --> 
        <xsl:call-template name="mediaobject.filename">
          <xsl:with-param name="object" select="."/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <!-- imagedata, videodata, audiodata -->
        <xsl:call-template name="mediaobject.filename">
          <xsl:with-param name="object" select=".."/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <fo:inline>
  <fo:external-graphic>
    <xsl:attribute name="src">
      <xsl:call-template name="fo-external-image">
        <xsl:with-param name="filename" select="$filename"/>
      </xsl:call-template>
    </xsl:attribute>

    <xsl:attribute name="width">
      <xsl:choose>
        <xsl:when test="$ignore.image.scaling != 0">auto</xsl:when>
        <xsl:when test="@width">
          <xsl:value-of select="@width"/>
        </xsl:when>
        <xsl:otherwise>auto</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>

    <xsl:attribute name="height">
      <xsl:choose>
        <xsl:when test="$ignore.image.scaling != 0">auto</xsl:when>
        <xsl:when test="@depth">
          <xsl:value-of select="@depth"/>
        </xsl:when>
        <xsl:otherwise>auto</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>

    <xsl:attribute name="content-width">
      <xsl:choose>
        <xsl:when test="$ignore.image.scaling != 0">auto</xsl:when>
        <xsl:when test="@contentwidth">
          <xsl:value-of select="@contentwidth"/>
        </xsl:when>
        <xsl:when test="number($scale) != 1.0">
          <xsl:value-of select="$scale * 100"/>
          <xsl:text>%</xsl:text>
        </xsl:when>
        <xsl:when test="$scalefit = 1">scale-to-fit</xsl:when>
        <xsl:otherwise>auto</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>

    <xsl:attribute name="content-height">
      <xsl:choose>
        <xsl:when test="$ignore.image.scaling != 0">auto</xsl:when>
        <xsl:when test="@contentdepth">
          <xsl:value-of select="@contentdepth"/>
        </xsl:when>
        <xsl:when test="number($scale) != 1.0">
          <xsl:value-of select="$scale * 100"/>
          <xsl:text>%</xsl:text>
        </xsl:when>
        <xsl:otherwise>auto</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>

    <xsl:if test="@align">
      <xsl:attribute name="text-align">
        <xsl:value-of select="@align"/>
      </xsl:attribute>
    </xsl:if>

    <xsl:if test="@valign">
      <xsl:attribute name="display-align">
        <xsl:choose>
          <xsl:when test="@valign = 'top'">before</xsl:when>
          <xsl:when test="@valign = 'middle'">center</xsl:when>
          <xsl:when test="@valign = 'bottom'">after</xsl:when>
          <xsl:otherwise>auto</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
    </xsl:if>
  </fo:external-graphic>
  </fo:inline>
</xsl:template>

<!-- ==================================================================== -->

<dtm:doc dtm:elements="graphic" dtm:idref="graphic image.process media.filename"/>
<xsl:template match="graphic" dtm:id="graphic">
  <xsl:choose>
    <xsl:when test="../inlineequation">
      <xsl:call-template name="process.image"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:block>
        <xsl:if test="@align">
          <xsl:attribute name="text-align">
            <xsl:value-of select="@align"/>
          </xsl:attribute>
        </xsl:if>
        <xsl:call-template name="process.image"/>
      </fo:block>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:elements="inlinegraphic" dtm:idref="inlinegraphic image.process media.filename"/>
<xsl:template match="inlinegraphic" dtm:id="inlinegraphic">
  <xsl:call-template name="process.image"/>
</xsl:template>

<!-- ==================================================================== -->

<dtm:doc dtm:idref="mediaobjects"/>
<xsl:template match="mediaobject|mediaobjectco" dtm:id="mediaobjects">
<fo:block>
  <xsl:variable name="olist" 
       select="imageobject|imageobjectco|videoobject|audioobject|textobject"/>

  <!-- We are processing all mediaobject in order to allow user edit
       them. -->

  <xsl:for-each select="$olist">
    <xsl:variable name="align">
      <xsl:value-of select="./imagedata[@align][1]/@align"/>
    </xsl:variable>
    <fo:block>
      <xsl:if test="$align != '' ">
        <xsl:attribute name="text-align">
          <xsl:value-of select="$align"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="."/>
    </fo:block>
  </xsl:for-each>
  <xsl:apply-templates select="caption"/>
</fo:block>
</xsl:template>

<dtm:doc dtm:idref="inlinemediaobject"/>
<xsl:template match="inlinemediaobject" dtm:id="inlinemediaobject">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="imageobject"/>
<xsl:template match="imageobject" dtm:id="imageobject">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="data image.process media.filename image.external"/>
<xsl:template match="videodata|imagedata|audiodata" dtm:id="data">
  <xsl:call-template name="process.image"/>
</xsl:template>

<dtm:doc dtm:idref="objects.media"/>
<xsl:template match="audioobject|videoobject" dtm:id="objects.media">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="object.text"/>
<xsl:template match="textobject|textdata" dtm:id="object.text">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="caption"/>
<xsl:template match="caption" dtm:id="caption">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>


<xsl:template name="fo-external-image" dtm:id="image.external">
  <xsl:param name="filename"/>
  <xsl:value-of select="concat('url(', $filename, ')')"/>
</xsl:template>

</xsl:stylesheet>
