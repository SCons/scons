<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<xsl:attribute-set name="book.titlepage.recto.style">
  <xsl:attribute name="font-family">
    <xsl:value-of select="$title.font.family"/>
  </xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:value-of select="concat($body.font.master,'pt')"/>
    </xsl:attribute>

  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="text-align">center</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="book.titlepage.verso.style">
    <xsl:attribute name="font-size">
      <xsl:value-of select="concat(0.83 * $body.font.master,'pt')"/>
    </xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="article.titlepage.recto.style"/>
<xsl:attribute-set name="article.titlepage.verso.style"/>

<xsl:attribute-set name="set.titlepage.recto.style"/>
<xsl:attribute-set name="set.titlepage.verso.style"/>

<xsl:attribute-set name="part.titlepage.recto.style">
  <xsl:attribute name="text-align">center</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="part.titlepage.verso.style"/>

<xsl:attribute-set name="partintro.titlepage.recto.style"/>
<xsl:attribute-set name="partintro.titlepage.verso.style"/>

<xsl:attribute-set name="reference.titlepage.recto.style"/>
<xsl:attribute-set name="reference.titlepage.verso.style"/>

<xsl:attribute-set name="dedication.titlepage.recto.style"/>
<xsl:attribute-set name="dedication.titlepage.verso.style"/>

<xsl:attribute-set name="preface.titlepage.recto.style"/>
<xsl:attribute-set name="preface.titlepage.verso.style"/>

<xsl:attribute-set name="chapter.titlepage.recto.style"/>
<xsl:attribute-set name="chapter.titlepage.verso.style"/>

<xsl:attribute-set name="appendix.titlepage.recto.style"/>
<xsl:attribute-set name="appendix.titlepage.verso.style"/>

<xsl:attribute-set name="bibliography.titlepage.recto.style"/>
<xsl:attribute-set name="bibliography.titlepage.verso.style"/>

<xsl:attribute-set name="bibliodiv.titlepage.recto.style"/>
<xsl:attribute-set name="bibliodiv.titlepage.verso.style"/>

<xsl:attribute-set name="glossary.titlepage.recto.style"/>
<xsl:attribute-set name="glossary.titlepage.verso.style"/>

<xsl:attribute-set name="glossdiv.titlepage.recto.style"/>
<xsl:attribute-set name="glossdiv.titlepage.verso.style"/>

<xsl:attribute-set name="index.titlepage.recto.style"/>
<xsl:attribute-set name="index.titlepage.verso.style"/>

<xsl:attribute-set name="setindex.titlepage.recto.style"/>
<xsl:attribute-set name="setindex.titlepage.verso.style"/>

<xsl:attribute-set name="indexdiv.titlepage.recto.style"/>
<xsl:attribute-set name="indexdiv.titlepage.verso.style"/>

<xsl:attribute-set name="colophon.titlepage.recto.style"/>
<xsl:attribute-set name="colophon.titlepage.verso.style"/>

<xsl:attribute-set name="section.titlepage.recto.style">
  <xsl:attribute name="keep-together">always</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="section.titlepage.verso.style">
  <xsl:attribute name="keep-together">always</xsl:attribute>
  <xsl:attribute name="keep-with-next">always</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="sect1.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="sect1.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="sect2.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="sect2.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="sect3.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="sect3.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="sect4.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="sect4.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="sect5.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="sect5.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="simplesect.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="simplesect.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="refsynopsisdiv.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="refsynopsisdiv.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="refsection.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="refsection.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="refsect1.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="refsect1.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="refsect2.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="refsect2.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="refsect3.titlepage.recto.style"
                   use-attribute-sets="section.titlepage.recto.style"/>
<xsl:attribute-set name="refsect3.titlepage.verso.style"
                   use-attribute-sets="section.titlepage.verso.style"/>

<xsl:attribute-set name="table.of.contents.titlepage.recto.style"/>
<xsl:attribute-set name="table.of.contents.titlepage.verso.style"/>

<xsl:attribute-set name="list.of.tables.titlepage.recto.style"/>
<xsl:attribute-set name="list.of.tables.contents.titlepage.verso.style"/>

