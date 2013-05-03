<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="xse dtm"
                version='1.0'>

<xsl:include href="common-table.xsl"/>

<dtm:doc dtm:idref="tables"/>
<xsl:template match="table|informaltable" dtm:id="tables">
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
  <fo:block>
    <xsl:attribute name="span">
      <xsl:choose>
        <xsl:when test="@pgwide=1">all</xsl:when>
        <xsl:otherwise>none</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>

    <fo:block xsl:use-attribute-sets="formal.object.properties">
      <xsl:if test="$placement = 'before' and not(self::informaltable)">
        <xsl:call-template name="formal.object.heading">
          <xsl:with-param name="placement" select="$placement"/>
        </xsl:call-template>
      </xsl:if>

      <xsl:apply-templates select="tgroup" mode="main"/>

      <xsl:if test="$placement != 'before' and not(self::informaltable)">
        <xsl:call-template name="formal.object.heading">
          <xsl:with-param name="placement" select="$placement"/>
        </xsl:call-template>
      </xsl:if>
    </fo:block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="tgroup.main"/>
<xsl:template match="tgroup" mode="main" dtm:id="tgroup.main">
  <xsl:if test="$show.preamble.editing">
    <fo:block xsl:use-attribute-sets="preamble.attributes">
      <fo:block background-color="transparent"
        xsl:use-attribute-sets="title.content.properties formal.title.properties">
        <xsl:call-template name="gentext.template">
          <xsl:with-param name="name" select="'draftarea'"/>
          <xsl:with-param name="context" select="'empty'"/>
        </xsl:call-template>
        <xsl:text> "</xsl:text>
        <xsl:value-of select="local-name(.)"/>
        <xsl:text>" </xsl:text>
        <xsl:call-template name="gentext.template">
          <xsl:with-param name="name" select="'metainfo'"/>
          <xsl:with-param name="context" select="'empty'"/>
        </xsl:call-template>
        <xsl:text>. </xsl:text>
        <xsl:if test="@cols"> 
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="name" select="'columns'"/>
            <xsl:with-param name="context" select="'empty'"/>
          </xsl:call-template>
          <xsl:text>: </xsl:text>
          <xsl:value-of select="@cols"/>
        </xsl:if>
        <xsl:text>. (</xsl:text>
        <xsl:call-template name="gentext.template">
          <xsl:with-param name="name" select="'edit-attrs'"/>
          <xsl:with-param name="context" select="'empty'"/>
        </xsl:call-template>
        <xsl:text>)</xsl:text>
      </fo:block>
      <xsl:apply-templates select="colspec|spanspec"/>
    </fo:block>
  </xsl:if>
  <fo:table border-collapse="collapse">
    <xsl:call-template name="table.frame"/>
    <xsl:if test="following-sibling::tgroup">
      <xsl:attribute name="border-bottom-width">0pt</xsl:attribute>
      <xsl:attribute name="border-bottom-style">none</xsl:attribute>
      <xsl:attribute name="padding-bottom">0pt</xsl:attribute>
      <xsl:attribute name="margin-bottom">0pt</xsl:attribute>
      <xsl:attribute name="space-after">0pt</xsl:attribute>
      <xsl:attribute name="space-after.minimum">0pt</xsl:attribute>
      <xsl:attribute name="space-after.optimum">0pt</xsl:attribute>
      <xsl:attribute name="space-after.maximum">0pt</xsl:attribute>
    </xsl:if>
    <xsl:if test="preceding-sibling::tgroup">
      <xsl:attribute name="border-top-width">0pt</xsl:attribute>
      <xsl:attribute name="border-top-style">none</xsl:attribute>
      <xsl:attribute name="padding-top">0pt</xsl:attribute>
      <xsl:attribute name="margin-top">0pt</xsl:attribute>
      <xsl:attribute name="space-before">0pt</xsl:attribute>
      <xsl:attribute name="space-before.minimum">0pt</xsl:attribute>
      <xsl:attribute name="space-before.optimum">0pt</xsl:attribute>
      <xsl:attribute name="space-before.maximum">0pt</xsl:attribute>
    </xsl:if>
    <xsl:if test="(colspec|thead/colspec|tfoot/colspec|tbody/colspec)[contains(@colwidth, '*')]">
      <xsl:attribute name="table-layout">fixed</xsl:attribute>
    </xsl:if>
    <xsl:apply-templates select="."/>
  </fo:table>
