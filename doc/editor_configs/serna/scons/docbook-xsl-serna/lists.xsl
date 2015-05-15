<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="xse dtm"
                version='1.0'>

  <!-- TODO: move to params -->
  <xsl:variable name="label-width">1.5em</xsl:variable>
  <xsl:variable name="presentation"></xsl:variable>
  <xsl:variable name="term-width">10em</xsl:variable>

  <!-- TODO: Move to common -->
<dtm:doc dtm:idref="next.itemsymbol"/>
<xsl:template name="next.itemsymbol" dtm:id="next.itemsymbol">
  <xsl:param name="itemsymbol" select="'default'"/>
  <xsl:choose>
    <!-- Change this list if you want to change the order of symbols -->
    <xsl:when test="$itemsymbol = 'disc'">circle</xsl:when>
    <xsl:when test="$itemsymbol = 'round'">square</xsl:when>
    <xsl:otherwise>disc</xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="list.itemsymbol"/>
<xsl:template name="list.itemsymbol" dtm:id="list.itemsymbol">
  <xsl:param name="node" select="."/>

  <xsl:choose>
    <xsl:when test="$node/@mark">
      <xsl:value-of select="$node/@mark"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$node/ancestor::itemizedlist">
          <xsl:call-template name="next.itemsymbol">
            <xsl:with-param name="itemsymbol">
              <xsl:call-template name="list.itemsymbol">
                <xsl:with-param name="node" select="$node/ancestor::itemizedlist[1]"/>
              </xsl:call-template>
            </xsl:with-param>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="next.itemsymbol"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="next.numeration"/>
<xsl:template name="next.numeration" dtm:id="next.numeration">
  <xsl:param name="numeration" select="'default'"/>
  <xsl:choose>
    <!-- Change this list if you want to change the order of numerations -->
    <xsl:when test="$numeration = 'arabic'">loweralpha</xsl:when>
    <xsl:when test="$numeration = 'loweralpha'">lowerroman</xsl:when>
    <xsl:when test="$numeration = 'lowerroman'">upperalpha</xsl:when>
    <xsl:when test="$numeration = 'upperalpha'">upperroman</xsl:when>
    <xsl:when test="$numeration = 'upperroman'">arabic</xsl:when>
    <xsl:otherwise>arabic</xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="list.numeration"/>
<xsl:template name="list.numeration" dtm:id="list.numeration">
  <xsl:param name="node" select="."/>

  <xsl:choose>
    <xsl:when test="$node/@numeration">
      <xsl:value-of select="$node/@numeration"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$node/ancestor::orderedlist">
          <xsl:call-template name="next.numeration">
            <xsl:with-param name="numeration">
              <xsl:call-template name="list.numeration">
                <xsl:with-param name="node" select="$node/ancestor::orderedlist[1]"/>
              </xsl:call-template>
            </xsl:with-param>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="next.numeration"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="itemizedlist"/>
<xsl:template match="itemizedlist" dtm:id="itemizedlist">
 <fo:block  xsl:use-attribute-sets="list.block.spacing">
    <xsl:apply-templates 
      select="title[not(self::processing-instruction('se:choice'))]" 
      mode="plain.formal.title.mode"/>
  
  <xsl:variable name="itemsymbol">
    <xsl:call-template name="list.itemsymbol">
      <xsl:with-param name="node" select="."/>
    </xsl:call-template>
  </xsl:variable>
  
  <xsl:variable name="itemchar">
    <xsl:choose>
      <xsl:when test="$itemsymbol='disc'">&#x2022;</xsl:when>
      <xsl:when test="$itemsymbol='bullet'">&#x2022;</xsl:when>
      <!-- why do these symbols not work? -->
      <!--
      <xsl:when test="$itemsymbol='circle'">&#x2218;</xsl:when>
      <xsl:when test="$itemsymbol='round'">&#x2218;</xsl:when>
      <xsl:when test="$itemsymbol='square'">&#x2610;</xsl:when>
      <xsl:when test="$itemsymbol='box'">&#x2610;</xsl:when>
      -->
      <xsl:otherwise>&#x2022;</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:apply-templates select="*[not(self::listitem or self::title)]"/>

  <fo:list-block provisional-label-separation="0.2em"
                 provisional-distance-between-starts="{$label-width}">
    <xsl:apply-templates select="listitem">
        <xsl:with-param name="itemsymbol" select="$itemchar"/>
    </xsl:apply-templates>
  </fo:list-block>
 </fo:block>
