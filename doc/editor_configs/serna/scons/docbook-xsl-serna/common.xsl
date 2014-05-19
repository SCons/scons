<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:doc="http://nwalsh.com/xsl/documentation/1.0"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                exclude-result-prefixes="doc"
                extension-element-prefixes="dtm"
                version='1.0'>

  <!-- Counts the depth of the sections/refsections/sectN when
      "title" is a context node -->
  <dtm:doc dtm:idref="section.level"/>
  <xsl:template name="section.level" dtm:id="section.level">
    <xsl:param name="parent" select="parent::*"/>
    <xsl:variable name="title.parent" select="name($parent)"/>
    <xsl:choose>
      <xsl:when test="$title.parent='section'">
        <xsl:value-of select="count(ancestor::section)"/>
      </xsl:when>
      <xsl:when test="$title.parent='refsection'">
        <xsl:value-of select="count(ancestor::refsection)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable 
          name="nmbr" 
          select="translate($title.parent, 'sectionrfmpl', '')"/>
        <xsl:choose>
          <xsl:when test="number($nmbr) = 'NaN'">1</xsl:when>
          <xsl:otherwise><xsl:value-of select="$nmbr"/></xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<dtm:doc dtm:idref="get.type"/>
<xsl:template name="get.type" dtm:id="get.type">
  <xsl:param name="node" select="."/>
  <xsl:choose>
    <xsl:when test="$node[self::appendix or self::article
                          or self::chapter or self::preface 
                          or self::bibliography or self::glossary
                          or self::index]">component</xsl:when>
    <xsl:when test="$node[self::book or self::part or
                          self::set or self::reference]">division</xsl:when>
    <xsl:otherwise>0</xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="is.component"/>
<xsl:template name="is.component" dtm:id="is.component">
  <xsl:param name="node" select="."/>
  <xsl:choose>
    <xsl:when test="$node[self::appendix or self::article or
                          self::chapter or self::preface or
                          self::bibliography or self::glossary or
                          self::index]">1</xsl:when>
    <xsl:otherwise>0</xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="copyright.years"/>
<xsl:template name="copyright.years" dtm:id="copyright.years">
  <xsl:param name="years"/>
  <xsl:param name="print.ranges" select="1"/>
  <xsl:param name="single.year.ranges" select="0"/>
  <xsl:param name="firstyear" select="0"/>
  <xsl:param name="nextyear" select="0"/>
  <xsl:variable name="num.years" select="count($years)"/>
  <xsl:choose>
    <xsl:when test="$print.ranges = 0">
      <xsl:choose>
        <xsl:when test="$num.years = 0"/>
        <xsl:when test="$num.years = 1">
          <xsl:apply-templates select="$years[1]" mode="titlepage.mode"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="$years[1]" mode="titlepage.mode"/>
          <xsl:text>, </xsl:text>
          <xsl:call-template name="copyright.years">
            <xsl:with-param name="years"
                            select="$years[position() &gt; 1]"/>
            <xsl:with-param name="print.ranges" select="$print.ranges"/>
            <xsl:with-param name="single.year.ranges"
                            select="$single.year.ranges"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="$num.years = 0">
      <xsl:variable name="lastyear" select="$nextyear - 1"/>
      <xsl:choose>
        <xsl:when test="$firstyear = 0">
          <!-- there weren't any years at all -->
        </xsl:when>
        <xsl:when test="$firstyear = $lastyear">
          <xsl:value-of select="$firstyear"/>
        </xsl:when>
        <xsl:when test="$single.year.ranges = 0
                        and $lastyear = $firstyear + 1">
          <xsl:value-of select="$firstyear"/>
          <xsl:text>, </xsl:text>
          <xsl:value-of select="$lastyear"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$firstyear"/>
          <xsl:text>-</xsl:text>
          <xsl:value-of select="$lastyear"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="$firstyear = 0">
      <xsl:call-template name="copyright.years">
        <xsl:with-param name="years"
                        select="$years[position() &gt; 1]"/>
        <xsl:with-param name="firstyear" select="$years[1]"/>
        <xsl:with-param name="nextyear" select="$years[1] + 1"/>
        <xsl:with-param name="print.ranges" select="$print.ranges"/>
        <xsl:with-param name="single.year.ranges"
                        select="$single.year.ranges"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:when test="$nextyear = $years[1]">
      <xsl:call-template name="copyright.years">
        <xsl:with-param name="years"
                        select="$years[position() &gt; 1]"/>
        <xsl:with-param name="firstyear" select="$firstyear"/>
        <xsl:with-param name="nextyear" select="$nextyear + 1"/>
        <xsl:with-param name="print.ranges" select="$print.ranges"/>
        <xsl:with-param name="single.year.ranges"
                        select="$single.year.ranges"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <!-- we have years left, but they aren't in the current range -->
      <xsl:choose>
        <xsl:when test="$nextyear = $firstyear + 1">
          <xsl:value-of select="$firstyear"/>
          <xsl:text>, </xsl:text>
        </xsl:when>
        <xsl:when test="$single.year.ranges = 0
                        and $nextyear = $firstyear + 2">
          <xsl:value-of select="$firstyear"/>
          <xsl:text>, </xsl:text>
          <xsl:value-of select="$nextyear - 1"/>
          <xsl:text>, </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$firstyear"/>
          <xsl:text>-</xsl:text>
          <xsl:value-of select="$nextyear - 1"/>
          <xsl:text>, </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:call-template name="copyright.years">
        <xsl:with-param name="years"
                        select="$years[position() &gt; 1]"/>
        <xsl:with-param name="firstyear" select="$years[1]"/>
        <xsl:with-param name="nextyear" select="$years[1] + 1"/>
        <xsl:with-param name="print.ranges" select="$print.ranges"/>
        <xsl:with-param name="single.year.ranges"
                        select="$single.year.ranges"/>
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="lookup.key"/>
<xsl:template name="lookup.key" dtm:id="lookup.key">
  <xsl:param name="key" select="''"/>
  <xsl:param name="table" select="''"/>

  <xsl:if test="contains($table, ' ')">
    <xsl:choose>
      <xsl:when test="substring-before($table, ' ') = $key">
        <xsl:variable name="rest" select="substring-after($table, ' ')"/>
        <xsl:choose>
          <xsl:when test="contains($rest, ' ')">
            <xsl:value-of select="substring-before($rest, ' ')"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$rest"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="lookup.key">
          <xsl:with-param name="key" select="$key"/>
          <xsl:with-param name="table" select="substring-after(substring-after($table,' '), ' ')"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="copy-string"/>
