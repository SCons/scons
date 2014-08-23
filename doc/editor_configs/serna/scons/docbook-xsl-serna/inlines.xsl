<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                xmlns:se="http://syntext.com/XSL/Format-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

  <!-- General templates -->
<xsl:attribute-set name="inline.monoseq.properties" 
                   use-attribute-sets="monospace.properties">
    <xsl:attribute name="border-left-width">0pt</xsl:attribute>
    <xsl:attribute name="border-right-width">0pt</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="inline.charseq.properties">
    <xsl:attribute name="border-left-width">0pt</xsl:attribute>
    <xsl:attribute name="border-right-width">0pt</xsl:attribute>
</xsl:attribute-set>

  <dtm:doc dtm:idref="inline.italicmonoseq"/>
  <xsl:template name="inline.italicmonoseq" dtm:id="inline.italicmonoseq">
    <fo:inline font-style="italic"
      border-left-width="0pt"
      border-right-width="0pt"
      xsl:use-attribute-sets="monospace.properties">
    <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

<dtm:doc dtm:idref="inline.italicseq"/>
<xsl:template name="inline.italicseq" dtm:id="inline.italicseq">
  <fo:inline font-style="italic"
      border-left-width="0pt"
      border-right-width="0pt">
  <xsl:apply-templates/>
  </fo:inline>
</xsl:template>

  <dtm:doc dtm:idref="inline.boldseq"/>
  <xsl:template name="inline.boldseq" dtm:id="inline.boldseq">
    <fo:inline font-weight="bold"
      border-left-width="0pt"
      border-right-width="0pt">
    <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="inline.monoseq"/>
  <xsl:template name="inline.monoseq" dtm:id="inline.monoseq">
    <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
    <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="inline.charseq"/>
  <xsl:template name="inline.charseq" dtm:id="inline.charseq">
    <fo:inline xsl:use-attribute-sets="inline.charseq.properties">
     <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="inline.boldmonoseq"/>
  <xsl:template name="inline.boldmonoseq" dtm:id="inline.boldmonoseq">
    <fo:inline 
      font-weight="bold" 
      border-left-width="0pt"
      border-right-width="0pt"
      xsl:use-attribute-sets="monospace.properties">
    <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <!-- Misc simple templates -->

  <dtm:doc dtm:idref="parameter"/>
  <xsl:template match="parameter" dtm:id="parameter">
    <xsl:call-template name="inline.italicmonoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="replaceable"/>
  <xsl:template match="replaceable" dtm:id="replaceable">
    <xsl:call-template name="inline.italicmonoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="structfield"/>
  <xsl:template match="structfield" dtm:id="structfield">
    <xsl:call-template name="inline.italicmonoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="authorinitials"/>
  <xsl:template match="authorinitials" dtm:id="authorinitials">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="editor"/>
  <xsl:template match="editor" dtm:id="editor">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="confs"/>
  <xsl:template match="confdates|confgroup|confnum|confsponsor|conftitle" dtm:id="confs">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="accel"/>
  <xsl:template match="accel" dtm:id="accel">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="action"/>
  <xsl:template match="action" dtm:id="action">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="application"/>
  <xsl:template match="application" dtm:id="application">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="database"/>
  <xsl:template match="database" dtm:id="database">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="errorcode"/>
  <xsl:template match="errorcode" dtm:id="errorcode">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="errorname"/>
  <xsl:template match="errorname" dtm:id="errorname">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="errortype"/>
  <xsl:template match="errortype" dtm:id="errortype">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="errortext"/>
  <xsl:template match="errortext" dtm:id="errortext">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="guibutton"/>
  <xsl:template match="guibutton" dtm:id="guibutton">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="guiicon"/>
  <xsl:template match="guiicon" dtm:id="guiicon">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="guilabel"/>
  <xsl:template match="guilabel" dtm:id="guilabel">
    <xsl:call-template name="inline.italicmonoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="guimenu"/>
  <xsl:template match="guimenu" dtm:id="guimenu">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="guimenuitem"/>
  <xsl:template match="guimenuitem" dtm:id="guimenuitem">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="guisubmenu"/>
  <xsl:template match="guisubmenu" dtm:id="guisubmenu">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="isbn-issn"/>
  <xsl:template match="isbn|issn" dtm:id="isbn-issn">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="nums"/>
  <xsl:template match="shortaffil|artpagenums|contractnum|contractsponsor|contrib|invpartnumber|issuenum|pagenums|volumenum|jobtitle" dtm:id="nums">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="hardware"/>
  <xsl:template match="hardware" dtm:id="hardware">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="interface"/>
  <xsl:template match="interface" dtm:id="interface">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="interfacedefinition"/>
  <xsl:template match="interfacedefinition" dtm:id="interfacedefinition">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="keycode"/>
  <xsl:template match="keycode" dtm:id="keycode">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="keysym"/>
  <xsl:template match="keysym" dtm:id="keysym">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="code"/>
  <xsl:template match="code" dtm:id="code">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="mousebutton"/>
  <xsl:template match="mousebutton" dtm:id="mousebutton">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="property"/>
  <xsl:template match="property" dtm:id="property">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="returnvalue"/>
  <xsl:template match="returnvalue" dtm:id="returnvalue">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="structname"/>
  <xsl:template match="structname" dtm:id="structname">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="symbol"/>
  <xsl:template match="symbol" dtm:id="symbol">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="token"/>
  <xsl:template match="token" dtm:id="token">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="type"/>
  <xsl:template match="type" dtm:id="type">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="abbrev"/>
  <xsl:template match="abbrev" dtm:id="abbrev">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="acronym"/>
  <xsl:template match="acronym" dtm:id="acronym">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="citerefentry"/>
  <xsl:template match="citerefentry" dtm:id="citerefentry">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="markup"/>
  <xsl:template match="markup" dtm:id="markup">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="phrase"/>
  <xsl:template match="phrase" dtm:id="phrase">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