</xsl:template>

<dtm:doc dtm:idref="title.lists"/>
<xsl:template match="itemizedlist/title|orderedlist/title" dtm:id="title.lists"/>

<dtm:doc dtm:idref="listitem.itemizedlist"/>
<xsl:template match="itemizedlist/listitem" dtm:id="listitem.itemizedlist">
  <xsl:param name="itemsymbol"/>
  
  <xsl:choose>
    <xsl:when test="parent::*/@spacing = 'compact'">
      <fo:list-item xsl:use-attribute-sets="compact.list.item.spacing">
        <xsl:call-template name="itemizedlist.item.contents">
            <xsl:with-param name="itemsymbol" select="$itemsymbol"/>
        </xsl:call-template>
      </fo:list-item>
    </xsl:when>
    <xsl:otherwise>
      <fo:list-item xsl:use-attribute-sets="list.item.spacing">
        <xsl:call-template name="itemizedlist.item.contents">
            <xsl:with-param name="itemsymbol" select="$itemsymbol"/>
        </xsl:call-template>
      </fo:list-item>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="itemizedlist.item.contents"/>
<xsl:template name="itemizedlist.item.contents" dtm:id="itemizedlist.item.contents">
    <xsl:param name="itemsymbol"/>
    <fo:list-item-label end-indent="label-end()">
      <fo:block>
        <xsl:value-of select="$itemsymbol"/>  
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <fo:block>
        <xsl:apply-templates/>
      </fo:block>
    </fo:list-item-body>
</xsl:template>

<dtm:doc dtm:idref="orderedlist"/>
<xsl:template match="orderedlist" dtm:id="orderedlist">
  <fo:block>
    <xsl:apply-templates 
      select="title[not(self::processing-instruction('se:choice'))]" 
      mode="plain.formal.title.mode"/>
  
  <xsl:variable name="starting.number">
    <xsl:call-template name="orderedlist-starting-number"/>
  </xsl:variable>

  <xsl:apply-templates select="*[not(self::listitem or self::title)]"/>

  <xsl:variable name="numeration">
    <xsl:call-template name="list.numeration">
      <xsl:with-param name="node" select="."/>
    </xsl:call-template>
  </xsl:variable>

  <fo:list-block xsl:use-attribute-sets="list.block.spacing"
                 provisional-label-separation="0.2em"
                 provisional-distance-between-starts="{$label-width}">
    <xsl:if test="$numeration='upperroman'">
        <xsl:attribute name="provisional-distance-between-starts">
            <xsl:value-of select="concat($label-width, '+1em')"/>
        </xsl:attribute>
    </xsl:if>
    <xsl:apply-templates select="listitem">
        <xsl:with-param name="starting.number" select="$starting.number"/>
        <xsl:with-param name="numeration" select="$numeration"/>
    </xsl:apply-templates>
  </fo:list-block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="listitem.orderedlist.item-number"/>
