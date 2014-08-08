<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

  <dtm:doc dtm:idref="block.object"/>
  <xsl:template name="block.object" dtm:id="block.object">
    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="para"/>
  <xsl:template match="para" dtm:id="para">
    <fo:block xsl:use-attribute-sets="normal.para.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="sconsdoc"/>
  <xsl:template match="sconsdoc" dtm:id="sconsdoc">
    <fo:block xsl:use-attribute-sets="normal.para.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="simpara"/>
  <xsl:template match="simpara" dtm:id="simpara">
    <fo:block xsl:use-attribute-sets="normal.para.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="date-releaseinfo"/>
  <xsl:template match="date|releaseinfo" dtm:id="date-releaseinfo">
    <fo:block xsl:use-attribute-sets="normal.para.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="abstract"/>
  <xsl:template match="abstract" dtm:id="abstract">
    <fo:block>
      <xsl:choose>
        <xsl:when test="title">
          <xsl:apply-templates select="title" mode="plain.formal.title.mode"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="formal.title.gentext">
            <xsl:with-param name="key" select="'abstract'"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="*[local-name(.) != 'title']"/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="blockquote"/>
  <xsl:template match="blockquote" dtm:id="blockquote">
    <fo:block xsl:use-attribute-sets="blockquote.properties">
      <fo:block>
        <xsl:if test="title">
          <fo:block xsl:use-attribute-sets="formal.title.properties">
            <xsl:apply-templates select="title" mode="plain.formal.title.mode"/>
          </fo:block>
        </xsl:if>
        <xsl:apply-templates select="*[not(self::title or self::attribution)
                        or self::processing-instruction('se:choice')]"/>
      </fo:block>
      <xsl:if test="attribution">
        <fo:block text-align="right">
          <xsl:text>&#x2014;&#160;</xsl:text>
          <xsl:apply-templates select="attribution"/>
        </fo:block>
      </xsl:if>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="formalpara"/>
  <xsl:template match="formalpara" dtm:id="formalpara">
    <fo:block xsl:use-attribute-sets="normal.para.properties">
      <xsl:apply-templates mode="formalpara"/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="title.formalpara.formalpara"/>
  <xsl:template match="formalpara/title" mode="formalpara" dtm:id="title.formalpara.formalpara">
    <xsl:variable name="titleStr" select="."/>
    <xsl:variable name="lastChar">
      <xsl:if test="$titleStr != ''">
        <xsl:value-of select="substring($titleStr,string-length($titleStr),1)"/>
      </xsl:if>
    </xsl:variable>
    
    <fo:inline font-weight="bold"
      keep-with-next.within-line="always"
      padding-right="1em">
      <xsl:apply-templates/>
      <xsl:if test="$lastChar != ''
                    and not(contains($title.end.punct, $lastChar))">
        <xsl:value-of select="$default.title.end.punct"/>
      </xsl:if>
    </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="para.formalpara.formalpara"/>  
  <xsl:template match="formalpara/para" mode="formalpara" dtm:id="para.formalpara.formalpara">
    <xsl:choose>
      <xsl:when test="itemizedlist|orderedlist|segmentedlist|variablelist">
        <fo:block>
          <xsl:apply-templates/>
        </fo:block>
      </xsl:when>
      <xsl:otherwise>
        <fo:inline>
          <xsl:apply-templates/>
        </fo:inline>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="indexterm.formalpara"/> 
  <xsl:template match="indexterm"  mode="formalpara" dtm:id="indexterm.formalpara">
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

  <dtm:doc dtm:idref="niwct"/> 
  <xsl:template match="note|important|warning|caution|tip" dtm:id="niwct">
    <fo:block xsl:use-attribute-sets="note.properties">
      <fo:block xsl:use-attribute-sets="admonition.title.properties">
        <xsl:choose>
          <xsl:when test="title[not(self::processing-instruction('se:choice'))]">
            <xsl:apply-templates select="title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="gentext">
              <xsl:with-param name="key" select="local-name(.)"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </fo:block>
      
      <fo:block>
        <xsl:apply-templates select="*[not(self::title)
            or self::processing-instruction('se:choice')]"/>
      </fo:block>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="authorgroup"/> 
  <xsl:template match="authorgroup" dtm:id="authorgroup">
    <fo:block>
        <xsl:apply-templates mode="authorgroup.mode"/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="node.authorgroup-mode"/>
  <xsl:template match="node()" mode="authorgroup.mode" dtm:id="node.authorgroup-mode">
    <xsl:apply-templates select='.'/>
    <xsl:choose>
      <xsl:when test="position() != last()">
        <xsl:text>, </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>.</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="legalnotice"/>
  <xsl:template match="legalnotice" dtm:id="legalnotice">
    <xsl:choose>
      <xsl:when test="title">
        <xsl:apply-templates select="title" mode="plain.formal.title.mode"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="formal.title.gentext">
          <xsl:with-param name="key" select="'legalnotice'"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates select="*[not(self::title)
                    or self::processing-instruction('se:choice')]"/>
  </xsl:template>

  <!-- Allow revhistory in context -->

  <dtm:doc dtm:idref="revhistory"/>
  <xsl:template match="revhistory" dtm:id="revhistory">
    <xsl:apply-templates select="." mode="rev.mode"/>
  </xsl:template>

  <dtm:doc dtm:idref="revhistory.rev-mode"/>
  <xsl:template match="revhistory" mode="rev.mode" dtm:id="revhistory.rev-mode">
    <fo:block>
      <xsl:call-template name="formal.title.gentext">
        <xsl:with-param name="key" select="'revhistory'"/>
      </xsl:call-template>
      <xsl:apply-templates select="revision" mode="rev.mode"/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="revision.rev-mode"/>
  <xsl:template match="revision" mode="rev.mode" dtm:id="revision.rev-mode">
    <fo:block xsl:use-attribute-sets="normal.para.properties">
      <xsl:apply-templates mode="rev.mode"/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="revnumber.rev-mode"/>
  <xsl:template match="revnumber" mode="rev.mode" dtm:id="revnumber.rev-mode">
    <fo:block>
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'revision'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="authorinitials.rev-mode"/>
  <xsl:template match="authorinitials" mode="rev.mode" dtm:id="authorinitials.rev-mode">
    <fo:block>
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'revisedby'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="all.rev-mode"/>
  <xsl:template match="*" mode="rev.mode" dtm:id="all.rev-mode">
    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="address"/>
  <xsl:template match="address" dtm:id="address">
    <fo:block 
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="footnote"/>
  <xsl:template match="footnote" dtm:id="footnote">
    <fo:block font-size="{$footnote.font.size}">
      <xsl:if test="@id">
        <fo:inline font-style="italic">
          <xsl:text>[</xsl:text>
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="context" select="'empty'"/>
            <xsl:with-param name="name" select="'footnote'"/>
          </xsl:call-template>
          <xsl:text>: </xsl:text>
          <xsl:value-of select="@id"/>
          <xsl:text>]</xsl:text>
        </fo:inline>
      </xsl:if>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="programlisting"/>
  <xsl:template match="programlisting|screen|synopsis|literallayout" name="programlisting" dtm:id="programlisting">
    <xsl:choose>
      <xsl:when test="$shade.verbatim != 0">
        <fo:block
          white-space-treatment='preserve'
          white-space-collapse='false'
          linefeed-treatment="preserve"
          xsl:use-attribute-sets="shade.verbatim.style verbatim.properties">
          <xsl:apply-templates/>
        </fo:block>
      </xsl:when>
      <xsl:otherwise>
        <fo:block
          white-space-collapse='false'
          linefeed-treatment="preserve"
          xsl:use-attribute-sets="verbatim.properties">
          <xsl:apply-templates/>
        </fo:block>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="summary"/> 
  <xsl:template match="summary" dtm:id="summary">
    <fo:block xsl:use-attribute-sets="admonition.title.properties">
      <xsl:text>Summary</xsl:text>
    </fo:block>
      
    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="builder"/> 
  <xsl:template match="builder" dtm:id="builder">
    <fo:block xsl:use-attribute-sets="admonition.title.properties">
      <xsl:text>Builder '</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>'</xsl:text>
    </fo:block>

    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="cvar"/> 
  <xsl:template match="cvar" dtm:id="cvar">
    <fo:block xsl:use-attribute-sets="admonition.title.properties">
      <xsl:text>CVar '</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>'</xsl:text>
    </fo:block>

    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="function"/> 
  <xsl:template match="function" dtm:id="function">
    <fo:block xsl:use-attribute-sets="admonition.title.properties">
      <xsl:text>Function '</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>'</xsl:text>
    </fo:block>

    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="tool"/> 
  <xsl:template match="tool" dtm:id="tool">
    <fo:block xsl:use-attribute-sets="admonition.title.properties">
      <xsl:text>Tool '</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>'</xsl:text>
    </fo:block>

    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="scons_example"/>
  <xsl:template match="scons_example" name="scons_example" dtm:id="scons_example">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#94caee">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="example_commands"/>
  <xsl:template match="example_commands" name="example_commands" dtm:id="example_commands">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#94caee">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="scons_example_file"/>
  <xsl:template match="scons_example_file" name="scons_example_file" dtm:id="scons_example_file">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#eed27b">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>


  <dtm:doc dtm:idref="scons_output"/>
  <xsl:template match="scons_output" name="scons_output" dtm:id="scons_output">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#94caee">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="scons_output_command"/>
  <xsl:template match="scons_output_command" name="scons_output_command" dtm:id="scons_output_command">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="shade.verbatim.style verbatim.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="sconstruct"/>
  <xsl:template match="sconstruct" name="sconstruct" dtm:id="sconstruct">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#94caee">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="file"/>
  <xsl:template match="file" name="file" dtm:id="file">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#eed27b">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="directory"/>
  <xsl:template match="directory" name="directory" dtm:id="directory">
    <fo:block
      white-space-treatment='preserve'
      white-space-collapse='false'
      linefeed-treatment="preserve"
      xsl:use-attribute-sets="verbatim.properties"
      background-color="#eed27b">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