<dtm:doc dtm:idref="productname"/>
<xsl:template match="productname" dtm:id="productname">
  <xsl:call-template name="inline.charseq"/>
  <xsl:if test="@class">
    <xsl:call-template name="dingbat">
      <xsl:with-param name="dingbat" select="@class"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>

  <dtm:doc dtm:idref="productnumber"/>
  <xsl:template match="productnumber" dtm:id="productnumber">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="addressparams"/>
  <xsl:template match="pob|street|city|state|postcode|country|otheraddr" dtm:id="addressparams">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="phone|fax"/>
  <xsl:template match="phone|fax" dtm:id="phone|fax">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="publisher"/>
  <xsl:template match="pubdate|publisher|publishername" dtm:id="publisher">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="year"/>
  <xsl:template match="year" dtm:id="year">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="author"/>
  <xsl:template 
    match="honorific|firstname|surname|lineage|othername|author|corpauthor|corpname" dtm:id="author">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="command"/>
  <xsl:template match="command" dtm:id="command">
    <xsl:call-template name="inline.boldseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="keycap"/>
  <xsl:template match="keycap" dtm:id="keycap">
    <xsl:call-template name="inline.boldseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="shortcut"/>
  <xsl:template match="shortcut" dtm:id="shortcut">
    <xsl:call-template name="inline.boldseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="filename"/>
  <xsl:template match="filename" dtm:id="filename">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="literal"/>
  <xsl:template match="literal" dtm:id="literal">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="classname"/>
  <xsl:template match="classname" dtm:id="classname">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="exceptionname"/>
  <xsl:template match="exceptionname" dtm:id="exceptionname">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="interfacename"/>
  <xsl:template match="interfacename" dtm:id="interfacename">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="methodname"/>
  <xsl:template match="methodname" dtm:id="methodname">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="computeroutput"/>
  <xsl:template match="computeroutput" dtm:id="computeroutput">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="constant"/>
  <xsl:template match="constant" dtm:id="constant">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="envar"/>
  <xsl:template match="envar" dtm:id="envar">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="option"/>
  <xsl:template match="option" dtm:id="option">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="prompt"/>
  <xsl:template match="prompt" dtm:id="prompt">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="systemitem"/>
  <xsl:template match="systemitem" dtm:id="systemitem">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="userinput"/>
  <xsl:template match="userinput" dtm:id="userinput">
    <xsl:call-template name="inline.boldmonoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="varname"/>
  <xsl:template match="varname" dtm:id="varname">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="orgname"/>
  <xsl:template match="orgname" dtm:id="orgname">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <!-- Specific templates -->
  <dtm:doc dtm:idref="affiliation"/>
  <xsl:template match="affiliation" dtm:id="affiliation">
    <fo:inline xsl:use-attribute-sets="monospace.properties">
    <xsl:call-template name="inline.monoseq"/>
    </fo:inline>
  </xsl:template>

<dtm:doc dtm:idref="trademark"/>
<xsl:template match="trademark" dtm:id="trademark">
  <xsl:call-template name="inline.charseq"/>
  <xsl:if test="@class">
    <xsl:call-template name="dingbat">
      <xsl:with-param name="dingbat" select="@class"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="citetitle"/>