<xsl:attribute-set name="list.of.figures.titlepage.recto.style"/>
<xsl:attribute-set name="list.of.figures.contents.titlepage.verso.style"/>

<xsl:attribute-set name="list.of.equations.titlepage.recto.style"/>
<xsl:attribute-set name="list.of.equations.contents.titlepage.verso.style"/>

<xsl:attribute-set name="list.of.examples.titlepage.recto.style"/>
<xsl:attribute-set name="list.of.examples.contents.titlepage.verso.style"/>

<xsl:attribute-set name="list.of.procedures.titlepage.recto.style"/>
<xsl:attribute-set name="list.of.procedures.contents.titlepage.verso.style"/>

<xsl:attribute-set name="list.of.unknowns.titlepage.recto.style"/>
<xsl:attribute-set name="list.of.unknowns.contents.titlepage.verso.style"/>

<!-- ==================================================================== -->
<dtm:doc dtm:idref="all.titlepage-mode"/>
<xsl:template match="*" mode="titlepage.mode" dtm:id="all.titlepage-mode">
  <!-- if an element isn't found in this mode, try the default mode -->
  <xsl:apply-templates select="."/>
</xsl:template>

<dtm:doc dtm:idref="abbrev.titlepage-mode"/>
<xsl:template match="abbrev" mode="titlepage.mode" dtm:id="abbrev.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="abstract.titlepage-mode"/>
<xsl:template match="abstract" mode="titlepage.mode" dtm:id="abstract.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="abstract/title" dtm:idref="title.abstract.titlepage-mode title.titlepage-title-mode"/>
<xsl:template match="abstract/title" mode="titlepage.mode" dtm:id="title.abstract.titlepage-mode"/>

<xsl:template match="abstract/title" mode="titlepage.abstract.title.mode" dtm:id="title.titlepage-title-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="address.titlepage-mode"/>
<xsl:template match="address" mode="titlepage.mode" dtm:id="address.titlepage-mode">
  <!-- use the normal address handling code -->
  <xsl:apply-templates select="."/>
</xsl:template>

<dtm:doc dtm:idref="affiliation.titlepage-mode"/>
<xsl:template match="affiliation" mode="titlepage.mode" dtm:id="affiliation.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="artpagenums.titlepage-mode"/>
<xsl:template match="artpagenums" mode="titlepage.mode" dtm:id="artpagenums.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="author.titlepage-mode"/>
<xsl:template match="author" mode="titlepage.mode" dtm:id="author.titlepage-mode">
  <fo:block>
    <xsl:call-template name="person.name"/>
    <xsl:if test="affiliation/orgname">
      <xsl:text>, </xsl:text>
      <xsl:apply-templates select="affiliation/orgname" mode="titlepage.mode"/>
    </xsl:if>
    <xsl:if test="email|affiliation/address/email">
      <xsl:text> </xsl:text>
      <xsl:apply-templates select="(email|affiliation/address/email)[1]"/>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="authorblurb.titlepage-mode"/>
<xsl:template match="authorblurb" mode="titlepage.mode" dtm:id="authorblurb.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="authorgroup.titlepage-mode"/>
<xsl:template match="authorgroup" mode="titlepage.mode" dtm:id="authorgroup.titlepage-mode">
  <fo:wrapper>
    <xsl:if test="@id">
      <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
    </xsl:if>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:wrapper>
</xsl:template>

<dtm:doc dtm:idref="authorinitials.titlepage-mode"/>
<xsl:template match="authorinitials" mode="titlepage.mode" dtm:id="authorinitials.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="bibliomisc.titlepage-mode"/>
<xsl:template match="bibliomisc" mode="titlepage.mode" dtm:id="bibliomisc.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="bibliomset.titlepage-mode"/>
<xsl:template match="bibliomset" mode="titlepage.mode" dtm:id="bibliomset.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="collab.titlepage-mode"/>
<xsl:template match="collab" mode="titlepage.mode" dtm:id="collab.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="confgroup.titlepage-mode"/>
<xsl:template match="confgroup" mode="titlepage.mode" dtm:id="confgroup.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="confdates.titlepage-mode"/>
<xsl:template match="confdates" mode="titlepage.mode" dtm:id="confdates.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="conftitle.titlepage-mode"/>
<xsl:template match="conftitle" mode="titlepage.mode" dtm:id="conftitle.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="confnum.titlepage-mode"/>
<xsl:template match="confnum" mode="titlepage.mode" dtm:id="confnum.titlepage-mode">
  <!-- suppress -->
