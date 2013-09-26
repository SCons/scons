<?xml version="1.0" encoding="utf-8"?><ax:stylesheet xmlns:ax="http://www.w3.org/1999/XSL/Transform" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:se="http://syntext.com/XSL/Format-1.0" version="1.0">

<!-- This stylesheet was created by template/titlepage.xsl; do not edit it by hand. -->

<xsl:template name="article.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="articleinfo/title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="artheader/title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="articleinfo/subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="artheader/subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block text-align="center"><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="article.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="article.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block font-family="{$title.font.family}">
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="article" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="article.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="article.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="article.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" font-size="{$title1.font.size}" font-weight="bold">
<xsl:apply-templates mode="article.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em" font-size="{$title3.font.size}">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em" font-size="{$title3.font.size}">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em" font-size="{$title3.font.size}">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" text-align="start" margin-left="0.5in" margin-right="0.5in" font-family="{$body.font.family}">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em">
<xsl:apply-templates mode="rev.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="article.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="article.titlepage.recto.style" padding-bottom="0.5em" text-align="start" margin-left="0.5in" margin-right="0.5in" font-family="{$body.font.family}">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="chapter.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="chapterinfo/title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="chapterinfo/subtitle">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block margin-left="{$title.margin.left}"><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="chapter.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="chapter.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block font-family="{$title.font.family}">
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="chapter" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="chapter.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="chapter.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="chapter.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style" font-size="{$title1.font.size}" font-weight="bold">
<xsl:apply-templates mode="chapter.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style" padding-bottom="0.5em" font-style="italic" font-size="{$title3.font.size}" font-weight="bold">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style" padding-bottom="0.5em" space-after="0.5em" font-size="{$title3.font.size}">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style" padding-bottom="0.5em" space-after="0.5em" font-size="{$title3.font.size}">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style" padding-bottom="0.5em" space-after="0.5em" font-size="{$title3.font.size}">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="chapter.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="book.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="bookinfo/title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="bookinfo/subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/author[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="book.titlepage.verso">
   <ax:variable name="result">
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="book.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="book.titlepage.recto"/>
    
   
    <xsl:call-template name="book.titlepage.verso"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="book" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="book.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="book.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="book.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="book.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.recto.style" text-align="center" font-size="{$title1.font.size}" padding-bottom="18.6624pt" font-weight="bold" font-family="{$title.font.family}">
<xsl:apply-templates mode="book.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="book.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.recto.style" text-align="center" font-size="{$title2.font.size}" padding-bottom="12.96pt" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="book.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.recto.style" font-size="{title2.font.size}" keep-with-next="always" padding-bottom="1in">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="book.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.recto.style" padding-bottom="1in">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="book.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.recto.style" font-size="{title2.font.size}" padding-bottom="10.8pt" keep-with-next="always">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style" padding-bottom="2em">
<xsl:call-template name="verso.authorgroup">
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style" padding-bottom="1em">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style" padding-bottom="0.5em">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style" padding-bottom="0.5em">
<xsl:apply-templates mode="rev.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="book.titlepage.verso.auto.mode">
<fo:block xsl:use-attribute-sets="book.titlepage.verso.style" font-size="8pt">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="part.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="partinfo/title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="partinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="partinfo/subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="partinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="part.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="part.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="part" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="part.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="part.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="part.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="part.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="part.titlepage.recto.style" text-align="center" font-size="{$title1.font.size}" padding-bottom="18.6624pt" font-weight="bold" font-family="{$title.font.family}">
<xsl:apply-templates mode="part.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="part.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="part.titlepage.recto.style" text-align="center" font-size="{$title2.font.size}" padding-bottom="15.552pt" font-weight="bold" font-style="italic" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="part.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="preface.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="prefaceinfo/title">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="prefaceinfo/subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="preface.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="preface.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="preface" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="preface.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="preface.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="preface.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="{$title1.font.size}" font-family="{$title.font.family}" font-weight="bold">
<xsl:apply-templates mode="preface.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="preface.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="partintro.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="partintroinfo/title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="partintroinfo/subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="partintro.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="partintro.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="partintro" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="partintro.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="partintro.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="partintro.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style" text-align="center" font-size="{$title1.font.size}" font-weight="bold" padding-bottom="1em" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style" text-align="center" font-size="{$title3.font.size}" font-weight="bold" font-style="italic" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="partintro.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="reference.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="referenceinfo/title">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="referenceinfo/subtitle">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="reference.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="reference.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="reference" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="reference.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="reference.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="reference.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="reference.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="reference.titlepage.recto.style" text-align="center" font-size="{$title1.font.size}" padding-bottom="18.6624pt" font-weight="bold" font-family="{$title.font.family}">
<xsl:apply-templates mode="reference.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="reference.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="reference.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="refsynopsisdivinfo/title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="refsynopsisdivinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="refsynopsisdiv.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="refsynopsisdiv.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="refsynopsisdiv" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="refsynopsisdiv.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="refsynopsisdiv.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="refsynopsisdiv.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="refsynopsisdiv.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="refsynopsisdiv.titlepage.recto.style" font-weight="bold" margin-left="{$title.margin.left}" font-family="{$title.font.family}">
<xsl:apply-templates mode="refsynopsisdiv.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template name="refsection.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="refsectioninfo/title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="refsectioninfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="refsection.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="refsection.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="refsection" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="refsection.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="refsection.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="refsection.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="refsection.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="refsection.titlepage.recto.style" font-weight="bold" font-family="{$title.font.family}">
<xsl:apply-templates mode="section.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template name="section.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="sectioninfo/title">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sectioninfo/subtitle">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="section.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="section.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="section" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="section.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="section.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="section.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style" font-weight="bold" margin-left="{$title.margin.left}" font-family="{$title.font.family}">
<xsl:apply-templates mode="section.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="section.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="simplesect.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="simplesectinfo/title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="simplesectinfo/subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="simplesect.titlepage.verso">
   <ax:variable name="result"/>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="simplesect.titlepage.separator">