<xsl:template match="orderedlist/listitem" mode="item-number" dtm:id="listitem.orderedlist.item-number">
  <xsl:param name="starting.number"/> 
  <xsl:param name="numeration"/>
  
  <xsl:variable name="item-number">
    <xsl:choose>
        <xsl:when test="$use-serna-extensions">
            <xsl:value-of 
                select="xse:docbook-orderedlist-itemnumber($starting.number)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="orderedlist-item-number">
            <xsl:with-param name="starting.number" select="$starting.number"/>
          </xsl:call-template>
        </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  
  <xsl:if test="parent::orderedlist/@inheritnum='inherit'
                and ancestor::listitem[parent::orderedlist]">
    <xsl:apply-templates select="ancestor::listitem[parent::orderedlist][1]"
                         mode="item-number">
        <xsl:with-param name="starting.number" select="$starting.number"/>
        <xsl:with-param name="numeration" select="$numeration"/>
    </xsl:apply-templates>
  </xsl:if>

  <xsl:choose>
    <xsl:when test="$numeration='arabic'">
      <xsl:number value="$item-number" format="1."/>
    </xsl:when>
    <xsl:when test="$numeration='loweralpha'">
      <xsl:number value="$item-number" format="a."/>
    </xsl:when>
    <xsl:when test="$numeration='lowerroman'">
      <xsl:number value="$item-number" format="i."/>
    </xsl:when>
    <xsl:when test="$numeration='upperalpha'">
      <xsl:number value="$item-number" format="A."/>
    </xsl:when>
    <xsl:when test="$numeration='upperroman'">
      <xsl:number value="$item-number" format="I."/>
    </xsl:when>
    <!-- What!? This should never happen -->
    <xsl:otherwise>
      <xsl:text>Unexpected: </xsl:text>
      <xsl:value-of select="$numeration"/>
      <xsl:value-of select="1."/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="listitem.orderedlist"/>
<xsl:template match="orderedlist/listitem" dtm:id="listitem.orderedlist">
  <xsl:param name="starting.number"/>
  <xsl:param name="numeration"/>
 
  <xsl:choose>
    <xsl:when test="parent::*/@spacing = 'compact'">
      <fo:list-item xsl:use-attribute-sets="compact.list.item.spacing">
        <fo:list-item-label end-indent="label-end()">
          <fo:block>
            <xsl:apply-templates select="." mode="item-number">
                <xsl:with-param name="starting.number" 
                                select="$starting.number"/> 
                <xsl:with-param name="numeration" select="$numeration"/>
            </xsl:apply-templates>
          </fo:block>
        </fo:list-item-label>
        <fo:list-item-body start-indent="body-start()">
          <xsl:apply-templates/>
        </fo:list-item-body>
      </fo:list-item>
    </xsl:when>
    <xsl:otherwise>
      <fo:list-item xsl:use-attribute-sets="list.item.spacing">
        <fo:list-item-label end-indent="label-end()">
          <fo:block>
            <xsl:apply-templates select="." mode="item-number">
                <xsl:with-param name="starting.number" 
                                select="$starting.number"/> 
                <xsl:with-param name="numeration" select="$numeration"/>
            </xsl:apply-templates>
          </fo:block>
        </fo:list-item-label>
        <fo:list-item-body start-indent="body-start()">
            <xsl:apply-templates/>
        </fo:list-item-body>
      </fo:list-item>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="orderedlist-starting-number"/>
<xsl:template name="orderedlist-starting-number" dtm:id="orderedlist-starting-number">
  <xsl:param name="list" select="."/>
  <xsl:choose>
    <xsl:when test="not($list/@continuation = 'continues')">1</xsl:when>
    <xsl:otherwise>
      <xsl:variable name="prevlist"
                    select="$list/preceding::orderedlist[1]"/>
      <xsl:choose>
        <xsl:when test="count($prevlist) = 0">2</xsl:when>
        <xsl:otherwise>
          <xsl:variable name="prevlength" select="count($prevlist/listitem)"/>
          <xsl:variable name="prevstart">
            <xsl:call-template name="orderedlist-starting-number">
              <xsl:with-param name="list" select="$prevlist"/>
            </xsl:call-template>
          </xsl:variable>
          <xsl:value-of select="$prevstart + $prevlength + 1"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="orderedlist-item-number"/>
