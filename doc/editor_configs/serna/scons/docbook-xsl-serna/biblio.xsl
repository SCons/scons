<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<dtm:doc dtm:idref="bibliography"/>
<xsl:template match="bibliography" dtm:id="bibliography">
  <xsl:variable name="preamble"
                select="bibliographyinfo|title|subtitle|titleabbrev"/>
  <xsl:variable name="content" select="*[not(self::bibliographyinfo or 
                                             self::title or self::subtitle
                                             or self::titleabbrev)]"/>
  <fo:block padding-bottom="1.5em">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="bibliography.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="bibliodiv"/>
<xsl:template match="bibliodiv" dtm:id="bibliodiv">
  <xsl:variable name="preamble"
                select="title|subtitle|titleabbrev"/>
  <xsl:variable name="content" select="*[not(self::title or self::subtitle
                                             or self::titleabbrev)]"/>
  <fo:block padding-bottom="1.5em">
    <xsl:call-template name="handle.empty">
      <xsl:with-param name="titles">
        <xsl:call-template name="bibliodiv.titlepage"/>
      </xsl:with-param>
      <xsl:with-param name="preamble" select="$preamble"/>
      <xsl:with-param name="content" select="$content"/>
    </xsl:call-template>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="biblioentry"/>
<xsl:template match="biblioentry" dtm:id="biblioentry">
  <fo:block xsl:use-attribute-sets="normal.para.properties"
    start-indent="0.5in">
    <xsl:call-template name="biblioentry.label"/>
    <xsl:apply-templates mode="bibliography.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="bibliomixed"/>
<xsl:template match="bibliomixed" dtm:id="bibliomixed">
  <fo:block xsl:use-attribute-sets="normal.para.properties"
    start-indent="0.5in">
    <xsl:call-template name="biblioentry.label"/>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="biblioentry.label"/>
<xsl:template name="biblioentry.label" dtm:id="biblioentry.label">
  <xsl:param name="node" select="."/>

  <xsl:choose>
    <xsl:when test="$bibliography.numbered != 0">
      <xsl:text>[</xsl:text>
      <xsl:number from="bibliography" count="biblioentry|bibliomixed"
                  level="multiple" format="1."/>
      <xsl:text>] </xsl:text>
    </xsl:when>
    <xsl:when test="local-name($node/child::*[1]) = 'abbrev'">
      <xsl:text>[</xsl:text>
      <xsl:apply-templates select="$node/abbrev[1]"/>
      <xsl:text>] </xsl:text>
    </xsl:when>
    <xsl:when test="$node/@xreflabel">
      <xsl:text>[</xsl:text>
      <xsl:value-of select="$node/@xreflabel"/>
      <xsl:text>] </xsl:text>
    </xsl:when>
    <xsl:when test="$node/@id">
      <xsl:text>[</xsl:text>
      <xsl:value-of select="$node/@id"/>
      <xsl:text>] </xsl:text>
    </xsl:when>
    <xsl:otherwise><!-- nop --></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="all.bibliography-mode"/>
<xsl:template match="*" mode="bibliography.mode" dtm:id="all.bibliography-mode">
  <xsl:apply-templates select="."/><!-- try the default mode -->
</xsl:template>

<dtm:doc dtm:elements="abbrev" dtm:idref="abbrev.bibliography-mode abbrev.bibliomixed-mode"/>
<xsl:template match="abbrev" mode="bibliography.mode" dtm:id="abbrev.bibliography-mode">
  <xsl:if test="preceding-sibling::*">
    <fo:inline>
      <xsl:apply-templates mode="bibliography.mode"/>
    </fo:inline>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:elements="abstract" dtm:idref="abstract.bibliography-mode abstract.bibliomixed-mode"/>
<xsl:template match="abstract" mode="bibliography.mode" dtm:id="abstract.bibliography-mode">
  <!-- suppressed -->
</xsl:template>