<dtm:doc dtm:idref="epigraph"/>
<xsl:template match="epigraph" dtm:id="epigraph">
  <fo:block>
    <xsl:apply-templates select="para|simpara|formalpara|literallayout"/>
    <fo:inline>
      <xsl:text>&#x2014;&#160;</xsl:text>
      <xsl:apply-templates select="attribution"/>
    </fo:inline>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="sidebar"/>
<xsl:template match="sidebar" dtm:id="sidebar">
  <fo:block xsl:use-attribute-sets="sidebar.properties">
    <xsl:if test="./title">
      <fo:block font-weight="bold">
        <xsl:apply-templates select="./title" mode="sidebar.title.mode"/>
      </fo:block>
    </xsl:if>

    <xsl:apply-templates select="*[not(self::title)
                    or self::processing-instruction('se:choice')]"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="title.sidebar.sidebar-title-mode"/>
<xsl:template match="sidebar/title" mode="sidebar.title.mode" dtm:id="title.sidebar.sidebar-title-mode">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="msgset"/>
<xsl:template match="msgset" dtm:id="msgset">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="msgentry"/>
<xsl:template match="msgentry" dtm:id="msgentry">
  <xsl:call-template name="block.object"/>
</xsl:template>

<dtm:doc dtm:idref="simplemsgentry"/>
<xsl:template match="simplemsgentry" dtm:id="simplemsgentry">
  <xsl:call-template name="block.object"/>