<xsl:template name="orderedlist-item-number" dtm:id="orderedlist-item-number">
  <!-- context node must be a listitem in an orderedlist -->
  <xsl:param name="node" select="."/>
  <xsl:param name="starting.number"/> 

  <xsl:choose>
    <xsl:when test="$node/@override">
      <xsl:value-of select="$node/@override"/>
    </xsl:when>
    <xsl:when test="$node/preceding-sibling::listitem">
      <xsl:variable name="pnum">
        <xsl:call-template name="orderedlist-item-number">
          <xsl:with-param name="node" 
                          select="$node/preceding-sibling::listitem[1]"/>
          <xsl:with-param name="starting.number" select="$starting.number"/>
        </xsl:call-template>
      </xsl:variable>
      <xsl:value-of select="$pnum + 1"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$starting.number"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="variablelist"/>
<xsl:template match="variablelist" dtm:id="variablelist">
  <xsl:choose>
    <xsl:when test="$presentation = 'list'">
      <xsl:apply-templates select="." mode="vl.as.list"/>
    </xsl:when>
    <xsl:when test="$presentation = 'blocks'">
      <xsl:apply-templates select="." mode="vl.as.blocks"/>
    </xsl:when>
    <xsl:when test="$variablelist.as.blocks">
      <xsl:apply-templates select="." mode="vl.as.blocks"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates select="." mode="vl.as.list"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="title.variablelist.vl-as-list"/>
<xsl:template match="variablelist/title" mode="vl.as.list" dtm:id="title.variablelist.vl-as-list"/>

<dtm:doc dtm:idref="title.variablelist.vl-as-blocks"/>
<xsl:template match="variablelist/title" mode="vl.as.blocks" dtm:id="title.variablelist.vl-as-blocks"/>

<dtm:doc dtm:idref="variablelist.vl-as-list"/>
<xsl:template match="variablelist" mode="vl.as.list" dtm:id="variablelist.vl-as-list">
  <xsl:variable name="termlength">
    <xsl:choose>
      <xsl:when test="$term-width != ''">
        <xsl:value-of select="$term-width"/>
      </xsl:when>
      <xsl:when test="@termlength">
        <xsl:variable name="termlength.is.number">
          <xsl:value-of select="@termlength + 0"/>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="$termlength.is.number = 'NaN'">
            <!-- if the term length isn't just a number, assume it's a measurement -->
            <xsl:value-of select="@termlength"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@termlength"/>
            <xsl:text>em</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <!-- FIXME: this should be a parameter! -->
        <xsl:call-template name="longest.term">
          <xsl:with-param name="terms" select="varlistentry/term"/>
          <xsl:with-param name="maxlength" select="12"/>
        </xsl:call-template>
        <xsl:text>em</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <fo:block>
    <xsl:if test="title[not(self::processing-instruction('se:choice'))]">
      <xsl:apply-templates select="title" mode="list.title.mode"/>
    </xsl:if>

    <fo:list-block provisional-distance-between-starts="{$termlength}"
      provisional-label-separation="0.25in"
      xsl:use-attribute-sets="list.block.spacing">
      <xsl:apply-templates mode="vl.as.list"/>
    </fo:list-block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="longest.term"/>