<dtm:doc dtm:elements="address" dtm:idref="address.bibliography-mode address.bibliomixed-mode"/>
<xsl:template match="address" mode="bibliography.mode" dtm:id="address.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="affiliation" dtm:idref="affiliation.bibliography-mode affiliation.bibliomixed-mode"/>
<xsl:template match="affiliation" mode="bibliography.mode" dtm:id="affiliation.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="shortaffil" dtm:idref="shortaffil.bibliography-mode shortaffil.bibliomixed-mode"/>
<xsl:template match="shortaffil" mode="bibliography.mode" dtm:id="shortaffil.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="jobtitle" dtm:idref="jobtitle.bibliography-mode jobtitle.bibliomixed-mode"/>
<xsl:template match="jobtitle" mode="bibliography.mode" dtm:id="jobtitle.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="artchilds.bibliography-mode"/>
<xsl:template match="artheader|articleinfo" mode="bibliography.mode" dtm:id="artchilds.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="artpagenums" dtm:idref="artpagenums.bibliography-mode author.bibliomixed-mode"/>
<xsl:template match="artpagenums" mode="bibliography.mode" dtm:id="artpagenums.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="author" dtm:idref="author.bibliography-mode author.bibliomixed-mode"/>
<xsl:template match="author" mode="bibliography.mode" dtm:id="author.bibliography-mode">
  <fo:inline>
    <xsl:call-template name="person.name"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="authorblurb" dtm:idref="authorblurb.bibliography-mode authorblurb.bibliomixed-mode"/>
<xsl:template match="authorblurb" mode="bibliography.mode" dtm:id="authorblurb.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="authorgroup" dtm:idref="authorgroup.bibliography-mode authorgroup.bibliomixed-mode"/>
<xsl:template match="authorgroup" mode="bibliography.mode" dtm:id="authorgroup.bibliography-mode">
  <fo:inline>
    <xsl:call-template name="person.name.list"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="authorinitials" dtm:idref="authorinitials.bibliography-mode authorinitials.bibliomixed-mode"/>
<xsl:template match="authorinitials" mode="bibliography.mode" dtm:id="authorinitials.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="bibliomisc" dtm:idref="bibliomisc.bibliography-mode bibliomisc.bibliomixed-mode"/>
<xsl:template match="bibliomisc" mode="bibliography.mode" dtm:id="bibliomisc.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="bibliomset.bibliography-mode"/>
<xsl:template match="bibliomset" mode="bibliography.mode" dtm:id="bibliomset.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<!-- ================================================== -->
<dtm:doc dtm:elements="biblioset" dtm:idref="biblioset.bibliography-mode biblioset.bibliomixed-mode"/>
<xsl:template match="biblioset" mode="bibliography.mode" dtm:id="biblioset.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="bibliosettitles.bibliography-mode"/>
<xsl:template match="biblioset/title|biblioset/citetitle" 
              mode="bibliography.mode"  dtm:id="bibliosettitles.bibliography-mode">
  <xsl:variable name="relation" select="../@relation"/>
  <xsl:choose>
    <xsl:when test="$relation='article' or @pubwork='article'">
      <xsl:call-template name="gentext.startquote"/>
      <xsl:apply-templates mode="bibliography.mode"/>
      <xsl:call-template name="gentext.endquote"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:inline font-style="italic">
        <xsl:apply-templates/>
      </fo:inline>
    </xsl:otherwise>
  </xsl:choose>
  <xsl:value-of select="$biblioentry.item.separator"/>
</xsl:template>

<!-- ================================================== -->
<dtm:doc dtm:idref="bookbiblio.bibliography-mode"/>
<xsl:template match="bookbiblio" mode="bibliography.mode" dtm:id="bookbiblio.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="citetitle" dtm:idref="citetitle.bibliography-mode citetitle.bibliomixed-mode"/>
<xsl:template match="citetitle" mode="bibliography.mode" dtm:id="citetitle.bibliography-mode">
  <fo:inline>
    <xsl:choose>
      <xsl:when test="@pubwork = 'article'">
        <xsl:call-template name="gentext.startquote"/>
        <xsl:apply-templates mode="bibliography.mode"/>
        <xsl:call-template name="gentext.endquote"/>
      </xsl:when>
      <xsl:otherwise>
        <fo:inline font-style="italic">
          <xsl:apply-templates mode="bibliography.mode"/>
        </fo:inline>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="collab" dtm:idref="collab.bibliography-mode collab.bibliomixed-mode"/>