<xsl:template name="copy-string" dtm:id="copy-string">
  <!-- returns 'count' copies of 'string' -->
  <xsl:param name="string"/>
  <xsl:param name="count" select="0"/>
  <xsl:param name="result"/>

  <xsl:choose>
    <xsl:when test="$count&gt;0">
      <xsl:call-template name="copy-string">
        <xsl:with-param name="string" select="$string"/>
        <xsl:with-param name="count" select="$count - 1"/>
        <xsl:with-param name="result">
          <xsl:value-of select="$result"/>
          <xsl:value-of select="$string"/>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$result"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="decorations"/>
<xsl:template name="decorations" dtm:id="decorations">
  <xsl:param name="key" select="local-name(.)"/>
  <xsl:call-template name="lookup.key">
    <xsl:with-param name="key" select="$key"/>
    <xsl:with-param name="table" select="$generate.toc"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="dingbat"/>
<xsl:template name="dingbat" dtm:id="dingbat">
  <xsl:param name="dingbat">bullet</xsl:param>
  <xsl:variable name="symbol">
    <xsl:choose>
      <xsl:when test="$dingbat='bullet'">o</xsl:when>
      <xsl:when test="$dingbat='copyright'">&#x00A9;</xsl:when>
      <xsl:when test="$dingbat='trademark'">&#x2122;</xsl:when>
      <xsl:when test="$dingbat='trade'">&#x2122;</xsl:when>
      <xsl:when test="$dingbat='registered'">&#x00AE;</xsl:when>
      <xsl:when test="$dingbat='service'">(SM)</xsl:when>
      <xsl:when test="$dingbat='ldquo'">"</xsl:when>
      <xsl:when test="$dingbat='rdquo'">"</xsl:when>
      <xsl:when test="$dingbat='lsquo'">'</xsl:when>
      <xsl:when test="$dingbat='rsquo'">'</xsl:when>
      <xsl:when test="$dingbat='em-dash'">--</xsl:when>
      <xsl:when test="$dingbat='en-dash'">-</xsl:when>
      <xsl:otherwise>o</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="$dingbat.font.family = ''">
      <xsl:copy-of select="$symbol"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:inline font-family="{$dingbat.font.family}">
        <xsl:copy-of select="$symbol"/>
      </fo:inline>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="person.name"/>
<xsl:template name="person.name" dtm:id="person.name">
  <!-- Formats a personal name. Handles corpauthor as a special case. -->
  <xsl:param name="node" select="."/>

  <xsl:variable name="style">
    <xsl:choose>
      <xsl:when test="$node/@role">
        <xsl:value-of select="$node/@role"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text></xsl:text> <!-- TODO: move to a param -->
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:choose>
    <!-- the personname element is a specialcase -->
    <xsl:when test="$node/personname">
      <xsl:call-template name="person.name">
        <xsl:with-param name="node" select="$node/personname"/>
      </xsl:call-template>
    </xsl:when>

    <!-- handle corpauthor as a special case...-->
    <xsl:when test="name($node)='corpauthor'">
      <xsl:apply-templates select="$node"/>
    </xsl:when>

    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$style = 'family-given'">
          <xsl:call-template name="person.name.family-given">
            <xsl:with-param name="node" select="$node"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="$style = 'last-first'">
          <xsl:call-template name="person.name.last-first">
            <xsl:with-param name="node" select="$node"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="person.name.first-last">
            <xsl:with-param name="node" select="$node"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="person.name.family-given"/>
