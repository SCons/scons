<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="xse dtm"
                version='1.0'>

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

      <xsl:apply-templates/>

      <xsl:if test="$placement != 'before' and not(self::informaltable)">
        <xsl:call-template name="formal.object.heading">
          <xsl:with-param name="placement" select="$placement"/>
        </xsl:call-template>
      </xsl:if>
    </fo:block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="tgroups"/>
<xsl:template match="table/tgroup|informaltable/tgroup" dtm:id="tgroups">
  <xsl:if test="$show.preamble.editing">
    <fo:block xsl:use-attribute-sets="preamble.attributes">
      <fo:block background-color="transparent"
        xsl:use-attribute-sets="title.content.properties 
                                formal.title.properties">
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
      <xsl:apply-templates select="colspec|spanspec" mode="cals-table-specs"/>
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
    <xse:cals-table-group>
        <xsl:call-template name="tgroup"/>
    </xse:cals-table-group>
  </fo:table>
</xsl:template>

<dtm:doc dtm:idref="specs.cals-table-specs"/>
<xsl:template match="colspec|spanspec" mode="cals-table-specs" dtm:id="specs.cals-table-specs">
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

<dtm:doc dtm:idref="cals-table-empty-cell"/>
<xsl:template name="cals-table-empty-cell" dtm:id="cals-table-empty-cell">
  <xsl:variable name="rowsep" select="xse:cals-attribute('rowsep', '1')"/>
  <xsl:variable name="colsep" select="xse:cals-attribute('colsep', '1')"/>
  <xsl:variable name="colnum" select="xse:cals-attribute('cals:colnum')"/>
  
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
    <fo:block>
        <xsl:text> </xsl:text>
    </fo:block>
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
<xsl:template name="tgroup" dtm:id="tgroup">
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
  
  <xsl:apply-templates select="thead|tbody|
    processing-instruction('se:choice')" mode="cals-table-head"/>
  <xsl:apply-templates select="tfoot|
    processing-instruction('se:choice')" mode="cals-table-head"/>
</xsl:template>

<dtm:doc dtm:idref="thead.cals-table-head"/>
<xsl:template match="thead" mode="cals-table-head">
  <fo:table-header>
    <xsl:apply-templates select="row|processing-instruction('se:choice')"
        mode="cals-table-row"/>
  </fo:table-header>
</xsl:template>

<dtm:doc dtm:idref="tfoot.cals-table-head"/>
<xsl:template match="tfoot" mode="cals-table-head" dtm:id="tfoot.cals-table-head">
  <fo:table-footer>
    <xsl:apply-templates select="row|processing-instruction('se:choice')"
        mode="cals-table-row"/>
  </fo:table-footer>
</xsl:template>

<dtm:doc dtm:idref="tbody.cals-table-head"/>
<xsl:template match="tbody" mode="cals-table-head" dtm:id="tbody.cals-table-head">
  <fo:table-body  start-indent="0pt">
    <xsl:apply-templates select="row|processing-instruction('se:choice')"
        mode="cals-table-row"/>
  </fo:table-body>
</xsl:template>

<dtm:doc dtm:idref="row.cals-table-row"/>
<xsl:template match="row" mode="cals-table-row" dtm:id="row.cals-table-head">
  <!-- Build current row with the incoming mnemonic row in "span" -->
  <fo:table-row>
    <xse:cals-table-row>
        <xsl:apply-templates select="entry|entrytbl|
            processing-instruction('se:choice')" mode="cals-table-entry"/>
    </xse:cals-table-row> 
  </fo:table-row>
</xsl:template>

<dtm:doc dtm:idref="entry.cals-table-entry"/>
<xsl:template match="entry|entrytbl" mode="cals-table-entry" dtm:id="entry.cals-table-entry">
  
  <xse:cals-table-cell>
    <xsl:variable name="rowsep" select="xse:cals-attribute('rowsep', '1')"/>
    <xsl:variable name="colsep" select="xse:cals-attribute('colsep', '1')"/>
    <xsl:variable name="valign" select="xse:cals-attribute('valign', '')"/>
    <xsl:variable name="align"  select="xse:cals-attribute('align', '')"/>
    <xsl:variable name="char"   select="xse:cals-attribute('char', '')"/>
    <xsl:variable name="colspan" select="xse:cals-attribute('cals:colspan')"/>
  
    <fo:table-cell xsl:use-attribute-sets="table.cell.padding">
      <xsl:if test="$rowsep &gt; 0">
        <xsl:call-template name="border">
          <xsl:with-param name="side" select="'bottom'"/>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="$colsep &gt; 0 and
              xse:cals-attribute('cals:colnum') &lt; ancestor::tgroup/@cols">
        <xsl:call-template name="border">
          <xsl:with-param name="side" select="'right'"/>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="$colspan &gt; 1">
        <xsl:attribute name="number-columns-spanned">
            <xsl:value-of select="$colspan"/>
        </xsl:attribute>
      </xsl:if>
    
      <xsl:if test="@morerows">
        <xsl:attribute name="number-rows-spanned">
          <xsl:value-of select="@morerows+1"/>
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
              <xse:cals-table-group>
                <xsl:call-template name="tgroup"/>
              </xse:cals-table-group>
            </fo:table>
          </xsl:when>

          <!-- Otherwise build the content -->
          <xsl:otherwise>
            <xsl:apply-templates/>
          </xsl:otherwise>
        </xsl:choose>
      </fo:block>
    </fo:table-cell>
  </xse:cals-table-cell>
</xsl:template>

<xsl:template name="generate.colgroup">
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

<dtm:doc dtm:idref="calc.column.width"/>
<xsl:template name="calc.column.width" dtm:id="calc.column.width">
  <xsl:param name="colwidth">1*</xsl:param>

  <xsl:if test="contains($colwidth, '*')">
    <xsl:text>proportional-column-width(</xsl:text>
    <xsl:value-of select="substring-before($colwidth, '*')"/>
    <xsl:text>)</xsl:text>
  </xsl:if>

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

  <xsl:variable name="width"
       select="normalize-space(translate($width-units,
                                         '+-0123456789.abcdefghijklmnopqrstuvwxyz',
                                         '+-0123456789.'))"/>

  <xsl:variable name="units"
       select="normalize-space(translate($width-units,
                                         'abcdefghijklmnopqrstuvwxyz+-0123456789.',
                                         'abcdefghijklmnopqrstuvwxyz'))"/>

  <xsl:value-of select="$width"/>

  <xsl:choose>
    <xsl:when test="$units = 'pi'">pc</xsl:when>
    <xsl:when test="$units = '' and $width != ''">pt</xsl:when>
    <xsl:otherwise><xsl:value-of select="$units"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>