<xsl:template name="longest.term" dtm:id="longest.term">
  <xsl:param name="longest" select="0"/>
  <xsl:param name="terms" select="."/>
  <xsl:param name="maxlength" select="-1"/>

  <xsl:choose>
    <xsl:when test="$longest &gt; $maxlength and $maxlength &gt; 0">
      <xsl:value-of select="$maxlength"/>
    </xsl:when>
    <xsl:when test="not($terms)">
      <xsl:value-of select="$longest"/>
    </xsl:when>
    <xsl:when test="string-length($terms[1]) &gt; $longest">
      <xsl:call-template name="longest.term">
        <xsl:with-param name="longest" select="string-length($terms[1])"/>
        <xsl:with-param name="maxlength" select="$maxlength"/>
        <xsl:with-param name="terms" select="$terms[position() &gt; 1]"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="longest.term">
        <xsl:with-param name="longest" select="$longest"/>
        <xsl:with-param name="maxlength" select="$maxlength"/>
        <xsl:with-param name="terms" select="$terms[position() &gt; 1]"/>
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="varlistentry.vl-as-list"/>
<xsl:template match="varlistentry" mode="vl.as.list" dtm:id="varlistentry.vl-as-list">
  <fo:list-item xsl:use-attribute-sets="list.item.spacing">
    <fo:list-item-label end-indent="label-end()" text-align="start">
      <fo:block>
        <xsl:apply-templates select="term"/>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <fo:block>
        <xsl:apply-templates select="listitem"/>
      </fo:block>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

<dtm:doc dtm:idref="variablelist.vl-as-blocks"/>
<xsl:template match="variablelist" mode="vl.as.blocks" dtm:id="variablelist.vl-as-blocks">
  <fo:block>
    <xsl:if test="title[not(self::processing-instruction('se:choice'))]">
      <xsl:apply-templates select="title" mode="list.title.mode"/>
    </xsl:if>

    <fo:block xsl:use-attribute-sets="list.block.spacing">
      <xsl:apply-templates mode="vl.as.blocks"/>
    </fo:block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="varlistentry.vl-as-blocks"/>
<xsl:template match="varlistentry" mode="vl.as.blocks" dtm:id="varlistentry.vl-as-blocks">
  <fo:block>
    <fo:block xsl:use-attribute-sets="list.item.spacing"  
      keep-together.within-column="always" 
      keep-with-next.within-column="always">
      <xsl:apply-templates select="term[not(self::processing-instruction('se:choice'))]"/>
    </fo:block>
    <fo:block start-indent="0.25in">
      <xsl:apply-templates select="listitem"/>
    </fo:block>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="term.varlistentry"/>
<xsl:template match="varlistentry/term" dtm:id="term.varlistentry">
  <xsl:choose>
    <xsl:when test="not(position() = last()) and not(following-sibling::*[1][self::processing-instruction('se:choice')])">
      <fo:inline><xsl:apply-templates/></fo:inline><xsl:text>, </xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <fo:inline><xsl:apply-templates/></fo:inline>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="listitem.varlistentry"/>
<xsl:template match="varlistentry/listitem" dtm:id="listitem.varlistentry">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<!-- ==================================================================== -->

<dtm:doc dtm:idref="title.list-title-mode"/>
<xsl:template match="title" mode="list.title.mode" dtm:id="title.list-title-mode">
  <xsl:call-template name="formal.object.heading">
    <xsl:with-param name="object" select=".."/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="procedure"/>
<xsl:template match="procedure" dtm:id="procedure">

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

  <xsl:variable name="preamble"
                select="*[not(self::step or self::title)]"/>

  <fo:block xsl:use-attribute-sets="list.block.spacing">
    <xsl:if test="./title and $placement = 'before'">
      <!-- n.b. gentext code tests for $formal.procedures and may make an "informal" -->
      <!-- heading even though we called formal.object.heading. odd but true. -->
      <xsl:call-template name="formal.object.heading"/>
    </xsl:if>

    <xsl:apply-templates select="$preamble"/>

    <fo:list-block xsl:use-attribute-sets="list.block.spacing"
                   provisional-distance-between-starts="2em"
                   provisional-label-separation="0.2em">
      <xsl:apply-templates select="step"/>
    </fo:list-block>

    <xsl:if test="./title and $placement != 'before'">
      <!-- n.b. gentext code tests for $formal.procedures and may make an "informal" -->
      <!-- heading even though we called formal.object.heading. odd but true. -->
      <xsl:call-template name="formal.object.heading"/>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="title.procedure"/>