</xsl:template>

<dtm:doc dtm:idref="msg"/>
<xsl:template match="msg" dtm:id="msg">
  <xsl:call-template name="block.object"/>
</xsl:template>

<dtm:doc dtm:idref="msgmain"/>
<xsl:template match="msgmain" dtm:id="msgmain">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="msgsub"/>
<xsl:template match="msgsub" dtm:id="msgsub">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="msgrel"/>
<xsl:template match="msgrel" dtm:id="msgrel">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="msgtext"/>
<xsl:template match="msgtext" dtm:id="msgtext">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="msginfo"/>
<xsl:template match="msginfo" dtm:id="msginfo">
  <xsl:call-template name="block.object"/>
</xsl:template>

<dtm:doc dtm:idref="msglevel"/>
<xsl:template match="msglevel" dtm:id="msglevel">
  <fo:block>
    <fo:inline font-weight="bold">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'msglevel'"/>
      </xsl:call-template>
    </fo:inline>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="msgorig"/>
<xsl:template match="msgorig" dtm:id="msgorig">
  <fo:block>
    <fo:inline font-weight="bold">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'msgorig'"/>
      </xsl:call-template>
    </fo:inline>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="msgaud"/>
<xsl:template match="msgaud" dtm:id="msgaud">
  <fo:block>
    <fo:inline font-weight="bold">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'msgaud'"/>
      </xsl:call-template>
    </fo:inline>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="msgexplan"/>