</xsl:template>

<dtm:doc dtm:idref="specs"/>
<xsl:template match="colspec|spanspec" dtm:id="specs">
  <fo:block white-space-treatment='preserve' white-space-collapse='false'>
    <xsl:value-of select="concat(translate(local-name(.), 
        'colspean', 'COLSPEAN'), ': ')"/>
      <fo:inline font-style="italic">
        <xsl:for-each select="@*">
            <xsl:value-of select="concat(local-name(.), '=', ., '   ')"/>
        </xsl:for-each>
      </fo:inline>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="table.frame"/>
<xsl:template name="table.frame" dtm:id="table.frame">
  <xsl:variable name="frame">
    <xsl:choose>
      <xsl:when test="../@frame">
        <xsl:value-of select="../@frame"/>
      </xsl:when>
      <xsl:otherwise>all</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="$frame='all'">
      <xsl:attribute name="border-left-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-right-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-left-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-right-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-left-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
      <xsl:attribute name="border-right-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
    </xsl:when>
    <xsl:when test="$frame='bottom'">
      <xsl:attribute name="border-left-style">none</xsl:attribute>
      <xsl:attribute name="border-right-style">none</xsl:attribute>
      <xsl:attribute name="border-top-style">none</xsl:attribute>
      <xsl:attribute name="border-bottom-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
    </xsl:when>
    <xsl:when test="$frame='sides'">
      <xsl:attribute name="border-left-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-right-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-style">none</xsl:attribute>
      <xsl:attribute name="border-bottom-style">none</xsl:attribute>
      <xsl:attribute name="border-left-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-right-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-left-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
      <xsl:attribute name="border-right-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
    </xsl:when>
    <xsl:when test="$frame='top'">
      <xsl:attribute name="border-left-style">none</xsl:attribute>
      <xsl:attribute name="border-right-style">none</xsl:attribute>
      <xsl:attribute name="border-top-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-style">none</xsl:attribute>
      <xsl:attribute name="border-top-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
    </xsl:when>
    <xsl:when test="$frame='topbot'">
      <xsl:attribute name="border-left-style">none</xsl:attribute>
      <xsl:attribute name="border-right-style">none</xsl:attribute>
      <xsl:attribute name="border-top-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-style">
        <xsl:value-of select="$table.frame.border.style"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-width">
        <xsl:value-of select="$table.frame.border.thickness"/>
      </xsl:attribute>
      <xsl:attribute name="border-top-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
      <xsl:attribute name="border-bottom-color">
        <xsl:value-of select="$table.frame.border.color"/>
      </xsl:attribute>
    </xsl:when>
    <xsl:when test="$frame='none'">
      <xsl:attribute name="border-left-style">none</xsl:attribute>
      <xsl:attribute name="border-right-style">none</xsl:attribute>
      <xsl:attribute name="border-top-style">none</xsl:attribute>
      <xsl:attribute name="border-bottom-style">none</xsl:attribute>
    </xsl:when>
    <xsl:otherwise>
      <xsl:attribute name="border-left-style">none</xsl:attribute>
      <xsl:attribute name="border-right-style">none</xsl:attribute>
      <xsl:attribute name="border-top-style">none</xsl:attribute>
      <xsl:attribute name="border-bottom-style">none</xsl:attribute>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="empty.table.cell"/>
<xsl:template name="empty.table.cell" dtm:id="empty.table.cell">
  <xsl:param name="colnum" select="0"/>

  <xsl:variable name="rowsep">
    <xsl:call-template name="inherited.table.attribute">
      <xsl:with-param name="entry" select="NOT-AN-ELEMENT-NAME"/>
      <xsl:with-param name="colnum" select="$colnum"/>
      <xsl:with-param name="attribute" select="'rowsep'"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="colsep">
    <xsl:call-template name="inherited.table.attribute">
      <xsl:with-param name="entry" select="NOT-AN-ELEMENT-NAME"/>
      <xsl:with-param name="colnum" select="$colnum"/>
      <xsl:with-param name="attribute" select="'colsep'"/>
    </xsl:call-template>
  </xsl:variable>

  <fo:table-cell text-align="center"
                 display-align="center"
                 xsl:use-attribute-sets="table.cell.padding">
    <xsl:if test="$rowsep &gt; 0">
      <xsl:call-template name="border">
        <xsl:with-param name="side" select="'bottom'"/>
      </xsl:call-template>
    </xsl:if>

    <xsl:if test="$colsep &gt; 0 and $colnum &lt; ancestor::tgroup/@cols">
      <xsl:call-template name="border">
        <xsl:with-param name="side" select="'right'"/>
      </xsl:call-template>
    </xsl:if>

    <!-- fo:table-cell should not be empty -->
    <fo:block><xsl:text> </xsl:text></fo:block>
  </fo:table-cell>