</xsl:template>

<dtm:doc dtm:idref="contractnum.titlepage-mode"/>
<xsl:template match="contractnum" mode="titlepage.mode" dtm:id="contractnum.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="contractsponsor.titlepage-mode"/>
<xsl:template match="contractsponsor" mode="titlepage.mode" dtm:id="contractsponsor.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="contrib.titlepage-mode"/>
<xsl:template match="contrib" mode="titlepage.mode" dtm:id="contrib.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="copyright.titlepage-mode"/>
<xsl:template match="copyright" mode="titlepage.mode" dtm:id="copyright.titlepage-mode">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'copyright'"/>
  </xsl:call-template>
  <xsl:text> </xsl:text>
  <xsl:call-template name="dingbat">
    <xsl:with-param name="dingbat">copyright</xsl:with-param>
  </xsl:call-template>
  <xsl:text> </xsl:text>
  <xsl:call-template name="copyright.years">
    <xsl:with-param name="years" select="year"/>
    <xsl:with-param name="print.ranges" select="$make.year.ranges"/>
    <xsl:with-param name="single.year.ranges"
                    select="$make.single.year.ranges"/>
  </xsl:call-template>
  <xsl:text> </xsl:text>
  <xsl:apply-templates select="holder" mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="year.titlepage-mode"/>
<xsl:template match="year" mode="titlepage.mode" dtm:id="year.titlepage-mode">
  <fo:inline 
    border-left-width="0pt" 
    border-right-width="0pt"><xsl:apply-templates/></fo:inline>
</xsl:template>

<dtm:doc dtm:idref="holder.titlepage-mode"/>
<xsl:template match="holder" mode="titlepage.mode" dtm:id="holder.titlepage-mode">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="corpauthor.titlepage-mode"/>
<xsl:template match="corpauthor" mode="titlepage.mode" dtm:id="corpauthor.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="corpname.titlepage-mode"/>
<xsl:template match="corpname" mode="titlepage.mode" dtm:id="corpname.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="date.titlepage-mode"/>
<xsl:template match="date" mode="titlepage.mode" dtm:id="date.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="edition.titlepage-mode"/>
<xsl:template match="edition" mode="titlepage.mode" dtm:id="edition.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
  <xsl:text> </xsl:text>
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'edition'"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="editor.titlepage-mode"/>
<xsl:template match="editor" mode="titlepage.mode" dtm:id="editor.titlepage-mode">
  <xsl:call-template name="person.name"/>
</xsl:template>

<dtm:doc dtm:idref="editor[1].titlepage-mode"/>
<xsl:template match="editor[1]" priority="2" mode="titlepage.mode" dtm:id="editor[1].titlepage-mode">
  <xsl:text>TODO: edited by </xsl:text>
  <xsl:call-template name="person.name"/>
</xsl:template>

<dtm:doc dtm:idref="firstname.titlepage-mode"/>
<xsl:template match="firstname" mode="titlepage.mode" dtm:id="firstname.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="graphic.titlepage-mode"/>
<xsl:template match="graphic" mode="titlepage.mode" dtm:id="graphic.titlepage-mode">
  <!-- use the normal graphic handling code -->
  <xsl:apply-templates select="."/>
</xsl:template>

<dtm:doc dtm:idref="honorific.titlepage-mode"/>
<xsl:template match="honorific" mode="titlepage.mode" dtm:id="honorific.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="isbn.titlepage-mode"/>
<xsl:template match="isbn" mode="titlepage.mode" dtm:id="isbn.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="issn.titlepage-mode"/>
<xsl:template match="issn" mode="titlepage.mode" dtm:id="issn.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="biblioid.titlepage-mode"/>
<xsl:template match="biblioid" mode="titlepage.mode" dtm:id="biblioid.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="itermset.titlepage-mode"/>
<xsl:template match="itermset" mode="titlepage.mode" dtm:id="itermset.titlepage-mode">
  <!-- discard -->