<xsl:template match="collab" mode="bibliography.mode" dtm:id="collab.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="confgroup" dtm:idref="confgroup.bibliography-mode confgroup.bibliomixed-mode"/>
<xsl:template match="confgroup" mode="bibliography.mode" dtm:id="confgroup.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="contractnum" dtm:idref="contractnum.bibliography-mode contractnum.bibliomixed-mode"/>
<xsl:template match="contractnum" mode="bibliography.mode" dtm:id="contractnum.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="contractsponsor" dtm:idref="contractsponsor.bibliography-mode contractsponsor.bibliomixed-mode"/>
<xsl:template match="contractsponsor" mode="bibliography.mode" dtm:id="contractsponsor.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="contrib" dtm:idref="contrib.bibliography-mode contrib.bibliomixed-mode"/>
<xsl:template match="contrib" mode="bibliography.mode" dtm:id="contrib.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<!-- ================================================== -->
<dtm:doc dtm:elements="copyright" dtm:idref="copyright.bibliography-mode copyright.bibliomixed-mode"/>
<xsl:template match="copyright" mode="bibliography.mode" dtm:id="copyright.bibliography-mode">
  <fo:inline>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'Copyright'"/>
    </xsl:call-template>
    <xsl:call-template name="gentext.space"/>
    <xsl:call-template name="dingbat">
      <xsl:with-param name="dingbat">copyright</xsl:with-param>
    </xsl:call-template>
    <xsl:call-template name="gentext.space"/>
    <xsl:apply-templates select="year" mode="bibliography.mode"/>
    <xsl:if test="holder">
      <xsl:call-template name="gentext.space"/>
      <xsl:apply-templates select="holder" mode="bibliography.mode"/>
    </xsl:if>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<xsl:template match="year" mode="bibliography.mode" dtm:id="year.bibliography-mode">
  <xsl:apply-templates/><xsl:text>, </xsl:text>
</xsl:template>

<xsl:template match="year[position()=last()]" mode="bibliography.mode" dtm:id="lastyear.bibliography-mode">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="holder.bibliography-mode"/>
<xsl:template match="holder" mode="bibliography.mode" dtm:id="holder.bibliography-mode">
  <xsl:apply-templates/>
</xsl:template>

<!-- ================================================== -->
<dtm:doc dtm:elements="corpauthor" dtm:idref="corpauthor.bibliography-mode corpauthor.bibliomixed-mode"/>
<xsl:template match="corpauthor" mode="bibliography.mode" dtm:id="corpauthor.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="corpname" dtm:idref="corpname.bibliography-mode corpname.bibliomixed-mode"/>
<xsl:template match="corpname" mode="bibliography.mode" dtm:id="corpname.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="date" dtm:idref="date.bibliography-mode date.bibliomixed-mode"/>
<xsl:template match="date" mode="bibliography.mode" dtm:id="date.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="edition" dtm:idref="edition.bibliography-mode edition.bibliomixed-mode"/>
<xsl:template match="edition" mode="bibliography.mode" dtm:id="edition.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="editor" dtm:idref="editor.bibliography-mode editor.bibliomixed-mode"/>
<xsl:template match="editor" mode="bibliography.mode" dtm:id="editor.bibliography-mode">
  <fo:inline>
    <xsl:call-template name="person.name"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="firstname" dtm:idref="firstname.bibliography-mode firstname.bibliomixed-mode"/>