</xsl:template>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="border"/>
<xsl:template name="border" dtm:id="border">
  <xsl:param name="side" select="'left'"/>

  <xsl:attribute name="border-{$side}-width">
    <xsl:value-of select="$table.cell.border.thickness"/>
  </xsl:attribute>
  <xsl:attribute name="border-{$side}-style">
    <xsl:value-of select="$table.cell.border.style"/>
  </xsl:attribute>
  <xsl:attribute name="border-{$side}-color">
    <xsl:value-of select="$table.cell.border.color"/>
  </xsl:attribute>
</xsl:template>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="tgroup"/>
<xsl:template match="tgroup" name="tgroup" dtm:id="tgroup">
  
  <xsl:if test="$use-serna-extensions">
    <xse:cals-process-tgroup/>
  </xsl:if>
  
  <xsl:variable name="cols">
    <xsl:variable name="ncols" select='number(@cols)'/>
    <xsl:choose>
        <xsl:when test="$ncols = 'NaN' or (floor($ncols) - $ncols != 0)
            or $ncols &lt; 1 or $ncols &gt; 100">
            <!--xsl:message>Bad COLS attribute value</xsl:message -->
            <xsl:text>1</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$ncols"/>
        </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
          
  <xsl:if test="position() = 1">
    <!-- If this is the first tgroup, output the width attribute for the -->
    <!-- surrounding fo:table. (If this isn't the first tgroup, trying   -->
    <!-- to output the attribute will cause an error.)                   -->
    <xsl:attribute name="width">
      <xsl:choose>
        <xsl:when test="$default.table.width = ''">
          <xsl:text>100%</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$default.table.width"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:if>

  <xsl:call-template name="generate.colgroup">
    <xsl:with-param name="cols" select="$cols"/>
  </xsl:call-template>
  
  <xsl:apply-templates select="thead|tbody|tfoot"/>
</xsl:template>

<dtm:doc dtm:idref="thead"/>
<xsl:template match="thead" dtm:id="thead">
  <fo:table-header>
    <xsl:call-template name="row.holder"/>
  </fo:table-header>
</xsl:template>

<dtm:doc dtm:idref="tfoot"/>
<xsl:template match="tfoot" dtm:id="tfoot">
  <fo:table-footer>
    <xsl:call-template name="row.holder"/>
  </fo:table-footer>
</xsl:template>

<dtm:doc dtm:idref="tbody"/>
<xsl:template match="tbody" dtm:id="tbody">
  <fo:table-body  start-indent="0pt">
    <xsl:call-template name="row.holder"/>
  </fo:table-body>
</xsl:template>

<dtm:doc dtm:idref="row.holder"/>
<xsl:template name="row.holder" dtm:id="row.holder">
  <xsl:apply-templates select="row[1]" xse:sections="preserve-left">
    <xsl:with-param name="spans">
      <xsl:call-template name="blank.spans">
        <xsl:with-param name="cols" select="../@cols"/>
      </xsl:call-template>
    </xsl:with-param>
  </xsl:apply-templates>
</xsl:template>

<dtm:doc dtm:idref="row"/>
<xsl:template match="row" dtm:id="row">
  <xsl:param name="spans"/>

  <!-- Build current row with the incoming mnemonic row in "span" -->
  <fo:table-row>
    <xsl:apply-templates select="(entry|entrytbl)[1]">
      <xsl:with-param name="spans" select="$spans"/>
    </xsl:apply-templates>
  </fo:table-row>

  <xsl:if test="following-sibling::row">
    <!-- For the next row build mnemonics out of situation in the
     current row... -->
    <xsl:variable name="nextspans">
      <xsl:apply-templates select="(entry|entrytbl)[1]" mode="span">
        <xsl:with-param name="spans" select="$spans"/>
      </xsl:apply-templates>
    </xsl:variable>

    <!-- And provide this mnemonics to the next row -->
    <xsl:apply-templates select="following-sibling::row[1]" 
        xse:sections="preserve-left">
      <xsl:with-param name="spans" select="$nextspans"/>
    </xsl:apply-templates>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="entry"/>