</xsl:template>

<dtm:doc dtm:idref="invpartnumber.titlepage-mode"/>
<xsl:template match="invpartnumber" mode="titlepage.mode" dtm:id="invpartnumber.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="issuenum.titlepage-mode"/>
<xsl:template match="issuenum" mode="titlepage.mode" dtm:id="issuenum.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="jobtitle.titlepage-mode"/>
<xsl:template match="jobtitle" mode="titlepage.mode" dtm:id="jobtitle.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="keywordset.titlepage-mode"/>
<xsl:template match="keywordset" mode="titlepage.mode" dtm:id="keywordset.titlepage-mode">
</xsl:template>

<dtm:doc dtm:idref="legalnotice.titlepage-mode"/>
<xsl:template match="legalnotice" mode="titlepage.mode" dtm:id="legalnotice.titlepage-mode">
  <fo:block>
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
    <xsl:apply-templates select="*[local-name(.) != 'title']"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="legalnotice/title" dtm:idref="title.legalnotice.titlepage-mode title.legalnotice.titlepage-title-mode"/>
<xsl:template match="legalnotice/title" mode="titlepage.mode" dtm:id="title.legalnotice.titlepage-mode">
</xsl:template>

<xsl:template match="legalnotice/title" mode="titlepage.legalnotice.title.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="lineage.titlepage-mode"/>
<xsl:template match="lineage" mode="titlepage.mode" dtm:id="lineage.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="modespec.titlepage-mode"/>
<xsl:template match="modespec" mode="titlepage.mode" dtm:id="modespec.titlepage-mode">
  <!-- discard -->
</xsl:template>

<dtm:doc dtm:idref="orgdiv.titlepage-mode"/>
<xsl:template match="orgdiv" mode="titlepage.mode" dtm:id="orgdiv.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="orgname.titlepage-mode"/>
<xsl:template match="orgname" mode="titlepage.mode" dtm:id="orgname.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="othercredit.titlepage-mode"/>
<xsl:template match="othercredit" mode="titlepage.mode" dtm:id="othercredit.titlepage-mode">
  <xsl:variable name="contrib" select="string(contrib)"/>
  <xsl:choose>
    <xsl:when test="contrib">
      <xsl:if test="not(preceding-sibling::othercredit[string(contrib)=$contrib])">
        <fo:block>
          <xsl:apply-templates mode="titlepage.mode" select="contrib"/>
          <xsl:text>: </xsl:text>
          <xsl:call-template name="person.name"/>
          <xsl:apply-templates mode="titlepage.mode" select="affiliation"/>
          <xsl:apply-templates select="following-sibling::othercredit[string(contrib)=$contrib]" mode="titlepage.othercredits"/>
        </fo:block>
      </xsl:if>
    </xsl:when>
    <xsl:otherwise>
      <fo:block><xsl:call-template name="person.name"/></fo:block>
      <xsl:apply-templates mode="titlepage.mode" select="./affiliation"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="othercredit.titlepage-othercredits"/>
<xsl:template match="othercredit" mode="titlepage.othercredits" dtm:id="othercredit.titlepage-othercredits">
  <xsl:text>, </xsl:text>
  <xsl:call-template name="person.name"/>
</xsl:template>