<xsl:template match="citetitle" dtm:id="citetitle">
  <xsl:choose>
    <xsl:when test="@pubwork = 'article'">
      <xsl:call-template name="gentext.startquote"/>
      <xsl:call-template name="inline.charseq"/>
      <xsl:call-template name="gentext.endquote"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="inline.italicseq"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

  <dtm:doc dtm:idref="email"/>
  <xsl:template match="email" dtm:id="email">
    <xsl:choose>
      <xsl:when test="node()">
        <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
            <xsl:text>&lt;</xsl:text>
            <xsl:apply-templates/>
            <xsl:text>&gt;</xsl:text>
        </fo:inline>
      </xsl:when>
      <xsl:otherwise>
        <fo:inline></fo:inline>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="quote"/>
  <xsl:template match="quote" dtm:id="quote">
    <fo:inline>
      <xsl:if test="node()">
      <xsl:choose>
        <xsl:when test="count(ancestor::quote) mod 2 = 0">
          <xsl:call-template name="gentext.startquote"/>
          <xsl:apply-templates/>
          <xsl:call-template name="gentext.endquote"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="gentext.nestedstartquote"/>
          <xsl:apply-templates/>
          <xsl:call-template name="gentext.nestedendquote"/>
        </xsl:otherwise>
      </xsl:choose>
      </xsl:if>
    </fo:inline>
  </xsl:template>