<xsl:template match="entry|entrytbl" name="entry" dtm:id="entry">
  <xsl:param name="col" select="1"/>
  <xsl:param name="spans"/>

  <xsl:variable name="named.colnum">
    <xsl:call-template name="entry.colnum"/>
  </xsl:variable>

  <!-- Entry number will be the one explicitely stated in namest, or
       the current column number (col) if explicitely was not stated. -->
  
  <xsl:variable name="entry.colnum">
    <xsl:choose>
      <xsl:when test="$named.colnum &gt; 0">
        <xsl:value-of select="$named.colnum"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$col"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <!-- Width of cell's span -->
  <xsl:variable name="entry.colspan">
    <xsl:choose>
      <xsl:when test="@spanname or @namest">
        <xsl:call-template name="calculate.colspan"/>
      </xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <!-- Mnemonics for the rest of the cells in the row -->
  <xsl:variable name="following.spans">
    <xsl:call-template name="calculate.following.spans">
      <xsl:with-param name="colspan" select="$entry.colspan"/>
      <xsl:with-param name="spans" select="$spans"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:choose>

    <!-- If in the span mnemonics my cell is not 0 that means here is
     vertical span from row above. Increase col number and try
     rerendering this cell -->
    <xsl:when test="$spans != '' and not(starts-with($spans,'0:'))">
      <xsl:call-template name="entry">
        <xsl:with-param name="col" select="$col+1"/>
        <xsl:with-param name="spans" select="substring-after($spans,':')"/>
      </xsl:call-template>
    </xsl:when>

    <!-- If the entry number is greater then current col number, then
     generate an empty cell and try to generate this cell in new position. -->
    <xsl:when test="$entry.colnum &gt; $col">
      <xsl:call-template name="empty.table.cell">
        <xsl:with-param name="colnum" select="$col"/>
      </xsl:call-template>
      <xsl:call-template name="entry">
        <xsl:with-param name="col" select="$col+1"/>
        <xsl:with-param name="spans" select="substring-after($spans,':')"/>
      </xsl:call-template>
    </xsl:when>

    <!-- Otherwise go generating a cell -->
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$use-serna-extensions">
          <xsl:call-template name="make-cell">
            <xsl:with-param 
              name="rowsep"
              select="xse:cals-inherited-attribute(., $entry.colnum, 'rowsep', '1')"/>
            <xsl:with-param 
              name="colsep" 
              select="xse:cals-inherited-attribute(., $entry.colnum, 'colsep', '1')"/>
            <xsl:with-param 
              name="valign"
              select="xse:cals-inherited-attribute(., $entry.colnum, 'valign', '')"/>
            <xsl:with-param 
              name="align"
              select="xse:cals-inherited-attribute(., $entry.colnum, 'align', '')"/>
            <xsl:with-param 
              name="char" 
              select="xse:cals-inherited-attribute(., $entry.colnum, 'char', '')"/>
            <xsl:with-param name="col" select="$col"/>
            <xsl:with-param name="entry.colspan" select="$entry.colspan"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="make-cell">
            <xsl:with-param name="rowsep">
              <xsl:call-template name="inherited.table.attribute">
                <xsl:with-param name="entry" select="."/>
                <xsl:with-param name="colnum" select="$entry.colnum"/>
                <xsl:with-param name="attribute" select="'rowsep'"/>
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="colsep">
              <xsl:call-template name="inherited.table.attribute">
                <xsl:with-param name="entry" select="."/>
                <xsl:with-param name="colnum" select="$entry.colnum"/>
                <xsl:with-param name="attribute" select="'colsep'"/>
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="valign">
              <xsl:call-template name="inherited.table.attribute">
                <xsl:with-param name="entry" select="."/>
                <xsl:with-param name="colnum" select="$entry.colnum"/>
                <xsl:with-param name="attribute" select="'valign'"/>
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="align">
              <xsl:call-template name="inherited.table.attribute">
                <xsl:with-param name="entry" select="."/>
                <xsl:with-param name="colnum" select="$entry.colnum"/>
                <xsl:with-param name="attribute" select="'align'"/>
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="char">
              <xsl:call-template name="inherited.table.attribute">
                <xsl:with-param name="entry" select="."/>
                <xsl:with-param name="colnum" select="$entry.colnum"/>
                <xsl:with-param name="attribute" select="'char'"/>
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="col" select="$col"/>
            <xsl:with-param name="entry.colspan" select="$entry.colspan"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:choose>
        <!-- Go generating next entries if there are any. -->
        <xsl:when test="following-sibling::entry|following-sibling::entrytbl">
          <xsl:apply-templates select="(following-sibling::entry
                                       |following-sibling::entrytbl)[1]">
            <xsl:with-param name="col" select="$col+$entry.colspan"/>
            <xsl:with-param name="spans" select="$following.spans"/>
          </xsl:apply-templates>
        </xsl:when>
        <!-- Or generate empty cells if span is not exhausted. -->
        <xsl:otherwise>
          <xsl:call-template name="finaltd">
            <xsl:with-param name="spans" select="$following.spans"/>
            <xsl:with-param name="col" select="$col+$entry.colspan"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="make-cell"/>