<xsl:template match="firstname" mode="bibliography.mode" dtm:id="firstname.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="honorific" dtm:idref="honorific.bibliography-mode honorific.bibliomixed-mode"/>
<xsl:template match="honorific" mode="bibliography.mode" dtm:id="honorific.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="indexterm" dtm:idref="indexterm.bibliography-mode indexterm.bibliomixed-mode"/>
<xsl:template match="indexterm" mode="bibliography.mode" dtm:id="indexterm.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="invpartnumber" dtm:idref="invpartnumber.bibliography-mode invpartnumber.bibliomixed-mode"/>
<xsl:template match="invpartnumber" mode="bibliography.mode" dtm:id="invpartnumber.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="isbn" dtm:idref="isbn.bibliography-mode isbn.bibliomixed-mode"/>
<xsl:template match="isbn" mode="bibliography.mode" dtm:id="isbn.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="issn" dtm:idref="issn.bibliography-mode issn.bibliomixed-mode"/>
<xsl:template match="issn" mode="bibliography.mode" dtm:id="issn.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="biblioid" dtm:idref="biblioid.bibliography-mode biblioid.bibliomixed-mode"/>
<xsl:template match="biblioid" mode="bibliography.mode" dtm:id="biblioid.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="issuenum" dtm:idref="issuenum.bibliography-mode issuenum.bibliomixed-mode"/>
<xsl:template match="issuenum" mode="bibliography.mode" dtm:id="issuenum.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="lineage" dtm:idref="lineage.bibliography-mode lineage.bibliomixed-mode"/>
<xsl:template match="lineage" mode="bibliography.mode" dtm:id="lineage.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="orgname" dtm:idref="orgname.bibliography-mode orgname.bibliomixed-mode"/>
<xsl:template match="orgname" mode="bibliography.mode" dtm:id="orgname.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="othercredit" dtm:idref="othercredit.bibliography-mode othercredit.bibliomixed-mode"/>
<xsl:template match="othercredit" mode="bibliography.mode" dtm:id="othercredit.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="othername" dtm:idref="othername.bibliography-mode othername.bibliomixed-mode"/>
<xsl:template match="othername" mode="bibliography.mode" dtm:id="othername.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="pagenums" dtm:idref="pagenums.bibliography-mode pagenums.bibliomixed-mode"/>
<xsl:template match="pagenums" mode="bibliography.mode" dtm:id="pagenums.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="printhistory" dtm:idref="printhistory.bibliography-mode printhistory.bibliomixed-mode"/>
<xsl:template match="printhistory" mode="bibliography.mode" dtm:id="printhistory.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="productname" dtm:idref="productname.bibliography-mode productname.bibliomixed-mode"/>
<xsl:template match="productname" mode="bibliography.mode" dtm:id="productname.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="productnumber" dtm:idref="productnumber.bibliography-mode productnumber.bibliomixed-mode"/>
<xsl:template match="productnumber" mode="bibliography.mode" dtm:id="productnumber.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="pubdate" dtm:idref="pubdate.bibliography-mode pubdate.bibliomixed-mode"/>
<xsl:template match="pubdate" mode="bibliography.mode" dtm:id="pubdate.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="publisher" dtm:idref="pubdate.bibliography-mode pubdate.bibliomixed-mode"/>
<xsl:template match="publisher" mode="bibliography.mode" dtm:id="pubdate.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="publishername" dtm:idref="publishername.bibliography-mode publishername.bibliomixed-mode"/>
<xsl:template match="publishername" mode="bibliography.mode" dtm:id="publishername.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="pubsnumber" dtm:idref="pubsnumber.bibliography-mode pubsnumber.bibliomixed-mode"/>
<xsl:template match="pubsnumber" mode="bibliography.mode" dtm:id="pubsnumber.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="releaseinfo" dtm:idref="releaseinfo.bibliography-mode releaseinfo.bibliomixed-mode"/>
<xsl:template match="releaseinfo" mode="bibliography.mode" dtm:id="releaseinfo.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="revhistory" dtm:idref="revhistory.bibliography-mode revhistory.bibliomixed-mode"/>
<xsl:template match="revhistory" mode="bibliography.mode" dtm:id="revhistory.bibliography-mode">
  <fo:block>
    <xsl:apply-templates select="."/> <!-- use normal mode -->
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="seriesinfo.bibliography-mode"/>
<xsl:template match="seriesinfo" mode="bibliography.mode" dtm:id="seriesinfo.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="seriesvolnums" dtm:idref="seriesvolnums.bibliography-mode seriesvolnums.bibliomixed-mode"/>
<xsl:template match="seriesvolnums" mode="bibliography.mode" dtm:id="seriesvolnums.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="subtitle" dtm:idref="subtitle.bibliography-mode subtitle.bibliomixed-mode"/>
<xsl:template match="subtitle" mode="bibliography.mode" dtm:id="subtitle.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="surname" dtm:idref="surname.bibliography-mode surname.bibliomixed-mode"/>
<xsl:template match="surname" mode="bibliography.mode" dtm:id="surname.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="title" dtm:idref="title.bibliography-mode title.bibliomixed-mode"/>
<xsl:template match="title" mode="bibliography.mode" dtm:id="title.bibliography-mode">
  <fo:inline>
    <fo:inline font-style="italic">
      <xsl:apply-templates mode="bibliography.mode"/>
    </fo:inline>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="titleabbrev" dtm:idref="titleabbrev.bibliography-mode titleabbrev.bibliomixed-mode"/>