<xsl:template name="person.name.family-given" dtm:id="person.name.family-given">
  <xsl:param name="node" select="."/>

  <!-- The family-given style applies a convention for identifying given -->
  <!-- and family names in locales where it may be ambiguous -->
  <xsl:apply-templates select="$node/surname[1]"/>

  <xsl:if test="$node/surname and $node/firstname">
    <xsl:text> </xsl:text>
  </xsl:if>

  <xsl:apply-templates select="$node/firstname[1]"/>

  <xsl:text> [FAMILY Given]</xsl:text>
</xsl:template>

<dtm:doc dtm:idref="person.name.last-first"/>
<xsl:template name="person.name.last-first" dtm:id="person.name.last-first">
  <xsl:param name="node" select="."/>

  <xsl:apply-templates select="$node/surname[1]"/>

  <xsl:if test="$node/surname and $node/firstname">
    <xsl:text>, </xsl:text>
  </xsl:if>

  <xsl:apply-templates select="$node/firstname[1]"/>
</xsl:template>

<dtm:doc dtm:idref="person.name.first-last"/>
<xsl:template name="person.name.first-last" dtm:id="person.name.first-last">
  <xsl:param name="node" select="."/>

  <xsl:if test="$node/honorific">
    <xsl:apply-templates select="$node/honorific[1]"/>
    <xsl:value-of select="$punct.honorific"/>
  </xsl:if>

  <xsl:if test="$node/firstname">
    <xsl:if test="$node/honorific">
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="$node/firstname[1]"/>
  </xsl:if>

  <xsl:if test="$node/othername and $author.othername.in.middle != 0">
    <xsl:if test="$node/honorific or $node/firstname">
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="$node/othername[1]"/>
  </xsl:if>

  <xsl:if test="$node/surname">
    <xsl:if test="$node/honorific or $node/firstname
                  or ($node/othername and $author.othername.in.middle != 0)">
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="$node/surname[1]"/>
  </xsl:if>

  <xsl:if test="$node/lineage">
    <xsl:text>, </xsl:text>
    <xsl:apply-templates select="$node/lineage[1]"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="person.name.list"/>
<xsl:template name="person.name.list" dtm:id="person.name.list">
  <!-- Return a formatted string representation of the contents of
       the current element. The current element must contain one or
       more AUTHORs, CORPAUTHORs, OTHERCREDITs, and/or EDITORs.

       John Doe
     or
       John Doe and Jane Doe
     or
       John Doe, Jane Doe, and A. Nonymous
  -->
  <xsl:param name="person.list"
             select="author|corpauthor|othercredit|editor"/>
  <xsl:param name="person.count" select="count($person.list)"/>
  <xsl:param name="count" select="1"/>

  <xsl:choose>
    <xsl:when test="$count &gt; $person.count"></xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="person.name">
        <xsl:with-param name="node" select="$person.list[position()=$count]"/>
      </xsl:call-template>

      <xsl:choose>
        <xsl:when test="$person.count = 2 and $count = 1">
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="context" select="'authorgroup'"/>
            <xsl:with-param name="name" select="'sep2'"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="$person.count &gt; 2 and $count+1 = $person.count">
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="context" select="'authorgroup'"/>
            <xsl:with-param name="name" select="'seplast'"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="$count &lt; $person.count">
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="context" select="'authorgroup'"/>
            <xsl:with-param name="name" select="'sep'"/>
          </xsl:call-template>
        </xsl:when>
      </xsl:choose>

      <xsl:call-template name="person.name.list">
        <xsl:with-param name="person.list" select="$person.list"/>
        <xsl:with-param name="person.count" select="$person.count"/>
        <xsl:with-param name="count" select="$count+1"/>
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template><!-- person.name.list -->

<xsl:variable name="arg.choice.opt.open.str">[</xsl:variable>
<xsl:variable name="arg.choice.opt.close.str">]</xsl:variable>
<xsl:variable name="arg.choice.req.open.str">{</xsl:variable>
<xsl:variable name="arg.choice.req.close.str">}</xsl:variable>
<xsl:variable name="arg.choice.plain.open.str"><xsl:text> </xsl:text></xsl:variable>
<xsl:variable name="arg.choice.plain.close.str"><xsl:text> </xsl:text></xsl:variable>
<xsl:variable name="arg.choice.def.open.str">[</xsl:variable>
<xsl:variable name="arg.choice.def.close.str">]</xsl:variable>
<xsl:variable name="arg.rep.repeat.str">...</xsl:variable>
<xsl:variable name="arg.rep.norepeat.str"></xsl:variable>
<xsl:variable name="arg.rep.def.str"></xsl:variable>
<xsl:variable name="arg.or.sep"> | </xsl:variable>
<xsl:variable name="cmdsynopsis.hanging.indent">4pi</xsl:variable>

<xsl:param name="use-serna-extensions" 
    select="contains(system-property('xsl:vendor'), 'Syntext')"/>

</xsl:stylesheet>