<xsl:template name="make-cell" dtm:id="make-cell">
  <xsl:param name="rowsep"/>
  <xsl:param name="colsep"/>
  <xsl:param name="valign"/>
  <xsl:param name="align"/>
  <xsl:param name="char"/>
  <xsl:param name="col"/>
  <xsl:param name="entry.colspan"/>

      <fo:table-cell xsl:use-attribute-sets="table.cell.padding">
        <xsl:if test="$rowsep &gt; 0">
          <xsl:call-template name="border">
            <xsl:with-param name="side" select="'bottom'"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:if test="$colsep &gt; 0 and $col &lt; ancestor::tgroup/@cols">
          <xsl:call-template name="border">
            <xsl:with-param name="side" select="'right'"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:if test="@morerows">
          <xsl:attribute name="number-rows-spanned">
            <xsl:value-of select="@morerows+1"/>
          </xsl:attribute>
        </xsl:if>

        <xsl:if test="$entry.colspan &gt; 1">
          <xsl:attribute name="number-columns-spanned">
            <xsl:value-of select="$entry.colspan"/>
          </xsl:attribute>
        </xsl:if>

        <xsl:if test="$valign != ''">
          <xsl:attribute name="display-align">
            <xsl:choose>
              <xsl:when test="$valign='top'">before</xsl:when>
              <xsl:when test="$valign='middle'">center</xsl:when>
              <xsl:when test="$valign='bottom'">after</xsl:when>
              <xsl:otherwise>
                <xsl:text>center</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </xsl:if>

        <xsl:if test="$align != ''">
          <xsl:attribute name="text-align">
            <xsl:value-of select="$align"/>
          </xsl:attribute>
        </xsl:if>

        <xsl:if test="$char != ''">
          <xsl:attribute name="text-align">
            <xsl:value-of select="$char"/>
          </xsl:attribute>
        </xsl:if>

        <fo:block>
          <!-- highlight this entry? -->
          <xsl:if test="ancestor::thead">
            <xsl:attribute name="font-weight">bold</xsl:attribute>
          </xsl:if>

          <!-- are we missing any indexterms? -->
          <xsl:if test="not(preceding-sibling::entry)
                        and not(parent::row/preceding-sibling::row)">
            <!-- this is the first entry of the first row -->
            <xsl:if test="ancestor::thead or
                          (ancestor::tbody
                           and not(ancestor::tbody/preceding-sibling::thead
                                   or ancestor::tbody/preceding-sibling::tbody))">
              <!-- of the thead or the first tbody -->
              <xsl:apply-templates select="ancestor::tgroup/preceding-sibling::indexterm"/>
            </xsl:if>
          </xsl:if>

          <xsl:choose>
            <!-- Generate whitespace if no children -->
            <xsl:when test="not(node())">
              <xsl:text>&#160;</xsl:text>
            </xsl:when>

            <!-- Generate table if it is entrytbl -->
            <xsl:when test="self::entrytbl">
              <fo:table border-collapse="collapse">
                <xsl:if test="(colspec|thead/colspec|tbody/colspec)[contains(@colwidth, '*')]">
                  <xsl:attribute name="table-layout">fixed</xsl:attribute>
                </xsl:if>
                <xsl:call-template name="tgroup"/>
              </fo:table>
            </xsl:when>

            <!-- Otherwise build the content -->
            <xsl:otherwise>
              <xsl:apply-templates/>
            </xsl:otherwise>
          </xsl:choose>
        </fo:block>
      </fo:table-cell>
</xsl:template>