<xsl:template match="titleabbrev" mode="bibliography.mode" dtm:id="titleabbrev.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="volumenum" dtm:idref="volumenum.bibliography-mode volumenum.bibliomixed-mode"/>
<xsl:template match="volumenum" mode="bibliography.mode" dtm:id="volumenum.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="orgdiv.bibliography-mode"/>
<xsl:template match="orgdiv" mode="bibliography.mode" dtm:id="orgdiv.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="collabname.bibliography-mode"/>
<xsl:template match="collabname" mode="bibliography.mode" dtm:id="collabname.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="confdates.bibliography-mode"/>
<xsl:template match="confdates" mode="bibliography.mode" dtm:id="confdates.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="conftitle.bibliography-mode"/>
<xsl:template match="conftitle" mode="bibliography.mode" dtm:id="conftitle.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="confnum.bibliography-mode"/>
<xsl:template match="confnum" mode="bibliography.mode" dtm:id="confnum.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="confsponsor.bibliography-mode"/>
<xsl:template match="confsponsor" mode="bibliography.mode" dtm:id="confsponsor.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="bibliocoverage|biblioid|bibliorelation|bibliosource" dtm:idref="bibliochilds.bibliography-mode bibliochilds.bibliomixed-mode"/>
<xsl:template match="bibliocoverage|biblioid|bibliorelation|bibliosource"
              mode="bibliography.mode" dtm:id="bibliochilds.bibliography-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
    <xsl:value-of select="$biblioentry.item.separator"/>
  </fo:inline>
</xsl:template>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="all.bibliomixed-mode"/>
<xsl:template match="*" mode="bibliomixed.mode" dtm:id="all.bibliomixed-mode">
  <xsl:apply-templates select="."/><!-- try the default mode -->
</xsl:template>

<xsl:template match="abbrev" mode="bibliomixed.mode" dtm:id="abbrev.bibliomixed-mode">
  <xsl:if test="preceding-sibling::*">
    <fo:inline>
      <xsl:apply-templates mode="bibliomixed.mode"/>
    </fo:inline>
  </xsl:if>
</xsl:template>

<xsl:template match="abstract" mode="bibliomixed.mode" dtm:id="abstract.bibliomixed-mode">
  <fo:block start-indent="1in">
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="para.bibliomixed-mode"/>
<xsl:template match="para" mode="bibliomixed.mode" dtm:id="para.bibliomixed-mode">
  <fo:block>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="address" mode="bibliomixed.mode" dtm:id="address.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="affiliation" mode="bibliomixed.mode" dtm:id="affiliation.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="shortaffil" mode="bibliomixed.mode" dtm:id="shortaffil.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="jobtitle" mode="bibliomixed.mode" dtm:id="jobtitle.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliography.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="artpagenums" mode="bibliomixed.mode" dtm:id="artpagenums.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="author" mode="bibliomixed.mode" dtm:id="author.bibliomixed-mode">
  <fo:inline>
    <xsl:call-template name="person.name"/>
  </fo:inline>
</xsl:template>

<xsl:template match="authorblurb" mode="bibliomixed.mode" dtm:id="authorblurb.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="authorgroup" mode="bibliomixed.mode" dtm:id="authorgroup.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="authorinitials" mode="bibliomixed.mode" dtm:id="authorinitials.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="bibliomisc" mode="bibliomixed.mode" dtm:id="bibliomisc.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<!-- ================================================== -->

<xsl:template match="bibliomset" mode="bibliomixed.mode" dtm:id="bibliomset.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="bibliomset/title|bibliomset/citetitle" 
              mode="bibliomixed.mode" dtm:id="bibliotitles.bibliomixed-mode">
  <xsl:variable name="relation" select="../@relation"/>
  <xsl:choose>
    <xsl:when test="$relation='article' or @pubwork='article'">
      <xsl:call-template name="gentext.startquote"/>
      <xsl:apply-templates mode="bibliomixed.mode"/>
      <xsl:call-template name="gentext.endquote"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:inline font-style="italic">
        <xsl:apply-templates/>
      </fo:inline>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- ================================================== -->