<xsl:template match="procedure/title" dtm:id="title.procedure">
</xsl:template>

<dtm:doc dtm:idref="substeps"/>
<xsl:template match="substeps" dtm:id="substeps">
  <fo:list-block xsl:use-attribute-sets="list.block.spacing"
                 provisional-distance-between-starts="2em"
                 provisional-label-separation="0.2em">
    <xsl:apply-templates/>
  </fo:list-block>
</xsl:template>

<dtm:doc dtm:idref="step"/>
<xsl:template match="step" dtm:id="step">
  <fo:list-item xsl:use-attribute-sets="list.item.spacing">
    <fo:list-item-label end-indent="label-end()">
      <fo:block>
        <!-- dwc: fix for one step procedures. Use a bullet if there's no step 2 -->
        <xsl:choose>
          <xsl:when test="count(../step) = 1">
            <xsl:text>&#x2022;</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="." mode="number">
              <xsl:with-param name="recursive" select="0"/>
            </xsl:apply-templates>.
          </xsl:otherwise>
        </xsl:choose>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <xsl:apply-templates/>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

<dtm:doc dtm:idref="step.number"/>
<xsl:template match="step" mode="number" dtm:id="step.number">

  <xsl:param name="rest" select="''"/>
  <xsl:param name="recursive" select="1"/>
  <xsl:variable name="format">
    <xsl:call-template name="procedure.step.numeration"/>
  </xsl:variable>
  <xsl:variable name="num">
    <xsl:number count="step" format="{$format}"/>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="$recursive != 0 and ancestor::step">
      <xsl:apply-templates select="ancestor::step[1]" mode="number">
        <xsl:with-param name="rest" select="concat('.', $num, $rest)"/>
      </xsl:apply-templates>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="concat($num, $rest)"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:param name="procedure.step.numeration.formats" select="'1aiAI'"/>

<dtm:doc dtm:idref="procedure.step.numeration"/>
<xsl:template name="procedure.step.numeration" dtm:id="procedure.step.numeration">
  <xsl:param name="context" select="."/>
  <xsl:variable name="format.length"
                select="string-length($procedure.step.numeration.formats)"/>
  <xsl:choose>
    <xsl:when test="local-name($context) = 'substeps'">
      <xsl:variable name="ssdepth"
                    select="count($context/ancestor::substeps)"/>
      <xsl:variable name="sstype" select="($ssdepth mod $format.length)+2"/>
      <xsl:choose>
        <xsl:when test="$sstype &gt; $format.length">
          <xsl:value-of select="substring($procedure.step.numeration.formats,1,1)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring($procedure.step.numeration.formats,$sstype,1)"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="local-name($context) = 'step'">
      <xsl:variable name="sdepth"
                    select="count($context/ancestor::substeps)"/>
      <xsl:variable name="stype" select="($sdepth mod $format.length)+1"/>
      <xsl:value-of select="substring($procedure.step.numeration.formats,$stype,1)"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:message>
        <xsl:text>Unexpected context in procedure.step.numeration: </xsl:text>
        <xsl:value-of select="local-name($context)"/>
      </xsl:message>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="title.step"/>