<!-- This template builds mnemonic row that designates spans valuable
     for the next row -->
<dtm:doc dtm:idref="sentry"/>
<xsl:template match="entry|entrytbl" name="sentry" mode="span" dtm:id="sentry">
  <xsl:param name="col" select="1"/>
  <xsl:param name="spans"/>


  <!-- Column number of the entry if explicitely stated in the entry -->
  <xsl:variable name="entry.colnum">
    <xsl:call-template name="entry.colnum"/>
  </xsl:variable>

  <!-- The width of the span of the entry -->
  <xsl:variable name="entry.colspan">
    <xsl:choose>
      <xsl:when test="@spanname or @namest">
        <xsl:call-template name="calculate.colspan"/>
      </xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <!-- The rest of width of table (span) left in terms of "0:" -->
  <xsl:variable name="following.spans">
    <xsl:call-template name="calculate.following.spans">
      <xsl:with-param name="colspan" select="$entry.colspan"/>
      <xsl:with-param name="spans" select="$spans"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:choose>
    <!-- If spans is not exhausted and the first mnemonics has vertical span, 
         then decrease this span for 1. -->
    <xsl:when test="$spans != '' and not(starts-with($spans,'0:'))">
      <xsl:value-of select="substring-before($spans,':')-1"/>
      <xsl:text>:</xsl:text>
      <xsl:call-template name="sentry">
        <xsl:with-param name="col" select="$col+1"/>
        <xsl:with-param name="spans" select="substring-after($spans,':')"/>
      </xsl:call-template>
    </xsl:when>

    <!-- If entry was explicitely shifted further then current col,
         generate 0:, generate next mnemonic for col increased on 
         entry.colspan with span of the following spans. -->
    <xsl:when test="$entry.colnum &gt; $col">
      <xsl:text>0:</xsl:text>
      <xsl:call-template name="sentry">
        <xsl:with-param name="col" select="$col+$entry.colspan"/>
        <xsl:with-param name="spans" select="$following.spans"/>
      </xsl:call-template>
    </xsl:when>

    <xsl:otherwise>
      <xsl:call-template name="copy-string">
        <xsl:with-param name="count" select="$entry.colspan"/>
        <xsl:with-param name="string">
          <xsl:choose>
            <!-- Create a mnemonic for vertical span row -->
            <xsl:when test="@morerows">
              <xsl:value-of select="@morerows"/>
            </xsl:when>
            <!-- Create a mnemonic for no vertical span row -->
            <xsl:otherwise>0</xsl:otherwise>
          </xsl:choose>
          <xsl:text>:</xsl:text>
        </xsl:with-param>
      </xsl:call-template>

      <xsl:choose>
        <!-- Create a mnemonic for the next cell if it exist. 
             Its column number will be current column number + 
             current span length -->
        <xsl:when test="following-sibling::entry|following-sibling::entrytbl">
          <xsl:apply-templates select="(following-sibling::entry
                                       |following-sibling::entrytbl)[1]"
                               mode="span">
            <xsl:with-param name="col" select="$col+$entry.colspan"/>
            <xsl:with-param name="spans" select="$following.spans"/>
          </xsl:apply-templates>
        </xsl:when>
        <!-- If there is no next cell, but following spans left, then
             the rest of mnemonics will be 1 morerow shorter. -->
        <xsl:otherwise>
          <xsl:call-template name="sfinaltd">
            <xsl:with-param name="spans" select="$following.spans"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="generate.colgroup.raw"/>