<dtm:doc dtm:idref="othername.titlepage-mode"/>
<xsl:template match="othername" mode="titlepage.mode" dtm:id="othername.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="pagenums.titlepage-mode"/>
<xsl:template match="pagenums" mode="titlepage.mode" dtm:id="pagenums.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="printhistory.titlepage-mode"/>
<xsl:template match="printhistory" mode="titlepage.mode" dtm:id="printhistory.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="productname.titlepage-mode"/>
<xsl:template match="productname" mode="titlepage.mode" dtm:id="productname.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="productnumber.titlepage-mode"/>
<xsl:template match="productnumber" mode="titlepage.mode" dtm:id="productnumber.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="pubdate.titlepage-mode"/>
<xsl:template match="pubdate" mode="titlepage.mode" dtm:id="pubdate.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="publisher.titlepage-mode"/>
<xsl:template match="publisher" mode="titlepage.mode" dtm:id="publisher.titlepage-mode">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="publishername.titlepage-mode"/>
<xsl:template match="publishername" mode="titlepage.mode" dtm:id="publishername.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="pubsnumber.titlepage-mode"/>
<xsl:template match="pubsnumber" mode="titlepage.mode" dtm:id="pubsnumber.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="releaseinfo.titlepage-mode"/>
<xsl:template match="releaseinfo" mode="titlepage.mode" dtm:id="releaseinfo.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="revhistory.titlepage-mode"/>
<xsl:template match="revhistory" mode="titlepage.mode" dtm:id="revhistory.titlepage-mode">
  <fo:table table-layout="fixed">
    <fo:table-column column-number="1" column-width="33%"/>
    <fo:table-column column-number="2" column-width="33%"/>
    <fo:table-column column-number="3" column-width="33%"/>
    <fo:table-body>
      <fo:table-row>
        <fo:table-cell number-columns-spanned="3">
          <fo:block>
            <xsl:call-template name="gentext">
              <xsl:with-param name="key" select="'revhistory'"/>
            </xsl:call-template>
          </fo:block>
        </fo:table-cell>
      </fo:table-row>
      <xsl:apply-templates mode="titlepage.mode"/>
    </fo:table-body>
  </fo:table>
</xsl:template>

<dtm:doc dtm:idref="revision.revhistory.titlepage-mode"/>
<xsl:template match="revhistory/revision" mode="titlepage.mode" dtm:id="revision.revhistory.titlepage-mode">
  <xsl:variable name="revnumber" select=".//revnumber"/>
  <xsl:variable name="revdate"   select=".//date"/>
  <xsl:variable name="revauthor" select=".//authorinitials"/>
  <xsl:variable name="revremark" select=".//revremark|.//revdescription"/>
  <fo:table-row>
    <fo:table-cell>
      <fo:block>
        <xsl:if test="$revnumber">
          <xsl:call-template name="gentext">
            <xsl:with-param name="key" select="'revision'"/>
          </xsl:call-template>
          <xsl:text> </xsl:text>
          <xsl:apply-templates select="$revnumber[1]" mode="titlepage.mode"/>
        </xsl:if>
      </fo:block>
    </fo:table-cell>
    <fo:table-cell>
      <fo:block>
        <xsl:apply-templates select="$revdate[1]" mode="titlepage.mode"/>
      </fo:block>
    </fo:table-cell>
    <fo:table-cell>
      <fo:block>
        <xsl:apply-templates select="$revauthor[1]" mode="titlepage.mode"/>
      </fo:block>
    </fo:table-cell>
  </fo:table-row>
  <xsl:if test="$revremark">
    <fo:table-row>
      <fo:table-cell number-columns-spanned="3">
        <fo:block>
          <xsl:apply-templates select="$revremark[1]" mode="titlepage.mode"/>
        </fo:block>
      </fo:table-cell>
    </fo:table-row>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="revnumber.revision.titlepage-mode"/>
<xsl:template match="revision/revnumber" mode="titlepage.mode" dtm:id="revnumber.revision.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="date.revision.titlepage-mode"/>
<xsl:template match="revision/date" mode="titlepage.mode" dtm:id="date.revision.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="authorinitials.revision.titlepage-mode"/>
<xsl:template match="revision/authorinitials" mode="titlepage.mode" dtm:id="authorinitials.revision.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="revremark.revision.titlepage-mode"/>
<xsl:template match="revision/revremark" mode="titlepage.mode" dtm:id="revremark.revision.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="revdescription.revision.titlepage-mode"/>
<xsl:template match="revision/revdescription" mode="titlepage.mode" dtm:id="revdescription.revision.titlepage-mode">
  <fo:block text-align="left">
  <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="seriesvolnums.titlepage-mode"/>