</xsl:template>

<xsl:template name="simplesect.titlepage.before.recto">
</xsl:template>

<xsl:template name="simplesect.titlepage.before.verso">
</xsl:template>

<xsl:template name="simplesect.titlepage">
  <ax:variable name="result"><xsl:call-template name="simplesect.titlepage.before.recto"/>
    <xsl:call-template name="simplesect.titlepage.recto"/>
    
   <xsl:call-template name="simplesect.titlepage.before.verso"/>
    <xsl:call-template name="simplesect.titlepage.verso"/>
    
    <xsl:call-template name="simplesect.titlepage.separator"/>
  </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="simplesect" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="simplesect.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="simplesect.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="simplesect.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style" font-weight="bold" margin-left="{$title.margin.left}" font-family="{$title.font.family}">
<xsl:apply-templates mode="simplesect.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="set.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="setinfo/title">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="setinfo/subtitle">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="set.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="set.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="set" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="set.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="set.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="set.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style" text-align="center" font-size="{$title1.font.size}" padding-bottom="18.6624pt" font-weight="bold" font-family="{$title.font.family}">
<xsl:apply-templates mode="set.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style" font-family="{$title.font.family}" text-align="center">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="set.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="appendix.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="appendixinfo/title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="appendixinfo/subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/corpauthor[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/authorgroup[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/author[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/othercredit[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/releaseinfo[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/copyright[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/legalnotice[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/pubdate[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/revision[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/revhistory[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/abstract[not(self::processing-instruction('se:choice'))]"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/abstract[not(self::processing-instruction('se:choice'))]"/></ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="appendix.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="appendix.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="appendix" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="appendix.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="appendix.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="appendix.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="{$title1.font.size}" font-weight="bold" font-family="{$title.font.family}">
<xsl:apply-templates mode="appendix.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="appendix.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="bibliography.titlepage.recto">
   <ax:variable name="result">
  <fo:block xsl:use-attribute-sets="bibliography.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="{$title1.font.size}" font-family="{$title.font.family}" font-weight="bold">
<xsl:call-template name="bibliography.title">
<xsl:with-param name="node" select="."/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="bibliographyinfo/subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="bibliographyinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="bibliography.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="bibliography.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="bibliography" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="bibliography.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="bibliography.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="bibliography.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="subtitle" mode="bibliography.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="bibliography.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="bibliography.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="bibliodiv.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="bibliodivinfo/title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="bibliodivinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="bibliodivinfo/subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="bibliodivinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="bibliodiv.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="bibliodiv.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="bibliodiv" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="bibliodiv.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="bibliodiv.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="bibliodiv.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="bibliodiv.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="bibliodiv.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="{$title2.font.size}" font-family="{$title.font.family}" font-weight="bold">
<xsl:apply-templates mode="bibliodiv.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="bibliodiv.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="bibliodiv.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="bibliodiv.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="glossary.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="glossaryinfo/title">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="glossaryinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="glossaryinfo/subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="glossaryinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="glossary.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="glossary.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="glossary" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="glossary.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="glossary.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="glossary.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="glossary.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="glossary.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="{$title1.font.size}" font-family="{$title.font.family}" font-weight="bold">
<xsl:apply-templates mode="glossary.title" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="glossary.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="glossary.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="glossary.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="glossdiv.titlepage.recto">
   <ax:variable name="result">
  <xsl:choose>
    <xsl:when test="glossdivinfo/title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="glossdivinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="docinfo/title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="title[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="glossdivinfo/subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="glossdivinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="docinfo/subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="subtitle[not(self::processing-instruction('se:choice'))]"/>
    </xsl:when>
  </xsl:choose>
</ax:variable>

   <ax:if test="string-length($result)">
   <fo:block><ax:copy-of select="$result"/>
   </fo:block>
  </ax:if>
    </xsl:template>

<xsl:template name="glossdiv.titlepage">
  <ax:variable name="result">
    <xsl:call-template name="glossdiv.titlepage.recto"/>
    
    </ax:variable><ax:if test="string-length($result)"><fo:block>
    <ax:copy-of select="$result"/></fo:block></ax:if>
</xsl:template>

<xsl:template match="glossdiv" mode="serna.fold">
  <fo:block se:fold="" color="gray">
    <se:fold show-element-name="false"/><xsl:apply-templates select="title" mode="glossdiv.titlepage.recto.auto.mode"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="glossdiv.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="glossdiv.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="glossdiv.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="glossdiv.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="{$title2.font.size}" font-family="{$title.font.family}" font-weight="bold">
<xsl:apply-templates mode="glossdiv.titles.mode" select=".">
</xsl:apply-templates>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="glossdiv.titlepage.recto.auto.mode">
<fo:block xsl:use-attribute-sets="glossdiv.titlepage.recto.style" font-family="{$title.font.family}">
<xsl:apply-templates select="." mode="glossdiv.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

</ax:stylesheet>