<xsl:template match="msgexplan" dtm:id="msgexplan">
  <xsl:call-template name="block.object"/>
</xsl:template>

<dtm:doc dtm:idref="title.msgexplan"/>
<xsl:template match="msgexplan/title" dtm:id="title.msgexplan">
  <fo:block font-weight="bold">
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="ackno"/>
<xsl:template match="ackno" dtm:id="ackno">
  <fo:block xsl:use-attribute-sets="normal.para.properties">
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="highlights"/>
<xsl:template match="highlights" dtm:id="highlights">
  <xsl:call-template name="block.object"/>
</xsl:template>

<dtm:doc dtm:idref="calclines"/>
<xsl:template name="calclines" dtm:id="calclines">
  <xsl:param name="marks"/>
  <xsl:param name="text" select="text()"/>
  <xsl:param name="curline" select="0"/>
  <xsl:variable name="lfeed" select="'&#xA;'"/>
  <xsl:variable name="num" select="concat(' ', $curline, ' ')"/>
  <xsl:choose>
    <xsl:when test="contains($marks, $num)">
      <xsl:variable name="str" select="concat(substring-before($marks, $num), substring-after($marks, $num))"/>
      <xsl:variable name="mark" select="substring-before(substring-after(substring-after($marks, $num), '('), ')')"/>
      <xsl:value-of select="concat('(', $mark, ')')"/>
      <xsl:call-template name="calclines">
        <xsl:with-param name="marks" select="$str"/>
        <xsl:with-param name="text" select="$text"/>
        <xsl:with-param name="curline" select="$curline"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:when test="contains($text, $lfeed)">
      <xsl:value-of select="$lfeed"/>
      <xsl:call-template name="calclines">
        <xsl:with-param name="marks" select="$marks"/>
        <xsl:with-param name="text" select="substring-after($text, $lfeed)"/>
        <xsl:with-param name="curline" select="$curline + 1"/>
      </xsl:call-template>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="areaspec.calc"/>
<xsl:template match="areaspec" mode="calc" dtm:id="areaspec.calc">
  <xsl:apply-templates mode="calc"/>
</xsl:template>

<dtm:doc dtm:idref="areaset.calc"/>
<xsl:template match="areaset" mode="calc" dtm:id="areaset.calc">
  <xsl:apply-templates mode="calc"/>
  <xsl:value-of select="concat('(', string(position()), ')')"/>
</xsl:template>

<dtm:doc dtm:idref="area.calc"/>
<xsl:template match="area" mode="calc" dtm:id="area.calc">
  <xsl:variable name="pos" select="number(normalize-space(@coords))"/>
  <xsl:if test="not($pos = 'NaN')">
    <xsl:text> </xsl:text>
    <xsl:value-of select="string($pos)"/>
    <xsl:text> </xsl:text>
  </xsl:if>
  <xsl:if test="not(parent::areaset)">
    <xsl:value-of select="concat('(', string(position()), ')')"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="programlisting.programlistingco"/>