<xsl:template name="generate.colgroup.raw" dtm:id="generate.colgroup.raw">
  <xsl:param name="cols" select="1"/>
  <xsl:param name="count" select="1"/>

  <xsl:choose>
    <xsl:when test="$count>$cols"></xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="generate.col.raw">
        <xsl:with-param name="countcol" select="$count"/>
      </xsl:call-template>
      <xsl:call-template name="generate.colgroup.raw">
        <xsl:with-param name="cols" select="$cols"/>
        <xsl:with-param name="count" select="$count+1"/>
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="generate.colgroup"/>
<xsl:template name="generate.colgroup" dtm:id="generate.colgroup">
  <xsl:param name="cols" select="1"/>
  <xsl:param name="count" select="1"/>

  <xsl:choose>
    <xsl:when test="$count>$cols"></xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="generate.col">
        <xsl:with-param name="countcol" select="$count"/>
        <xsl:with-param name="colspecs" select="colspec"/>
      </xsl:call-template>
      <xsl:call-template name="generate.colgroup">
        <xsl:with-param name="cols" select="$cols"/>
        <xsl:with-param name="count" select="$count+1"/>
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="generate.col.raw"/>
<xsl:template name="generate.col.raw" dtm:id="generate.col.raw">
  <!-- generate the table-column for column countcol -->
  <xsl:param name="countcol">1</xsl:param>
  <xsl:param name="colspecs" select="./colspec"/>
  <xsl:param name="count">1</xsl:param>
  <xsl:param name="colnum">1</xsl:param>

  <xsl:choose>
    <xsl:when test="$count>count($colspecs)">
      <fo:table-column column-number="{$countcol}"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="colspec" select="$colspecs[$count=position()]"/>

      <xsl:variable name="colspec.colnum">
        <xsl:choose>
          <xsl:when test="$colspec/@colnum">
            <xsl:value-of select="$colspec/@colnum"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$colnum"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <xsl:variable name="colspec.colwidth">
        <xsl:choose>
          <xsl:when test="$colspec/@colwidth">
            <xsl:value-of select="$colspec/@colwidth"/>
          </xsl:when>
          <xsl:otherwise>1*</xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <xsl:choose>
        <xsl:when test="$colspec.colnum=$countcol">
          <fo:table-column column-number="{$countcol}">
            <xsl:attribute name="column-width">
              <xsl:value-of select="$colspec.colwidth"/>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="generate.col.raw">
            <xsl:with-param name="countcol" select="$countcol"/>
            <xsl:with-param name="colspecs" select="$colspecs"/>
            <xsl:with-param name="count" select="$count+1"/>
            <xsl:with-param name="colnum">
              <xsl:choose>
                <xsl:when test="$colspec/@colnum">
                  <xsl:value-of select="$colspec/@colnum + 1"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="$colnum + 1"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:with-param>
           </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="generate.col"/>
<xsl:template name="generate.col" dtm:id="generate.col">
  <!-- generate the table-column for column countcol -->
  <xsl:param name="countcol">1</xsl:param>
  <xsl:param name="colspecs"/>
  <xsl:param name="count">1</xsl:param>
  <xsl:param name="colnum">1</xsl:param>

  <xsl:choose>
    <xsl:when test="$count>count($colspecs)">
      <fo:table-column column-number="{$countcol}">
        <xsl:variable name="colwidth">
          <xsl:call-template name="calc.column.width"/>
        </xsl:variable>
        <xsl:if test="$colwidth != 'proportional-column-width(1)'">
          <xsl:attribute name="column-width">
            <xsl:value-of select="$colwidth"/>
          </xsl:attribute>
        </xsl:if>
      </fo:table-column>
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="colspec" select="$colspecs[$count=position()]"/>

      <xsl:variable name="colspec.colnum">
        <xsl:choose>
          <xsl:when test="$colspec/@colnum">
            <xsl:value-of select="$colspec/@colnum"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$colnum"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <xsl:variable name="colspec.colwidth">
        <xsl:choose>
          <xsl:when test="$colspec/@colwidth">
            <xsl:value-of select="$colspec/@colwidth"/>
          </xsl:when>
          <xsl:otherwise>1*</xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <xsl:choose>
        <xsl:when test="$colspec.colnum=$countcol">
          <fo:table-column column-number="{$countcol}">
            <xsl:variable name="colwidth">
              <xsl:call-template name="calc.column.width">
                <xsl:with-param name="colwidth">
                  <xsl:value-of select="$colspec.colwidth"/>
                </xsl:with-param>
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$colwidth != 'proportional-column-width(1)'">
              <xsl:attribute name="column-width">
                <xsl:value-of select="$colwidth"/>
              </xsl:attribute>
            </xsl:if>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="generate.col">
            <xsl:with-param name="countcol" select="$countcol"/>
            <xsl:with-param name="colspecs" select="$colspecs"/>
            <xsl:with-param name="count" select="$count+1"/>
            <xsl:with-param name="colnum">
              <xsl:choose>
                <xsl:when test="$colspec/@colnum">
                  <xsl:value-of select="$colspec/@colnum + 1"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="$colnum + 1"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:with-param>
           </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- doc:template name="calc.column.width" xmlns="">
<refpurpose>Calculate an XSL FO table column width specification from a
CALS table column width specification.</refpurpose>