<dtm:doc dtm:idref="sgmltag"/>
<xsl:template match="sgmltag" dtm:id="sgmltag">
  <xsl:variable name="class">
    <xsl:choose>
      <xsl:when test="@class">
        <xsl:value-of select="@class"/>
      </xsl:when>
      <xsl:otherwise>element</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="$class='attribute'">
      <xsl:call-template name="inline.monoseq"/>
    </xsl:when>
    <xsl:when test="$class='attvalue'">
      <xsl:call-template name="inline.monoseq"/>
    </xsl:when>
    <xsl:when test="$class='element'">
      <xsl:call-template name="inline.monoseq"/>
    </xsl:when>
    <xsl:when test="$class='endtag'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&lt;/</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>&gt;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='genentity'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&amp;</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='numcharref'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&amp;#</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='paramentity'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>%</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='pi'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&lt;?</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>&gt;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='xmlpi'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&lt;?</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>?&gt;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='starttag'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&lt;</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>&gt;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='emptytag'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&lt;</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>/&gt;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:when test="$class='sgmlcomment'">
      <fo:inline xsl:use-attribute-sets="inline.monoseq.properties">
          <xsl:text>&lt;!--</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>--&gt;</xsl:text>
      </fo:inline>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="inline.charseq"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

  <dtm:doc dtm:idref="citation"/>
  <xsl:template match="citation" dtm:id="citation">
    <xsl:text>[</xsl:text>
    <xsl:call-template name="inline.charseq"/>
    <xsl:text>]</xsl:text>
  </xsl:template>

  <dtm:doc dtm:idref="emphasis"/>
  <xsl:template match="emphasis" dtm:id="emphasis">
    <xsl:choose>
      <xsl:when test="@role='bold'">
        <xsl:call-template name="inline.boldseq"/>
      </xsl:when>
      <xsl:when test="@role='underline'">
        <fo:inline 
          border-left-width="0pt"
          border-right-width="0pt"
          text-decoration="underline">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='strikethrough'">
        <fo:inline 
          border-left-width="0pt"
          border-right-width="0pt"
          text-decoration="line-through">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="count(ancestor::emphasis) mod 2">
            <fo:inline 
              border-left-width="0pt"
              border-right-width="0pt"
              font-style="normal">
              <xsl:apply-templates/>
            </fo:inline>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="inline.italicseq"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- xsl:template match="emphasis">
    <fo:inline font-style="italic"
      border-left-width="0pt"
      border-right-width="0pt">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template -->

  <dtm:doc dtm:idref="firstterm"/>
  <xsl:template match="firstterm" dtm:id="firstterm">
    <fo:inline font-weight="bold"
      border-left-width="0pt"
      border-right-width="0pt">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="glossterm"/>
  <xsl:template match="glossterm" dtm:id="glossterm">
    <fo:inline font-style="italic" 
      font-weight="bold"
      border-left-width="0pt"
      border-right-width="0pt">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="ulink"/>
  <xsl:template match="ulink" dtm:id="ulink">
    <!-- Keep all the content within one area -->
    <fo:inline text-decoration="underline">

      <!-- Separate inline area will draw empty tag if content is empty -->
      <fo:inline>
        <xsl:apply-templates/>
      </fo:inline>

      <!-- Use the extensions if processed in Serna -->
      <xsl:choose>
        <xsl:when test="$use-serna-extensions">
          <xsl:apply-templates select="@url" mode="ulink"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text> [</xsl:text>
          <xsl:value-of select="@url"/>
          <xsl:text>]</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </fo:inline>
  </xsl:template>

  <!-- Call separate template for @url to make @url the context node -->
  <dtm:doc dtm:idref="url.ulink"/>
  <xsl:template match="@url" mode="ulink" dtm:id="url.ulink">
    <fo:inline>
      <xsl:text> [</xsl:text>
      <se:line-edit width="4cm" value="{string(.)}" />
      <xsl:text>]</xsl:text>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="link"/>
  <xsl:template match="link" dtm:id="link">
    <fo:inline>
      <xsl:if test="@endterm">
          <xsl:value-of select="id(@endterm)"/>
      </xsl:if>
      <xsl:apply-templates/>
      <xsl:text> [</xsl:text>
      <xsl:value-of select="@linkend"/>
      <xsl:text>]</xsl:text>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="olink"/>
  <xsl:template match="olink" dtm:id="olink">
    <fo:inline>
      <xsl:choose>
        <xsl:when test="node()">
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>[]</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="attribution"/>
  <xsl:template match="attribution" dtm:id="attribution">
    <fo:inline><xsl:apply-templates/></fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="lineannotation"/>
  <xsl:template match="lineannotation" dtm:id="lineannotation">
    <fo:inline font-style="italic">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="remark"/>
  <xsl:template match="remark" dtm:id="remark">
    <xsl:if test="$show.remarks != 0">
      <fo:block font-style="italic">
        <xsl:apply-templates/>
      </fo:block>
    </xsl:if>
  </xsl:template>

  <dtm:doc dtm:idref="copyright"/>
  <xsl:template match="copyright" dtm:id="copyright">
    <fo:inline>
      <xsl:if test="node()">
        <xsl:call-template name="gentext">
          <xsl:with-param name="key" select="'copyright'"/>
        </xsl:call-template>
        <xsl:text>&#x00A9; </xsl:text>
        <xsl:call-template name="copyright.years">
          <xsl:with-param name="years" select="year"/>
          <xsl:with-param name="print.ranges" select="$make.year.ranges"/>
          <xsl:with-param name="single.year.ranges"
            select="$make.single.year.ranges"/>
        </xsl:call-template>
        <xsl:text>&#160;</xsl:text>
        <xsl:apply-templates select="holder"/>
      </xsl:if>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="holder"/>  
  <xsl:template match="holder" dtm:id="holder">
    <xsl:call-template name="inline.charseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="anchor"/>
  <xsl:template match="anchor" dtm:id="anchor">
   <xsl:if test="$show.preamble.editing">
     <fo:block xsl:use-attribute-sets="preamble.attributes">
       <xsl:call-template name="gentext.template">
         <xsl:with-param name="name" select="'draftarea'"/>
         <xsl:with-param name="context" select="'empty'"/>
       </xsl:call-template>
       <xsl:text> "</xsl:text>
       <xsl:value-of select="local-name(.)"/>
       <xsl:text>" </xsl:text>
        <fo:inline font-size="0.75em" color="gray"><xsl:text> (anchor: </xsl:text>
          <xsl:choose>
            <xsl:when test="@id">
              <xsl:value-of select="@id"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>no ID</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>) </xsl:text>
        </fo:inline>
     </fo:block>
   </xsl:if>

  </xsl:template>

  <dtm:doc dtm:idref="member"/>
  <xsl:template match="member" dtm:id="member">
    <fo:inline><xsl:apply-templates/></fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="optional"/>
  <xsl:template match="optional" dtm:id="optional">
    <xsl:value-of select="$arg.choice.opt.open.str"/>
    <xsl:call-template name="inline.charseq"/>
    <xsl:value-of select="$arg.choice.opt.close.str"/>
  </xsl:template>

  <dtm:doc dtm:idref="footnoteref"/>
  <xsl:template match="footnoteref" dtm:id="footnoteref">
    <fo:inline baseline-shift="super">
      <xsl:choose>
        <xsl:when test="@linkend">
          <xsl:value-of select="id(@linkend)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>[</xsl:text>
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="name" select="'footnote'"/>
            <xsl:with-param name="context" select="'empty'"/>
          </xsl:call-template>
          <xsl:text>: </xsl:text>
          <xsl:if test="@label">
            <xsl:value-of select="@label"/>
            <xsl:text> </xsl:text>
          </xsl:if>
          <xsl:text>]</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="title.footnote"/>
  <xsl:template match="title/footnote" dtm:id="title.footnote">
    <fo:inline font-size="{$footnote.font.size}" baseline-shift="super">
      <xsl:choose>
        <xsl:when test="@id">
          <xsl:value-of select="id(@linkend)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>[</xsl:text>
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="context" select="'empty'"/>
            <xsl:with-param name="name" select="'footnote'"/>
          </xsl:call-template>
          <xsl:text>]</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="function"/>
  <xsl:template match="function" dtm:id="function">
    <xsl:call-template name="inline.monoseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="superscript"/>
  <xsl:template match="superscript" dtm:id="superscript">
    <fo:inline 
      border-left-width="0pt"
      border-right-width="0pt"
      baseline-shift="super">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="subscript"/>
  <xsl:template match="subscript" dtm:id="subscript">
    <fo:inline 
      border-left-width="0pt"
      border-right-width="0pt"
      baseline-shift="sub">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="keycombo"/>
  <xsl:template match="keycombo" dtm:id="keycombo">
    <xsl:variable name="action" select="@action"/>
    <xsl:variable name="joinchar">
      <xsl:choose>
        <xsl:when test="$action='seq'"><xsl:text> </xsl:text></xsl:when>
        <xsl:when test="$action='simul'">+</xsl:when>
        <xsl:when test="$action='press'">-</xsl:when>
        <xsl:when test="$action='click'">-</xsl:when>
        <xsl:when test="$action='double-click'">-</xsl:when>
        <xsl:when test="$action='other'"></xsl:when>
        <xsl:otherwise>-</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <fo:inline xsl:use-attribute-sets="inline.charseq.properties">
      <xsl:for-each select="*">
        <xsl:if test="position() > 1">
            <xsl:value-of select="$joinchar"/>
      </xsl:if>
      <xsl:apply-templates select="."/>
     </xsl:for-each> 
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="menuchoice"/>
  <xsl:template match="menuchoice" dtm:id="menuchoice">
    <fo:inline xsl:use-attribute-sets="inline.charseq.properties">
        <xsl:call-template name="process.menuchoice"/>
        <xsl:if test="shortcut[not(self::processing-instruction('se:choice'))]">
          <xsl:text> (</xsl:text>
          <xsl:apply-templates select="shortcut"/>
          <xsl:text>)</xsl:text>
        </xsl:if>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="process.menuchoice"/>
  <xsl:template name="process.menuchoice" dtm:id="process.menuchoice">
    <xsl:param name="nodelist" select="guibutton|guiicon|guilabel|guimenu|guimenuitem|guisubmenu|interface"/><!-- not(shortcut) -->
    <xsl:param name="count" select="1"/>
    
    <xsl:choose>
      <xsl:when test="$count>count($nodelist)"></xsl:when>
        <xsl:when test="$count=1">
          <xsl:apply-templates select="$nodelist[$count=position()]"/>
          <xsl:call-template name="process.menuchoice">
            <xsl:with-param name="nodelist" select="$nodelist"/>
            <xsl:with-param name="count" select="$count+1"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="node" select="$nodelist[$count=position()]"/>
          <xsl:choose>
            <xsl:when test="name($node)='guimenuitem'
                            or name($node)='guisubmenu'">
              <xsl:value-of select="$menuchoice.menu.separator"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="$menuchoice.separator"/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:apply-templates select="$node"/>
          <xsl:call-template name="process.menuchoice">
            <xsl:with-param name="nodelist" select="$nodelist"/>
            <xsl:with-param name="count" select="$count+1"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:template>

  <dtm:doc dtm:idref="foreignphrase"/>
  <xsl:template match="foreignphrase" dtm:id="foreignphrase">
    <xsl:call-template name="inline.italicseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="wordasword"/>
  <xsl:template match="wordasword" dtm:id="wordasword">
    <xsl:call-template name="inline.italicseq"/>
  </xsl:template>

  <dtm:doc dtm:idref="medialabel"/>
  <xsl:template match="medialabel" dtm:id="medialabel">
    <xsl:call-template name="inline.italicseq"/>
  </xsl:template>

</xsl:stylesheet>