<xsl:template match="biblioset" mode="bibliomixed.mode" dtm:id="biblioset.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="citetitle" mode="bibliomixed.mode" dtm:id="citetitle.bibliomixed-mode">
  <xsl:choose>
    <xsl:when test="@pubwork = 'article'">
      <xsl:call-template name="gentext.startquote"/>
      <xsl:apply-templates mode="bibliomixed.mode"/>
      <xsl:call-template name="gentext.endquote"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:inline font-style="italic">
        <xsl:apply-templates mode="bibliography.mode"/>
      </fo:inline>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="collab" mode="bibliomixed.mode" dtm:id="collab.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="confgroup" mode="bibliomixed.mode" dtm:id="confgroup.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="contractnum" mode="bibliomixed.mode" dtm:id="contractnum.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="contractsponsor" mode="bibliomixed.mode" dtm:id="contractsponsor.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="contrib" mode="bibliomixed.mode" dtm:id="contrib.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="copyright" mode="bibliomixed.mode" dtm:id="copyright.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="corpauthor" mode="bibliomixed.mode" dtm:id="corpauthor.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="corpname" mode="bibliomixed.mode" dtm:id="corpname.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="date" mode="bibliomixed.mode" dtm:id="date.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="edition" mode="bibliomixed.mode" dtm:id="edition.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="editor" mode="bibliomixed.mode" dtm:id="editor.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="firstname" mode="bibliomixed.mode" dtm:id="firstname.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="honorific" mode="bibliomixed.mode" dtm:id="honorific.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="indexterm" mode="bibliomixed.mode" dtm:id="indexterm.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="invpartnumber" mode="bibliomixed.mode" dtm:id="invpartnumber.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="isbn" mode="bibliomixed.mode" dtm:id="isbn.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="issn" mode="bibliomixed.mode" dtm:id="issn.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="biblioid" mode="bibliomixed.mode" dtm:id="biblioid.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="issuenum" mode="bibliomixed.mode" dtm:id="issuenum.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="lineage" mode="bibliomixed.mode" dtm:id="lineage.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="orgname" mode="bibliomixed.mode" dtm:id="orgname.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="othercredit" mode="bibliomixed.mode" dtm:id="othercredit.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="othername" mode="bibliomixed.mode" dtm:id="othername.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="pagenums" mode="bibliomixed.mode" dtm:id="pagenums.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="printhistory" mode="bibliomixed.mode" dtm:id="printhistory.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="productname" mode="bibliomixed.mode" dtm:id="productname.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="productnumber" mode="bibliomixed.mode" dtm:id="productnumber.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="pubdate" mode="bibliomixed.mode" dtm:id="pubdate.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="publisher" mode="bibliomixed.mode" dtm:id="publisher.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="publishername" mode="bibliomixed.mode" dtm:id="publishername.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="pubsnumber" mode="bibliomixed.mode" dtm:id="pubsnumber.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="releaseinfo" mode="bibliomixed.mode" dtm:id="releaseinfo.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="revhistory" mode="bibliomixed.mode" dtm:id="revhistory.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="seriesvolnums" mode="bibliomixed.mode" dtm:id="seriesvolnums.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="subtitle" mode="bibliomixed.mode" dtm:id="subtitle.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="surname" mode="bibliomixed.mode" dtm:id="surname.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="title" mode="bibliomixed.mode" dtm:id="title.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="titleabbrev" mode="bibliomixed.mode" dtm:id="titleabbrev.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="volumenum" mode="bibliomixed.mode" dtm:id="volumenum.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<xsl:template match="bibliocoverage|biblioid|bibliorelation|bibliosource"
              mode="bibliomixed.mode" dtm:id="bibliochilds.bibliomixed-mode">
  <fo:inline>
    <xsl:apply-templates mode="bibliomixed.mode"/>
  </fo:inline>
</xsl:template>

<!-- ==================================================================== -->

</xsl:stylesheet>