<refdescription>
<para>CALS expresses table column widths in the following basic
forms:</para>

<itemizedlist>
<listitem>
<para><emphasis>99.99units</emphasis>, a fixed length specifier.</para>
</listitem>
<listitem>
<para><emphasis>99.99</emphasis>, a fixed length specifier without any units.</para>
</listitem>
<listitem>
<para><emphasis>99.99*</emphasis>, a relative length specifier.</para>
</listitem>
<listitem>
<para><emphasis>99.99*+99.99units</emphasis>, a combination of both.</para>
</listitem>
</itemizedlist>

<para>The CALS units are points (pt), picas (pi), centimeters (cm),
millimeters (mm), and inches (in). These are the same units as XSL,
except that XSL abbreviates picas "pc" instead of "pi". If a length
specifier has no units, the CALS default unit (pt) is assumed.</para>

<para>Relative length specifiers are represented in XSL with the
proportional-column-width() function.</para>

<para>Here are some examples:</para>

<itemizedlist>
<listitem>
<para>"36pt" becomes "36pt"</para>
</listitem>
<listitem>
<para>"3pi" becomes "3pc"</para>
</listitem>
<listitem>
<para>"36" becomes "36pt"</para>
</listitem>
<listitem>
<para>"3*" becomes "proportional-column-width(3)"</para>
</listitem>
<listitem>
<para>"3*+2pi" becomes "proportional-column-width(3)+2pc"</para>
</listitem>
<listitem>
<para>"1*+2" becomes "proportional-column-width(1)+2pt"</para>
</listitem>
</itemizedlist>
</refdescription>

<refparameter>
<variablelist>
<varlistentry><term>colwidth</term>
<listitem>
<para>The CALS column width specification.</para>
</listitem>
</varlistentry>
</variablelist>
</refparameter>

<refreturn>
<para>The XSL column width specification.</para>
</refreturn>
</doc:template -->

<dtm:doc dtm:idref="calc.column.width"/>
<xsl:template name="calc.column.width" dtm:id="calc.column.width">
  <xsl:param name="colwidth">1*</xsl:param>

  <!-- Ok, the colwidth could have any one of the following forms: -->
  <!--        1*       = proportional width -->
  <!--     1unit       = 1.0 units wide -->
  <!--         1       = 1pt wide -->
  <!--  1*+1unit       = proportional width + some fixed width -->
  <!--      1*+1       = proportional width + some fixed width -->

  <!-- If it has a proportional width, translate it to XSL -->
  <xsl:if test="contains($colwidth, '*')">
    <xsl:text>proportional-column-width(</xsl:text>
    <xsl:choose> 
      <xsl:when test="'*' = $colwidth">1</xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="substring-before($colwidth, '*')"/>
      </xsl:otherwise>
     </xsl:choose> 
    <xsl:text>)</xsl:text>
  </xsl:if>

  <!-- Now grab the non-proportional part of the specification -->
  <xsl:variable name="width-units">
    <xsl:choose>
      <xsl:when test="contains($colwidth, '*')">
        <xsl:value-of
             select="normalize-space(substring-after($colwidth, '*'))"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="normalize-space($colwidth)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <!-- Ok, now the width-units could have any one of the following forms: -->
  <!--                 = <empty string> -->
  <!--     1unit       = 1.0 units wide -->
  <!--         1       = 1pt wide -->
  <!-- with an optional leading sign -->

  <!-- Grab the width part by blanking out the units part and discarding -->
  <!-- whitespace. It's not pretty, but it works. -->
  <xsl:variable name="width"
       select="normalize-space(translate($width-units,
                                         '+-0123456789.abcdefghijklmnopqrstuvwxyz',
                                         '+-0123456789.'))"/>

  <!-- Grab the units part by blanking out the width part and discarding -->
  <!-- whitespace. It's not pretty, but it works. -->
  <xsl:variable name="units"
       select="normalize-space(translate($width-units,
                                         'abcdefghijklmnopqrstuvwxyz+-0123456789.',
                                         'abcdefghijklmnopqrstuvwxyz'))"/>

  <!-- Output the width -->
  <xsl:value-of select="$width"/>

  <!-- Output the units, translated appropriately -->
  <xsl:choose>
    <xsl:when test="$units = 'pi'">pc</xsl:when>
    <xsl:when test="$units = '' and $width != ''">pt</xsl:when>
    <xsl:otherwise><xsl:value-of select="$units"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>