<xsl:template match="seriesvolnums" mode="titlepage.mode" dtm:id="seriesvolnums.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="shortaffil.titlepage-mode"/>
<xsl:template match="shortaffil" mode="titlepage.mode" dtm:id="shortaffil.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="subjectset.titlepage-mode"/>
<xsl:template match="subjectset" mode="titlepage.mode" dtm:id="subjectset.titlepage-mode">
  <!-- discard -->
</xsl:template>

<dtm:doc dtm:idref="subtitle.titlepage-mode"/>
<xsl:template match="subtitle" mode="titlepage.mode" dtm:id="subtitle.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="surname.titlepage-mode"/>
<xsl:template match="surname" mode="titlepage.mode" dtm:id="surname.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="title.titlepage-mode"/>
<xsl:template match="title" mode="titlepage.mode" dtm:id="title.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="titleabbrev.titlepage-mode"/>
<xsl:template match="titleabbrev" mode="titlepage.mode" dtm:id="titleabbrev.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<dtm:doc dtm:idref="volumenum.titlepage-mode"/>
<xsl:template match="volumenum" mode="titlepage.mode" dtm:id="volumenum.titlepage-mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<!-- ==================================================================== -->
<!-- Book templates -->

<!-- Note: these templates cannot use *.titlepage.recto.mode or
     *.titlepage.verso.mode. If they do then subsequent use of a custom
     titlepage.templates.xml file will not work correctly. -->

<!-- book recto -->
<dtm:doc dtm:idref="authorgroup.bookinfo.titlepage-mode"/>
<xsl:template match="bookinfo/authorgroup" mode="titlepage.mode" priority="2" dtm:id="authorgroup.bookinfo.titlepage-mode">
  <fo:block>
    <xsl:if test="@id">
      <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
    </xsl:if>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'by'"/>
    </xsl:call-template>
    <xsl:text> </xsl:text>
    <xsl:call-template name="person.name.list"/>
  </fo:block>
</xsl:template>

<!-- book verso -->
<dtm:doc dtm:idref="book.verso.title"/>
<xsl:template name="book.verso.title" dtm:id="book.verso.title">
  <fo:block>
    <xsl:apply-templates mode="titlepage.mode"/>

    <xsl:if test="following-sibling::subtitle
                  |following-sibling::bookinfo/subtitle">
      <xsl:text>: </xsl:text>

      <xsl:apply-templates select="(following-sibling::subtitle
                                   |following-sibling::bookinfo/subtitle)[1]"
                           mode="book.verso.subtitle.mode"/>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="subtitle.book.verso.mode"/>
<xsl:template match="subtitle" mode="book.verso.subtitle.mode" dtm:id="subtitle.book.verso.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
  <xsl:if test="following-sibling::subtitle">
    <xsl:text>: </xsl:text>
    <xsl:apply-templates select="following-sibling::subtitle[1]"
                         mode="book.verso.subtitle.mode"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="verso.authorgroup"/>
<xsl:template name="verso.authorgroup" dtm:id="verso.authorgroup">
  <fo:block>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'by'"/>
    </xsl:call-template>
    <xsl:text> </xsl:text>
    <xsl:call-template name="person.name.list"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="author.bookinfo.titlepage-mode"/>
<xsl:template match="bookinfo/author" mode="titlepage.mode" priority="2" dtm:id="author.bookinfo.titlepage-mode">
  <fo:block>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'by'"/>
    </xsl:call-template>
    <xsl:text> </xsl:text>
    <xsl:call-template name="person.name"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="corpauthor.bookinfo.titlepage-mode"/>
<xsl:template match="bookinfo/corpauthor" mode="titlepage.mode" priority="2" dtm:id="corpauthor.bookinfo.titlepage-mode">
  <fo:block>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'by'"/>
    </xsl:call-template>
    <xsl:text> </xsl:text>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="pubdate.bookinfo.titlepage-mode"/>
<xsl:template match="bookinfo/pubdate" mode="titlepage.mode" priority="2" dtm:id="pubdate.bookinfo.titlepage-mode">
  <fo:block>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'published'"/>
    </xsl:call-template>
    <xsl:text> </xsl:text>
    <xsl:apply-templates mode="titlepage.mode"/>
  </fo:block>
</xsl:template>

<!-- ==================================================================== -->

</xsl:stylesheet>