<xsl:template match="programlistingco/programlisting" dtm:id="programlisting.programlistingco">
  <xsl:variable name="marks">
    <xsl:apply-templates select="../areaspec" mode="calc"/>
  </xsl:variable>
  <xsl:variable name="lines">
     <xsl:call-template name="calclines">
        <xsl:with-param name="marks" select="$marks"/>
     </xsl:call-template>
  </xsl:variable> 
  <fo:table>
    <fo:table-column column-number="1"/>
    <fo:table-column column-number="2" column-width="2cm" />
    <fo:table-body>
      <fo:table-row>
         <fo:table-cell>
           <xsl:call-template name="programlisting"/>
         </fo:table-cell>
         <fo:table-cell>
           <fo:block linefeed-treatment="preserve"
                     xsl:use-attribute-sets="shade.verbatim.style verbatim.properties">
             <xsl:value-of select="$lines"/>
           </fo:block>
         </fo:table-cell>
      </fo:table-row>
    </fo:table-body>
  </fo:table>
</xsl:template>

<dtm:doc dtm:idref="programlistingco"/>
<xsl:template match="programlistingco|areaspec|areaset|area|screenco" dtm:id="programlistingco">
  <fo:block xsl:use-attribute-sets="normal.para.properties">
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="calloutlist"/>
<xsl:template match="calloutlist" dtm:id="calloutlist">
  <fo:block>
    <xsl:apply-templates 
      select="title[not(self::processing-instruction('se:choice'))]" 
      mode="plain.formal.title.mode"/>
  
  <fo:list-block xsl:use-attribute-sets="list.block.spacing"
                 provisional-label-separation="0.2em">
    <xsl:attribute name="provisional-distance-between-starts">
      <xsl:choose>
        <xsl:when test="$label-width != ''">
          <xsl:value-of select="$label-width"/>
        </xsl:when>
        <xsl:otherwise>2em</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:apply-templates select="callout"/>
  </fo:list-block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="callout.calloutlist"/>
<xsl:template match="calloutlist/callout" dtm:id="callout.calloutlist">
  <fo:list-item xsl:use-attribute-sets="list.item.spacing">
    <fo:list-item-label end-indent="label-end()">
      <fo:block>           
        <xsl:variable name="x" select="id(@arearefs)"/>
        <xsl:for-each select="$x[1]/parent::*[1]/*">
          <xsl:if test="@id = $x/@id">
            <xsl:value-of select="concat('(', string(position()), ')')"/>
          </xsl:if>
        </xsl:for-each>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
        <xsl:apply-templates/>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

<dtm:doc dtm:idref="co"/>
<xsl:template match="co" dtm:id="co">
  <fo:inline>
    <xsl:text>(</xsl:text>
    <xsl:value-of select="position() div 2"/>
    <xsl:text>)</xsl:text>
  </fo:inline>
</xsl:template>

<!-- Indexterms -->
  <dtm:doc dtm:idref="indexterm"/>
  <xsl:template match="indexterm" dtm:id="indexterm">
    <xsl:if test="'1' = $show.preamble.editing">
      <fo:block  background-color="#e0e0e0" 
                 border-width="1pt"
                 border-color="black">
        <xsl:choose>
          <xsl:when test="@class='endofrange'">
            <xsl:text>End of range</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates mode="startofrange"/>
          </xsl:otherwise>
        </xsl:choose>
      </fo:block>
    </xsl:if>
  </xsl:template>
  
  <dtm:doc dtm:idref="primary.startofrange"/>
  <xsl:template match="primary" mode="startofrange" dtm:id="primary.startofrange">
    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>
  
  <dtm:doc dtm:idref="tertiary.startofrange"/>
  <xsl:template match="tertiary" mode="startofrange" dtm:id="tertiary.startofrange">
    <fo:block start-indent="4em">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="see.startofrange"/>
  <xsl:template match="seealso|see|secondary" mode="startofrange" dtm:id="see.startofrange">
    <fo:block start-indent="2em">
      <xsl:if test="local-name(.)='seealso'">
        <xsl:text>See also: </xsl:text>
      </xsl:if>
      <xsl:if test="local-name(.)='see'">
        <xsl:text>See: </xsl:text>
      </xsl:if>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

</xsl:stylesheet>