<xsl:template match="step/title" dtm:id="title.step">
  <fo:block font-weight="bold">
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="simplelist"/>
<xsl:template match="simplelist" dtm:id="simplelist">
  <xsl:variable name="cols">
    <xsl:choose>
      <xsl:when test="@columns">
        <xsl:value-of select="@columns"/>
      </xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <fo:table xsl:use-attribute-sets="normal.para.spacing">
    <xsl:call-template name="simplelist.table.columns">
      <xsl:with-param name="cols" select="$cols"/>
    </xsl:call-template>
    <fo:table-body>
      <xsl:choose>
        <xsl:when test="@type='horiz'">
          <xsl:for-each select="member">
            <xsl:if test="(position() + $cols - 1) mod $cols = 0">
              <xsl:variable name="from" select="position()"/>
              <xsl:variable name="to" select="$from + $cols"/>
              <fo:table-row>
                <xsl:apply-templates select="../member[(position() &gt;= $from) and (position() &lt; $to)]"/>
              </fo:table-row>
            </xsl:if>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="rows" select="floor((count(member)+$cols - 1) div $cols)"/>
          <xsl:for-each select="member">
            <xsl:if test="position() &lt;= $rows">
              <xsl:variable name="pos" select="position()-1"/>
              <fo:table-row>
                <xsl:apply-templates select="../member[(position() - $pos + $rows - 1) mod $rows = 0]"/>
              </fo:table-row>
            </xsl:if>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
    </fo:table-body>
  </fo:table>
</xsl:template>

<dtm:doc dtm:idref="inline.simplelist"/>
<xsl:template match="simplelist[@type='inline']" dtm:id="inline.simplelist">
  <fo:inline><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="simplelist.table.columns"/>
<xsl:template name="simplelist.table.columns" dtm:id="simplelist.table.columns">
  <xsl:param name="cols" select="1"/>
  <xsl:param name="curcol" select="1"/>
  <fo:table-column column-number="{$curcol}"/>
  <xsl:if test="$curcol &lt; $cols">
    <xsl:call-template name="simplelist.table.columns">
      <xsl:with-param name="cols" select="$cols"/>
      <xsl:with-param name="curcol" select="$curcol + 1"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="member-seg"/>
<xsl:template match="member|seg" dtm:id="member-seg">
  <fo:table-cell>
    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </fo:table-cell>
</xsl:template>

<dtm:doc dtm:idref="member.inlinesimplelist"/>
<xsl:template match="simplelist[@type='inline']/member" dtm:id="member.inlinesimplelist">
  <fo:inline>
    <xsl:apply-templates/>
    <xsl:text>, </xsl:text>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="lastmember.inlinesimplelist"/>
<xsl:template match="simplelist[@type='inline']/member[position()=last()]"
              priority="2" dtm:id="lastmember.inlinesimplelist">
  <fo:inline>
    <xsl:apply-templates/>
  </fo:inline>
</xsl:template>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="segmentedlist"/>
<xsl:template match="segmentedlist" dtm:id="segmentedlist">
  <fo:block> 
   <xsl:apply-templates 
      select="title[not(self::processing-instruction('se:choice'))]" 
      mode="plain.formal.title.mode"/>
   <xsl:choose>
    <xsl:when test="segtitle[not(self::processing-instruction('se:choice'))]">
      <fo:table xsl:use-attribute-sets="normal.para.spacing">
        <xsl:call-template name="simplelist.table.columns">
          <xsl:with-param name="cols" select="count(segtitle)"/>
        </xsl:call-template>
        <fo:table-body>
          <fo:table-row>
            <xsl:apply-templates select="segtitle[not(self::processing-instruction('se:choice'))]"/>
          </fo:table-row>
          <xsl:for-each select="seglistitem[not(self::processing-instruction('se:choice'))]">
            <fo:table-row>
              <xsl:apply-templates select="seg"/>
            </fo:table-row>
          </xsl:for-each>
        </fo:table-body>
      </fo:table>
    </xsl:when>
    <xsl:when test="title[not(self::processing-instruction('se:choice'))]">
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates select="node()"/>
    </xsl:otherwise>
   </xsl:choose>
  </fo:block> 
</xsl:template>

<dtm:doc dtm:idref="segtitle"/>
<xsl:template match="segtitle" dtm:id="segtitle">
  <fo:table-cell>
    <fo:block font-weight="bold">
      <xsl:apply-templates select="*[not(self::processing-instruction('se:choice'))]"/>
    </fo:block>
  </fo:table-cell>
</xsl:template>

<!-- ==================================================================== -->
</xsl:stylesheet>

