<?xml version="1.0"?>
<!--

  __COPYRIGHT__

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns:exsl="http://exslt.org/common"
		xmlns:fo="http://www.w3.org/1999/XSL/Format" 
	        version="1.0" exclude-result-prefixes="exsl">

<!-- This stylesheet was created by template/titlepage.xsl; do not edit it by hand. -->

<xsl:template name="article.titlepage.recto">
  <xsl:choose>
    <xsl:when test="articleinfo/title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/title"/>
    </xsl:when>
    <xsl:when test="artheader/title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="articleinfo/subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="artheader/subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="articleinfo/mediaobject"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="artheader/mediaobject"/>
  <xsl:apply-templates mode="article.titlepage.recto.auto.mode" select="info/mediaobject"/>
</xsl:template>

<xsl:template name="article.titlepage.verso">
</xsl:template>

<xsl:template name="article.titlepage.separator">
</xsl:template>

<xsl:template name="article.titlepage.before.recto">
</xsl:template>

<xsl:template name="article.titlepage.before.verso">
</xsl:template>

<xsl:template name="article.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" font-family="{$title.fontset}">
    <xsl:variable name="recto.content">
      <xsl:call-template name="article.titlepage.before.recto"/>
      <xsl:call-template name="article.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block start-indent="0pt" text-align="center"><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="article.titlepage.before.verso"/>
      <xsl:call-template name="article.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="article.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="article.titlepage.recto.style" keep-with-next.within-column="always" font-size="24.8832pt" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::article[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="article.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="article.titlepage.recto.style">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="mediaobject" mode="article.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="article.titlepage.recto.style">
<xsl:apply-templates select="." mode="article.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="set.titlepage.recto">
  <xsl:choose>
    <xsl:when test="setinfo/title">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="setinfo/subtitle">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/corpauthor"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/authorgroup"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/author"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/othercredit"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/releaseinfo"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/copyright"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/legalnotice"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/pubdate"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/revision"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/revhistory"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="setinfo/abstract"/>
  <xsl:apply-templates mode="set.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="set.titlepage.verso">
</xsl:template>

<xsl:template name="set.titlepage.separator">
</xsl:template>

<xsl:template name="set.titlepage.before.recto">
</xsl:template>

<xsl:template name="set.titlepage.before.verso">
</xsl:template>

<xsl:template name="set.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="set.titlepage.before.recto"/>
      <xsl:call-template name="set.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="set.titlepage.before.verso"/>
      <xsl:call-template name="set.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="set.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style" text-align="center" font-size="24.8832pt" space-before="18.6624pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="division.title">
<xsl:with-param name="node" select="ancestor-or-self::set[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style" font-family="{$title.fontset}" text-align="center">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="set.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="set.titlepage.recto.style">
<xsl:apply-templates select="." mode="set.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:param name="scons.inner.twidtha">
  <xsl:choose>
    <xsl:when test="$paper.type = 'A4'">200mm</xsl:when>
    <xsl:otherwise>205.9mm</xsl:otherwise> <!-- 8.5in-10mm -->
  </xsl:choose>
</xsl:param>
<xsl:param name="scons.inner.twidthb">
  <xsl:choose>
    <xsl:when test="$paper.type = 'A4'">190mm</xsl:when>
    <xsl:otherwise>195.9mm</xsl:otherwise> <!-- 8.5in-20mm -->
  </xsl:choose>
</xsl:param>
<xsl:param name="scons.inner.twidthc">
  <xsl:choose>
    <xsl:when test="$paper.type = 'A4'">180mm</xsl:when>
    <xsl:otherwise>185.9mm</xsl:otherwise> <!-- 8.5in-30mm -->
  </xsl:choose>
</xsl:param>

<xsl:template name="book.titlepage.recto">

	<fo:block-container height="3mm">
		<fo:block></fo:block>
	</fo:block-container>
	<fo:block>
    <fo:table table-layout="fixed" width="100%" padding="0pt" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidtha}"/>
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
           <fo:table-cell text-align="center">
	     <fo:block line-height="0">
		 <fo:external-graphic
       src="url(titlepage/SConsBuildBricks_path.svg)"
       width="{$scons.inner.twidtha}" content-width="scale-to-fit"
       scaling="uniform"/>
	     </fo:block></fo:table-cell>
        </fo:table-row>
      </fo:table-body>
   </fo:table>
 </fo:block>


	<fo:block-container height="4cm">
		<fo:block></fo:block>
	</fo:block-container>
	
<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
	    
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
  <xsl:choose>
    <xsl:when test="bookinfo/title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:block><fo:inline> </fo:inline></fo:block>
    </xsl:otherwise>
  </xsl:choose>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>

<!--
	<fo:block-container height="6mm">
		<fo:block></fo:block>
	</fo:block-container>
-->

  <xsl:choose>
    <xsl:when test="bookinfo/edition">
<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
	    
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/edition"/>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>

	<fo:block-container height="9mm">
		<fo:block></fo:block>
	</fo:block-container>
    </xsl:when>
    <xsl:otherwise>
	<fo:block-container height="6mm">
		<fo:block></fo:block>
	</fo:block-container>
    </xsl:otherwise>
  </xsl:choose>


<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
	    
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
  <xsl:choose>
    <xsl:when test="bookinfo/subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:block><fo:inline> </fo:inline></fo:block>
    </xsl:otherwise>
  </xsl:choose>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>


  <xsl:choose>
    <xsl:when test="bookinfo/corpauthor">
	<fo:block-container height="15mm">
		<fo:block></fo:block>
	</fo:block-container>
<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
	    
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/corpauthor"/>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>

	<fo:block-container height="9mm">
		<fo:block></fo:block>
	</fo:block-container>

  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/mediaobject"/>
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="info/mediaobject"/>
</xsl:template>

<xsl:template name="book.titlepage.verso">
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/releaseinfo"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/copyright"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/pubdate"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/revision"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="book.titlepage.verso.auto.mode" select="bookinfo/legalnotice"/>
</xsl:template>

<xsl:template name="book.titlepage.separator">
</xsl:template>

<xsl:template name="book.titlepage.before.recto">
</xsl:template>

<xsl:template name="book.titlepage.before.verso"><fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" break-after="page"/>
</xsl:template>

<xsl:template name="book.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="book.titlepage.before.recto"/>
      <xsl:call-template name="book.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="book.titlepage.before.verso"/>
      <xsl:call-template name="book.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="book.titlepage.separator"/>
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

<!--
<xsl:template match="title" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" text-align="center" font-size="24pt" space-before="18pt" font-weight="bold" font-family="'serif'">
<xsl:call-template name="division.title">
<xsl:with-param name="node" select="ancestor-or-self::book[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" text-align="left" font-size="20pt" space-before="15pt" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>
-->
<xsl:template match="corpauthor" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" text-align="left" font-size="20pt" space-before="0pt" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="mediaobject" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="book.titlepage.verso.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="book.titlepage.verso.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="book.titlepage.verso.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="book.titlepage.verso.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.verso.style">
<xsl:apply-templates select="." mode="book.titlepage.verso.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="part.titlepage.recto">
  <xsl:choose>
    <xsl:when test="partinfo/title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="partinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="partinfo/subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="partinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="part.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="part.titlepage.verso">
</xsl:template>

<xsl:template name="part.titlepage.separator">
</xsl:template>

<xsl:template name="part.titlepage.before.recto">
</xsl:template>

<xsl:template name="part.titlepage.before.verso">
</xsl:template>

<xsl:template name="part.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="part.titlepage.before.recto"/>
      <xsl:call-template name="part.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="part.titlepage.before.verso"/>
      <xsl:call-template name="part.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="part.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="part.titlepage.recto.style" text-align="center" font-size="24.8832pt" space-before="18.6624pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="division.title">
<xsl:with-param name="node" select="ancestor-or-self::part[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="part.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="part.titlepage.recto.style" text-align="center" font-size="20.736pt" space-before="15.552pt" font-weight="bold" font-style="italic" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="part.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="partintro.titlepage.recto">
  <xsl:choose>
    <xsl:when test="partintroinfo/title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="partintroinfo/subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/corpauthor"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/corpauthor"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/authorgroup"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/authorgroup"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/author"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/author"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/othercredit"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/othercredit"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/releaseinfo"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/releaseinfo"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/copyright"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/copyright"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/legalnotice"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/legalnotice"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/pubdate"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/pubdate"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/revision"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/revision"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/revhistory"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/revhistory"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="partintroinfo/abstract"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="docinfo/abstract"/>
  <xsl:apply-templates mode="partintro.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="partintro.titlepage.verso">
</xsl:template>

<xsl:template name="partintro.titlepage.separator">
</xsl:template>

<xsl:template name="partintro.titlepage.before.recto">
</xsl:template>

<xsl:template name="partintro.titlepage.before.verso">
</xsl:template>

<xsl:template name="partintro.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="partintro.titlepage.before.recto"/>
      <xsl:call-template name="partintro.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="partintro.titlepage.before.verso"/>
      <xsl:call-template name="partintro.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="partintro.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style" text-align="center" font-size="24.8832pt" font-weight="bold" space-before="1em" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style" text-align="center" font-size="14.4pt" font-weight="bold" font-style="italic" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="partintro.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="partintro.titlepage.recto.style">
<xsl:apply-templates select="." mode="partintro.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="reference.titlepage.recto">


    <fo:block-container height="3mm">
        <fo:block></fo:block>
    </fo:block-container>
    <fo:block>
    <fo:table table-layout="fixed" width="100%" padding="0pt" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidtha}"/>
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
           <fo:table-cell text-align="center">
         <fo:block line-height="0">
         <fo:external-graphic
       src="url(titlepage/SConsBuildBricks_path.svg)"
       width="{$scons.inner.twidtha}" content-width="scale-to-fit"
       scaling="uniform"/>
         </fo:block></fo:table-cell>
        </fo:table-row>
      </fo:table-body>
   </fo:table>
 </fo:block>


    <fo:block-container height="4cm">
        <fo:block></fo:block>
    </fo:block-container>
    
<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
        
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
  <xsl:choose>
    <xsl:when test="referenceinfo/title">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:block><fo:inline> </fo:inline></fo:block>
    </xsl:otherwise>
  </xsl:choose>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>

<!--
    <fo:block-container height="6mm">
        <fo:block></fo:block>
    </fo:block-container>
-->

  <xsl:choose>
    <xsl:when test="referenceinfo/edition">
<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
        
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/edition"/>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>

    <fo:block-container height="9mm">
        <fo:block></fo:block>
    </fo:block-container>
    </xsl:when>
    <xsl:otherwise>
    <fo:block-container height="6mm">
        <fo:block></fo:block>
    </fo:block-container>
    </xsl:otherwise>
  </xsl:choose>


<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
        
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
  <xsl:choose>
    <xsl:when test="referenceinfo/subtitle">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:block><fo:inline> </fo:inline></fo:block>
    </xsl:otherwise>
  </xsl:choose>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>


  <xsl:choose>
    <xsl:when test="referenceinfo/corpauthor">
    <fo:block-container height="15mm">
        <fo:block></fo:block>
    </fo:block-container>
<fo:block>
    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="10mm"/>
      <fo:table-column column-width="{$scons.inner.twidthc}"/>
      <fo:table-column column-width="20mm"/>
        
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
         <fo:table-cell text-align="left" display-align="after">
      <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/corpauthor"/>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
 </fo:table-body>
 </fo:table>
 </fo:block>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>

    <fo:block-container height="9mm">
        <fo:block></fo:block>
    </fo:block-container>

  <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="referenceinfo/mediaobject"/>
  <xsl:apply-templates mode="reference.titlepage.recto.auto.mode" select="info/mediaobject"/>

</xsl:template>

<xsl:template name="reference.titlepage.verso">
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="referenceinfo/releaseinfo"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="referenceinfo/copyright"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="referenceinfo/pubdate"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="referenceinfo/revision"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="reference.titlepage.verso.auto.mode" select="referenceinfo/legalnotice"/>
</xsl:template>

<xsl:template name="reference.titlepage.separator">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" break-after="page"/>
</xsl:template>

<xsl:template name="reference.titlepage.before.recto">
</xsl:template>

<xsl:template name="reference.titlepage.before.verso">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" break-after="page"/>
</xsl:template>

<xsl:template name="reference.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="reference.titlepage.before.recto"/>
      <xsl:call-template name="reference.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="reference.titlepage.before.verso"/>
      <xsl:call-template name="reference.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="reference.titlepage.separator"/>
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

<!--
<xsl:template match="title" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style" text-align="center" font-size="24.8832pt" space-before="18.6624pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="division.title">
<xsl:with-param name="node" select="."/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style" font-family="{$title.fontset}" text-align="center">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>
-->

<xsl:template match="corpauthor" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style" text-align="left" font-size="20pt" space-before="0pt" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage.recto">
  <xsl:choose>
    <xsl:when test="refsynopsisdivinfo/title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="refsynopsisdivinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsynopsisdiv.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage.verso">
</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage.separator">
</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage.before.recto">
</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage.before.verso">
</xsl:template>

<xsl:template name="refsynopsisdiv.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="refsynopsisdiv.titlepage.before.recto"/>
      <xsl:call-template name="refsynopsisdiv.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="refsynopsisdiv.titlepage.before.verso"/>
      <xsl:call-template name="refsynopsisdiv.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="refsynopsisdiv.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="refsynopsisdiv.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="refsynopsisdiv.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="refsection.titlepage.recto">
  <xsl:choose>
    <xsl:when test="refsectioninfo/title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="refsectioninfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsection.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="refsection.titlepage.verso">
</xsl:template>

<xsl:template name="refsection.titlepage.separator">
</xsl:template>

<xsl:template name="refsection.titlepage.before.recto">
</xsl:template>

<xsl:template name="refsection.titlepage.before.verso">
</xsl:template>

<xsl:template name="refsection.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="refsection.titlepage.before.recto"/>
      <xsl:call-template name="refsection.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="refsection.titlepage.before.verso"/>
      <xsl:call-template name="refsection.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="refsection.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="refsection.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="refsection.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="refsect1.titlepage.recto">
  <xsl:choose>
    <xsl:when test="refsect1info/title">
      <xsl:apply-templates mode="refsect1.titlepage.recto.auto.mode" select="refsect1info/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsect1.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="refsect1.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsect1.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="refsect1.titlepage.verso">
</xsl:template>

<xsl:template name="refsect1.titlepage.separator">
</xsl:template>

<xsl:template name="refsect1.titlepage.before.recto">
</xsl:template>

<xsl:template name="refsect1.titlepage.before.verso">
</xsl:template>

<xsl:template name="refsect1.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="refsect1.titlepage.before.recto"/>
      <xsl:call-template name="refsect1.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="refsect1.titlepage.before.verso"/>
      <xsl:call-template name="refsect1.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="refsect1.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="refsect1.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="refsect1.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="refsect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="refsect1.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="refsect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="refsect2.titlepage.recto">
  <xsl:choose>
    <xsl:when test="refsect2info/title">
      <xsl:apply-templates mode="refsect2.titlepage.recto.auto.mode" select="refsect2info/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsect2.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="refsect2.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsect2.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="refsect2.titlepage.verso">
</xsl:template>

<xsl:template name="refsect2.titlepage.separator">
</xsl:template>

<xsl:template name="refsect2.titlepage.before.recto">
</xsl:template>

<xsl:template name="refsect2.titlepage.before.verso">
</xsl:template>

<xsl:template name="refsect2.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="refsect2.titlepage.before.recto"/>
      <xsl:call-template name="refsect2.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="refsect2.titlepage.before.verso"/>
      <xsl:call-template name="refsect2.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="refsect2.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="refsect2.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="refsect2.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="refsect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="refsect2.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="refsect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="refsect3.titlepage.recto">
  <xsl:choose>
    <xsl:when test="refsect3info/title">
      <xsl:apply-templates mode="refsect3.titlepage.recto.auto.mode" select="refsect3info/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="refsect3.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="refsect3.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="refsect3.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="refsect3.titlepage.verso">
</xsl:template>

<xsl:template name="refsect3.titlepage.separator">
</xsl:template>

<xsl:template name="refsect3.titlepage.before.recto">
</xsl:template>

<xsl:template name="refsect3.titlepage.before.verso">
</xsl:template>

<xsl:template name="refsect3.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="refsect3.titlepage.before.recto"/>
      <xsl:call-template name="refsect3.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="refsect3.titlepage.before.verso"/>
      <xsl:call-template name="refsect3.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="refsect3.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="refsect3.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="refsect3.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="refsect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="refsect3.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="refsect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="dedication.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="dedication.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::dedication[1]"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="dedicationinfo/subtitle">
      <xsl:apply-templates mode="dedication.titlepage.recto.auto.mode" select="dedicationinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="dedication.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="dedication.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="dedication.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="dedication.titlepage.verso">
</xsl:template>

<xsl:template name="dedication.titlepage.separator">
</xsl:template>

<xsl:template name="dedication.titlepage.before.recto">
</xsl:template>

<xsl:template name="dedication.titlepage.before.verso">
</xsl:template>

<xsl:template name="dedication.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="dedication.titlepage.before.recto"/>
      <xsl:call-template name="dedication.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="dedication.titlepage.before.verso"/>
      <xsl:call-template name="dedication.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="dedication.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="dedication.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="dedication.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="subtitle" mode="dedication.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="dedication.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="dedication.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="preface.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::preface[1]"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="prefaceinfo/subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/corpauthor"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/corpauthor"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/authorgroup"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/authorgroup"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/author"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/author"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/othercredit"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/othercredit"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/releaseinfo"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/releaseinfo"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/copyright"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/copyright"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/legalnotice"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/legalnotice"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/pubdate"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/pubdate"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/revision"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/revision"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/revhistory"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/revhistory"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="prefaceinfo/abstract"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="docinfo/abstract"/>
  <xsl:apply-templates mode="preface.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="preface.titlepage.verso">
</xsl:template>

<xsl:template name="preface.titlepage.separator">
</xsl:template>

<xsl:template name="preface.titlepage.before.recto">
</xsl:template>

<xsl:template name="preface.titlepage.before.verso">
</xsl:template>

<xsl:template name="preface.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="preface.titlepage.before.recto"/>
      <xsl:call-template name="preface.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="preface.titlepage.before.verso"/>
      <xsl:call-template name="preface.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="preface.titlepage.separator"/>
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

<xsl:template match="subtitle" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="preface.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="preface.titlepage.recto.style">
<xsl:apply-templates select="." mode="preface.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="chapter.titlepage.recto">

	<fo:block-container height="1cm">
		<fo:block></fo:block>
	</fo:block-container>

<fo:block text-align="center">
  <fo:leader leader-length="85%" leader-pattern="rule" rule-style="solid" rule-thickness="1pt" color="#C51410"/>
</fo:block>

	<fo:block-container height="0.7cm">
		<fo:block></fo:block>
	</fo:block-container>

  <xsl:choose>
    <xsl:when test="chapterinfo/title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="chapterinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="chapter.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>


	<fo:block-container height="0.7cm">
		<fo:block></fo:block>
	</fo:block-container>


<fo:block text-align="center">
  <fo:leader leader-length="85%" leader-pattern="rule" rule-style="solid" rule-thickness="1pt" color="#C51410"/>
</fo:block>

	<fo:block-container height="1cm">
		<fo:block></fo:block>
	</fo:block-container>

</xsl:template>

<xsl:template name="chapter.titlepage.verso">
</xsl:template>

<xsl:template name="chapter.titlepage.separator">
<!--
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" break-after="page"/>
-->
</xsl:template>

<xsl:template name="chapter.titlepage.before.recto">
</xsl:template>

<xsl:template name="chapter.titlepage.before.verso">
</xsl:template>

<xsl:template name="chapter.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" font-family="{$title.fontset}">
    <xsl:variable name="recto.content">
      <xsl:call-template name="chapter.titlepage.before.recto"/>
      <xsl:call-template name="chapter.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block margin-left="{$title.margin.left}"><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="chapter.titlepage.before.verso"/>
      <xsl:call-template name="chapter.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="chapter.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style" font-size="24.8832pt" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::chapter[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style" space-before="0.5em" font-style="italic" font-size="14.4pt" font-weight="bold">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style" space-before="0.5em" space-after="0.5em" font-size="14.4pt">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style" space-before="0.5em" space-after="0.5em" font-size="14.4pt">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style" space-before="0.5em" space-after="0.5em" font-size="14.4pt">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="chapter.titlepage.recto.style">
<xsl:apply-templates select="." mode="chapter.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="appendix.titlepage.recto">
  <xsl:choose>
    <xsl:when test="appendixinfo/title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="appendixinfo/subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/corpauthor"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/corpauthor"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/authorgroup"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/authorgroup"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/author"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/author"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/othercredit"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/othercredit"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/releaseinfo"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/releaseinfo"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/copyright"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/copyright"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/legalnotice"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/legalnotice"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/pubdate"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/pubdate"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/revision"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/revision"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/revhistory"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/revhistory"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="appendixinfo/abstract"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="docinfo/abstract"/>
  <xsl:apply-templates mode="appendix.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="appendix.titlepage.verso">
</xsl:template>

<xsl:template name="appendix.titlepage.separator">
</xsl:template>

<xsl:template name="appendix.titlepage.before.recto">
</xsl:template>

<xsl:template name="appendix.titlepage.before.verso">
</xsl:template>

<xsl:template name="appendix.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="appendix.titlepage.before.recto"/>
      <xsl:call-template name="appendix.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="appendix.titlepage.before.verso"/>
      <xsl:call-template name="appendix.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="appendix.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="24.8832pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::appendix[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="appendix.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="appendix.titlepage.recto.style">
<xsl:apply-templates select="." mode="appendix.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="section.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sectioninfo/title">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sectioninfo/subtitle">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/corpauthor"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/authorgroup"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/author"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/othercredit"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/releaseinfo"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/copyright"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/legalnotice"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/pubdate"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/revision"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/revhistory"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="sectioninfo/abstract"/>
  <xsl:apply-templates mode="section.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="section.titlepage.verso">
</xsl:template>

<xsl:template name="section.titlepage.separator">
</xsl:template>

<xsl:template name="section.titlepage.before.recto">
</xsl:template>

<xsl:template name="section.titlepage.before.verso">
</xsl:template>

<xsl:template name="section.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="section.titlepage.before.recto"/>
      <xsl:call-template name="section.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="section.titlepage.before.verso"/>
      <xsl:call-template name="section.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="section.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="section.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="section.titlepage.recto.style">
<xsl:apply-templates select="." mode="section.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="sect1.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sect1info/title">
      <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sect1info/subtitle">
      <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/corpauthor"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/authorgroup"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/author"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/othercredit"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/releaseinfo"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/copyright"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/legalnotice"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/pubdate"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/revision"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/revhistory"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="sect1info/abstract"/>
  <xsl:apply-templates mode="sect1.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="sect1.titlepage.verso">
</xsl:template>

<xsl:template name="sect1.titlepage.separator">
</xsl:template>

<xsl:template name="sect1.titlepage.before.recto">
</xsl:template>

<xsl:template name="sect1.titlepage.before.verso">
</xsl:template>

<xsl:template name="sect1.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="sect1.titlepage.before.recto"/>
      <xsl:call-template name="sect1.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="sect1.titlepage.before.verso"/>
      <xsl:call-template name="sect1.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="sect1.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="sect1.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="sect1.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="sect1.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect1.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect1.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="sect2.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sect2info/title">
      <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sect2info/subtitle">
      <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/corpauthor"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/authorgroup"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/author"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/othercredit"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/releaseinfo"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/copyright"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/legalnotice"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/pubdate"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/revision"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/revhistory"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="sect2info/abstract"/>
  <xsl:apply-templates mode="sect2.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="sect2.titlepage.verso">
</xsl:template>

<xsl:template name="sect2.titlepage.separator">
</xsl:template>

<xsl:template name="sect2.titlepage.before.recto">
</xsl:template>

<xsl:template name="sect2.titlepage.before.verso">
</xsl:template>

<xsl:template name="sect2.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="sect2.titlepage.before.recto"/>
      <xsl:call-template name="sect2.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="sect2.titlepage.before.verso"/>
      <xsl:call-template name="sect2.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="sect2.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="sect2.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="sect2.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="sect2.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect2.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect2.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="sect3.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sect3info/title">
      <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sect3info/subtitle">
      <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/corpauthor"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/authorgroup"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/author"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/othercredit"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/releaseinfo"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/copyright"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/legalnotice"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/pubdate"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/revision"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/revhistory"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="sect3info/abstract"/>
  <xsl:apply-templates mode="sect3.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="sect3.titlepage.verso">
</xsl:template>

<xsl:template name="sect3.titlepage.separator">
</xsl:template>

<xsl:template name="sect3.titlepage.before.recto">
</xsl:template>

<xsl:template name="sect3.titlepage.before.verso">
</xsl:template>

<xsl:template name="sect3.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="sect3.titlepage.before.recto"/>
      <xsl:call-template name="sect3.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="sect3.titlepage.before.verso"/>
      <xsl:call-template name="sect3.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="sect3.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="sect3.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="sect3.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="sect3.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect3.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect3.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="sect4.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sect4info/title">
      <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sect4info/subtitle">
      <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/corpauthor"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/authorgroup"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/author"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/othercredit"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/releaseinfo"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/copyright"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/legalnotice"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/pubdate"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/revision"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/revhistory"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="sect4info/abstract"/>
  <xsl:apply-templates mode="sect4.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="sect4.titlepage.verso">
</xsl:template>

<xsl:template name="sect4.titlepage.separator">
</xsl:template>

<xsl:template name="sect4.titlepage.before.recto">
</xsl:template>

<xsl:template name="sect4.titlepage.before.verso">
</xsl:template>

<xsl:template name="sect4.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="sect4.titlepage.before.recto"/>
      <xsl:call-template name="sect4.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="sect4.titlepage.before.verso"/>
      <xsl:call-template name="sect4.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="sect4.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="sect4.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="sect4.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="sect4.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect4.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect4.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="sect5.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sect5info/title">
      <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sect5info/subtitle">
      <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/corpauthor"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/authorgroup"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/author"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/othercredit"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/releaseinfo"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/copyright"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/legalnotice"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/pubdate"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/revision"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/revhistory"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="sect5info/abstract"/>
  <xsl:apply-templates mode="sect5.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="sect5.titlepage.verso">
</xsl:template>

<xsl:template name="sect5.titlepage.separator">
</xsl:template>

<xsl:template name="sect5.titlepage.before.recto">
</xsl:template>

<xsl:template name="sect5.titlepage.before.verso">
</xsl:template>

<xsl:template name="sect5.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="sect5.titlepage.before.recto"/>
      <xsl:call-template name="sect5.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="sect5.titlepage.before.verso"/>
      <xsl:call-template name="sect5.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="sect5.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="sect5.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="sect5.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="sect5.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sect5.titlepage.recto.style">
<xsl:apply-templates select="." mode="sect5.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="simplesect.titlepage.recto">
  <xsl:choose>
    <xsl:when test="simplesectinfo/title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="simplesectinfo/subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/corpauthor"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/corpauthor"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/authorgroup"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/authorgroup"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/author"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/author"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/othercredit"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/othercredit"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/releaseinfo"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/releaseinfo"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/copyright"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/copyright"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/legalnotice"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/legalnotice"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/pubdate"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/pubdate"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/revision"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/revision"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/revhistory"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/revhistory"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="simplesectinfo/abstract"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="docinfo/abstract"/>
  <xsl:apply-templates mode="simplesect.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="simplesect.titlepage.verso">
</xsl:template>

<xsl:template name="simplesect.titlepage.separator">
</xsl:template>

<xsl:template name="simplesect.titlepage.before.recto">
</xsl:template>

<xsl:template name="simplesect.titlepage.before.verso">
</xsl:template>

<xsl:template name="simplesect.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="simplesect.titlepage.before.recto"/>
      <xsl:call-template name="simplesect.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="simplesect.titlepage.before.verso"/>
      <xsl:call-template name="simplesect.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="simplesect.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style" margin-left="{$title.margin.left}" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="simplesect.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="simplesect.titlepage.recto.style">
<xsl:apply-templates select="." mode="simplesect.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="bibliography.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="bibliography.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::bibliography[1]"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="bibliographyinfo/subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="bibliographyinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="bibliography.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="bibliography.titlepage.verso">
</xsl:template>

<xsl:template name="bibliography.titlepage.separator">
</xsl:template>

<xsl:template name="bibliography.titlepage.before.recto">
</xsl:template>

<xsl:template name="bibliography.titlepage.before.verso">
</xsl:template>

<xsl:template name="bibliography.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="bibliography.titlepage.before.recto"/>
      <xsl:call-template name="bibliography.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="bibliography.titlepage.before.verso"/>
      <xsl:call-template name="bibliography.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="bibliography.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="bibliography.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="bibliography.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="bibliodiv.titlepage.recto">
  <xsl:choose>
    <xsl:when test="bibliodivinfo/title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="bibliodivinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="bibliodivinfo/subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="bibliodivinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="bibliodiv.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="bibliodiv.titlepage.verso">
</xsl:template>

<xsl:template name="bibliodiv.titlepage.separator">
</xsl:template>

<xsl:template name="bibliodiv.titlepage.before.recto">
</xsl:template>

<xsl:template name="bibliodiv.titlepage.before.verso">
</xsl:template>

<xsl:template name="bibliodiv.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="bibliodiv.titlepage.before.recto"/>
      <xsl:call-template name="bibliodiv.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="bibliodiv.titlepage.before.verso"/>
      <xsl:call-template name="bibliodiv.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="bibliodiv.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="bibliodiv.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="20.736pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::bibliodiv[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="bibliodiv.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="bibliodiv.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="bibliodiv.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="glossary.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="glossary.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::glossary[1]"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="glossaryinfo/subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="glossaryinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="glossary.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="glossary.titlepage.verso">
</xsl:template>

<xsl:template name="glossary.titlepage.separator">
</xsl:template>

<xsl:template name="glossary.titlepage.before.recto">
</xsl:template>

<xsl:template name="glossary.titlepage.before.verso">
</xsl:template>

<xsl:template name="glossary.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="glossary.titlepage.before.recto"/>
      <xsl:call-template name="glossary.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="glossary.titlepage.before.verso"/>
      <xsl:call-template name="glossary.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="glossary.titlepage.separator"/>
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

<xsl:template match="subtitle" mode="glossary.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="glossary.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="glossary.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="glossdiv.titlepage.recto">
  <xsl:choose>
    <xsl:when test="glossdivinfo/title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="glossdivinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="glossdivinfo/subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="glossdivinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="glossdiv.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="glossdiv.titlepage.verso">
</xsl:template>

<xsl:template name="glossdiv.titlepage.separator">
</xsl:template>

<xsl:template name="glossdiv.titlepage.before.recto">
</xsl:template>

<xsl:template name="glossdiv.titlepage.before.verso">
</xsl:template>

<xsl:template name="glossdiv.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="glossdiv.titlepage.before.recto"/>
      <xsl:call-template name="glossdiv.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="glossdiv.titlepage.before.verso"/>
      <xsl:call-template name="glossdiv.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="glossdiv.titlepage.separator"/>
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
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="glossdiv.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="20.736pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::glossdiv[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="glossdiv.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="glossdiv.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="glossdiv.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="index.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="index.titlepage.recto.style" margin-left="0pt" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::index[1]"/>
<xsl:with-param name="pagewide" select="1"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="indexinfo/subtitle">
      <xsl:apply-templates mode="index.titlepage.recto.auto.mode" select="indexinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="index.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="index.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="index.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="index.titlepage.verso">
</xsl:template>

<xsl:template name="index.titlepage.separator">
</xsl:template>

<xsl:template name="index.titlepage.before.recto">
</xsl:template>

<xsl:template name="index.titlepage.before.verso">
</xsl:template>

<xsl:template name="index.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="index.titlepage.before.recto"/>
      <xsl:call-template name="index.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="index.titlepage.before.verso"/>
      <xsl:call-template name="index.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="index.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="index.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="index.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="subtitle" mode="index.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="index.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="index.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="indexdiv.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="indexdiv.titlepage.recto.style">
<xsl:call-template name="indexdiv.title">
<xsl:with-param name="title" select="title"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="indexdivinfo/subtitle">
      <xsl:apply-templates mode="indexdiv.titlepage.recto.auto.mode" select="indexdivinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="indexdiv.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="indexdiv.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="indexdiv.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="indexdiv.titlepage.verso">
</xsl:template>

<xsl:template name="indexdiv.titlepage.separator">
</xsl:template>

<xsl:template name="indexdiv.titlepage.before.recto">
</xsl:template>

<xsl:template name="indexdiv.titlepage.before.verso">
</xsl:template>

<xsl:template name="indexdiv.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="indexdiv.titlepage.before.recto"/>
      <xsl:call-template name="indexdiv.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="indexdiv.titlepage.before.verso"/>
      <xsl:call-template name="indexdiv.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="indexdiv.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="indexdiv.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="indexdiv.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="subtitle" mode="indexdiv.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="indexdiv.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="indexdiv.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="setindex.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="setindex.titlepage.recto.style" margin-left="0pt" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::setindex[1]"/>
<xsl:with-param name="pagewide" select="1"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="setindexinfo/subtitle">
      <xsl:apply-templates mode="setindex.titlepage.recto.auto.mode" select="setindexinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="setindex.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="setindex.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="setindex.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="setindex.titlepage.verso">
</xsl:template>

<xsl:template name="setindex.titlepage.separator">
</xsl:template>

<xsl:template name="setindex.titlepage.before.recto">
</xsl:template>

<xsl:template name="setindex.titlepage.before.verso">
</xsl:template>

<xsl:template name="setindex.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="setindex.titlepage.before.recto"/>
      <xsl:call-template name="setindex.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="setindex.titlepage.before.verso"/>
      <xsl:call-template name="setindex.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="setindex.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="setindex.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="setindex.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="subtitle" mode="setindex.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="setindex.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="setindex.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="colophon.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="colophon.titlepage.recto.style" margin-left="{$title.margin.left}" font-size="24.8832pt" font-family="{$title.fontset}" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::colophon[1]"/>
</xsl:call-template></fo:block>
  <xsl:choose>
    <xsl:when test="colophoninfo/subtitle">
      <xsl:apply-templates mode="colophon.titlepage.recto.auto.mode" select="colophoninfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="colophon.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="colophon.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="colophon.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="colophon.titlepage.verso">
</xsl:template>

<xsl:template name="colophon.titlepage.separator">
</xsl:template>

<xsl:template name="colophon.titlepage.before.recto">
</xsl:template>

<xsl:template name="colophon.titlepage.before.verso">
</xsl:template>

<xsl:template name="colophon.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="colophon.titlepage.before.recto"/>
      <xsl:call-template name="colophon.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="colophon.titlepage.before.verso"/>
      <xsl:call-template name="colophon.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="colophon.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="colophon.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="colophon.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="subtitle" mode="colophon.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="colophon.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="colophon.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="sidebar.titlepage.recto">
  <xsl:choose>
    <xsl:when test="sidebarinfo/title">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="sidebarinfo/title"/>
    </xsl:when>
    <xsl:when test="docinfo/title">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="docinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="sidebarinfo/subtitle">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="sidebarinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="docinfo/subtitle">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="docinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="sidebar.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

</xsl:template>

<xsl:template name="sidebar.titlepage.verso">
</xsl:template>

<xsl:template name="sidebar.titlepage.separator">
</xsl:template>

<xsl:template name="sidebar.titlepage.before.recto">
</xsl:template>

<xsl:template name="sidebar.titlepage.before.verso">
</xsl:template>

<xsl:template name="sidebar.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="sidebar.titlepage.before.recto"/>
      <xsl:call-template name="sidebar.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="sidebar.titlepage.before.verso"/>
      <xsl:call-template name="sidebar.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="sidebar.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="sidebar.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="sidebar.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="sidebar.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sidebar.titlepage.recto.style" font-family="{$title.fontset}" font-weight="bold">
<xsl:apply-templates select="." mode="sidebar.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="sidebar.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="sidebar.titlepage.recto.style" font-family="{$title.fontset}">
<xsl:apply-templates select="." mode="sidebar.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="qandaset.titlepage.recto">
  <xsl:choose>
    <xsl:when test="qandasetinfo/title">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/title"/>
    </xsl:when>
    <xsl:when test="blockinfo/title">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="qandasetinfo/subtitle">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="blockinfo/subtitle">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>

  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/corpauthor"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/corpauthor"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/corpauthor"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/authorgroup"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/authorgroup"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/authorgroup"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/author"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/author"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/author"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/othercredit"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/othercredit"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/othercredit"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/releaseinfo"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/releaseinfo"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/releaseinfo"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/copyright"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/copyright"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/copyright"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/legalnotice"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/legalnotice"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/legalnotice"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/pubdate"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/pubdate"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/pubdate"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/revision"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/revision"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/revision"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/revhistory"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/revhistory"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/revhistory"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="qandasetinfo/abstract"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="blockinfo/abstract"/>
  <xsl:apply-templates mode="qandaset.titlepage.recto.auto.mode" select="info/abstract"/>
</xsl:template>

<xsl:template name="qandaset.titlepage.verso">
</xsl:template>

<xsl:template name="qandaset.titlepage.separator">
</xsl:template>

<xsl:template name="qandaset.titlepage.before.recto">
</xsl:template>

<xsl:template name="qandaset.titlepage.before.verso">
</xsl:template>

<xsl:template name="qandaset.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" font-family="{$title.fontset}">
    <xsl:variable name="recto.content">
      <xsl:call-template name="qandaset.titlepage.before.recto"/>
      <xsl:call-template name="qandaset.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block start-indent="0pt" text-align="center"><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="qandaset.titlepage.before.verso"/>
      <xsl:call-template name="qandaset.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="qandaset.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="qandaset.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="qandaset.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="title" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" keep-with-next.within-column="always" font-size="24.8832pt" font-weight="bold">
<xsl:call-template name="component.title">
<xsl:with-param name="node" select="ancestor-or-self::qandaset[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="corpauthor" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em" font-size="14.4pt">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="authorgroup" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em" font-size="14.4pt">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="author" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em" font-size="14.4pt">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="othercredit" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="releaseinfo" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="copyright" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="legalnotice" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" text-align="start" margin-left="0.5in" margin-right="0.5in" font-family="{$body.fontset}">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="pubdate" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revision" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="revhistory" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="abstract" mode="qandaset.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="qandaset.titlepage.recto.style" space-before="0.5em" text-align="start" margin-left="0.5in" margin-right="0.5in" font-family="{$body.fontset}">
<xsl:apply-templates select="." mode="qandaset.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template name="table.of.contents.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="table.of.contents.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'TableofContents'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="table.of.contents.titlepage.verso">
</xsl:template>

<xsl:template name="table.of.contents.titlepage.separator">
</xsl:template>

<xsl:template name="table.of.contents.titlepage.before.recto">
</xsl:template>

<xsl:template name="table.of.contents.titlepage.before.verso">
</xsl:template>

<xsl:template name="table.of.contents.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="table.of.contents.titlepage.before.recto"/>
      <xsl:call-template name="table.of.contents.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="table.of.contents.titlepage.before.verso"/>
      <xsl:call-template name="table.of.contents.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="table.of.contents.titlepage.separator"/>
  </fo:block>
  
</xsl:template>

<xsl:template match="*" mode="table.of.contents.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="table.of.contents.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template name="list.of.tables.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="list.of.tables.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'ListofTables'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="list.of.tables.titlepage.verso">
</xsl:template>

<xsl:template name="list.of.tables.titlepage.separator">
</xsl:template>

<xsl:template name="list.of.tables.titlepage.before.recto">
</xsl:template>

<xsl:template name="list.of.tables.titlepage.before.verso">
</xsl:template>

<xsl:template name="list.of.tables.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="list.of.tables.titlepage.before.recto"/>
      <xsl:call-template name="list.of.tables.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="list.of.tables.titlepage.before.verso"/>
      <xsl:call-template name="list.of.tables.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="list.of.tables.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="list.of.tables.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="list.of.tables.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template name="list.of.figures.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="list.of.figures.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'ListofFigures'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="list.of.figures.titlepage.verso">
</xsl:template>

<xsl:template name="list.of.figures.titlepage.separator">
</xsl:template>

<xsl:template name="list.of.figures.titlepage.before.recto">
</xsl:template>

<xsl:template name="list.of.figures.titlepage.before.verso">
</xsl:template>

<xsl:template name="list.of.figures.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="list.of.figures.titlepage.before.recto"/>
      <xsl:call-template name="list.of.figures.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="list.of.figures.titlepage.before.verso"/>
      <xsl:call-template name="list.of.figures.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="list.of.figures.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="list.of.figures.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="list.of.figures.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template name="list.of.examples.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="list.of.examples.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'ListofExamples'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="list.of.examples.titlepage.verso">
</xsl:template>

<xsl:template name="list.of.examples.titlepage.separator">
</xsl:template>

<xsl:template name="list.of.examples.titlepage.before.recto">
</xsl:template>

<xsl:template name="list.of.examples.titlepage.before.verso">
</xsl:template>

<xsl:template name="list.of.examples.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="list.of.examples.titlepage.before.recto"/>
      <xsl:call-template name="list.of.examples.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="list.of.examples.titlepage.before.verso"/>
      <xsl:call-template name="list.of.examples.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="list.of.examples.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="list.of.examples.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="list.of.examples.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template name="list.of.equations.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="list.of.equations.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'ListofEquations'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="list.of.equations.titlepage.verso">
</xsl:template>

<xsl:template name="list.of.equations.titlepage.separator">
</xsl:template>

<xsl:template name="list.of.equations.titlepage.before.recto">
</xsl:template>

<xsl:template name="list.of.equations.titlepage.before.verso">
</xsl:template>

<xsl:template name="list.of.equations.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="list.of.equations.titlepage.before.recto"/>
      <xsl:call-template name="list.of.equations.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="list.of.equations.titlepage.before.verso"/>
      <xsl:call-template name="list.of.equations.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="list.of.equations.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="list.of.equations.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="list.of.equations.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template name="list.of.procedures.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="list.of.procedures.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'ListofProcedures'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="list.of.procedures.titlepage.verso">
</xsl:template>

<xsl:template name="list.of.procedures.titlepage.separator">
</xsl:template>

<xsl:template name="list.of.procedures.titlepage.before.recto">
</xsl:template>

<xsl:template name="list.of.procedures.titlepage.before.verso">
</xsl:template>

<xsl:template name="list.of.procedures.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="list.of.procedures.titlepage.before.recto"/>
      <xsl:call-template name="list.of.procedures.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="list.of.procedures.titlepage.before.verso"/>
      <xsl:call-template name="list.of.procedures.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="list.of.procedures.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="list.of.procedures.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="list.of.procedures.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template name="list.of.unknowns.titlepage.recto">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="list.of.unknowns.titlepage.recto.style" space-before.minimum="1em" space-before.optimum="1.5em" space-before.maximum="2em" space-after="0.5em" margin-left="{$title.margin.left}" start-indent="0pt" font-size="17.28pt" font-weight="bold" font-family="{$title.fontset}">
<xsl:call-template name="gentext">
<xsl:with-param name="key" select="'ListofUnknown'"/>
</xsl:call-template></fo:block>
</xsl:template>

<xsl:template name="list.of.unknowns.titlepage.verso">
</xsl:template>

<xsl:template name="list.of.unknowns.titlepage.separator">
</xsl:template>

<xsl:template name="list.of.unknowns.titlepage.before.recto">
</xsl:template>

<xsl:template name="list.of.unknowns.titlepage.before.verso">
</xsl:template>

<xsl:template name="list.of.unknowns.titlepage">
  <fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:variable name="recto.content">
      <xsl:call-template name="list.of.unknowns.titlepage.before.recto"/>
      <xsl:call-template name="list.of.unknowns.titlepage.recto"/>
    </xsl:variable>
    <xsl:variable name="recto.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($recto.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($recto.content) != '') or ($recto.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$recto.content"/></fo:block>
    </xsl:if>
    <xsl:variable name="verso.content">
      <xsl:call-template name="list.of.unknowns.titlepage.before.verso"/>
      <xsl:call-template name="list.of.unknowns.titlepage.verso"/>
    </xsl:variable>
    <xsl:variable name="verso.elements.count">
      <xsl:choose>
        <xsl:when test="function-available('exsl:node-set')"><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:when test="contains(system-property('xsl:vendor'), 'Apache Software Foundation')">
          <!--Xalan quirk--><xsl:value-of select="count(exsl:node-set($verso.content)/*)"/></xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="(normalize-space($verso.content) != '') or ($verso.elements.count &gt; 0)">
      <fo:block><xsl:copy-of select="$verso.content"/></fo:block>
    </xsl:if>
    <xsl:call-template name="list.of.unknowns.titlepage.separator"/>
  </fo:block>
</xsl:template>

<xsl:template match="*" mode="list.of.unknowns.titlepage.recto.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="*" mode="list.of.unknowns.titlepage.verso.mode">
  <!-- if an element isn't found in this mode, -->
  <!-- try the generic titlepage.mode -->
  <xsl:apply-templates select="." mode="titlepage.mode"/>
</xsl:template>


<!-- special titlepage masters for SCons Titlepage style in books -->
<xsl:template name="user.pagemasters">
    <!-- title pages -->
    <fo:simple-page-master master-name="scons-titlepage-first"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="0mm"
                           margin-bottom="0mm"
                           margin-left="0mm"
                           margin-right="0mm">
      <xsl:attribute name="margin-{$direction.align.start}" select="0mm"/>
      <xsl:attribute name="margin-{$direction.align.end}" select="0mm"/>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-titlepage-first</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="0mm"
                      margin-top="0mm"
                      column-gap="0mm"
		      column-count="{$column.count.titlepage}"
                      background-repeat="no-repeat"
                      background-image="url(titlepage/mapnik_final_colors.svg)"
                      background-position-vertical="center"
                      background-position-horizontal="center">
      </fo:region-body>
      <fo:region-before region-name="xsl-region-before-first"
                        extent="{$region.before.extent}"
                        display-align="before"/>
      <fo:region-after region-name="xsl-region-after-first"
                       extent="{$region.after.extent}"
                        display-align="after"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="scons-titlepage-odd"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="{$page.margin.top}"
                           margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-titlepage-odd</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="{$body.margin.bottom}"
                      margin-top="{$body.margin.top}"
                      column-gap="{$column.gap.titlepage}"
                      column-count="{$column.count.titlepage}">
      </fo:region-body>
      <fo:region-before region-name="xsl-region-before-odd"
                        extent="{$region.before.extent}"
                        display-align="before"/>
      <fo:region-after region-name="xsl-region-after-odd"
                       extent="{$region.after.extent}"
                        display-align="after"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="scons-titlepage-even"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="{$page.margin.top}"
                           margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-titlepage-even</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="{$body.margin.bottom}"
                      margin-top="{$body.margin.top}"
                      column-gap="{$column.gap.titlepage}"
                      column-count="{$column.count.titlepage}">
      </fo:region-body>
      <fo:region-before region-name="xsl-region-before-even"
                        extent="{$region.before.extent}"
                        display-align="before"/>
      <fo:region-after region-name="xsl-region-after-even"
                       extent="{$region.after.extent}"
                        display-align="after"/>
    </fo:simple-page-master>

    <!-- chapter pages -->
    <fo:simple-page-master master-name="scons-chapter-first"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="{$page.margin.top}"
                           margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-chapter-first</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="{$body.margin.bottom}"
                      margin-top="{$body.margin.top}"
                      column-gap="{$column.gap.titlepage}"
                      column-count="{$column.count.titlepage}">
      </fo:region-body>
      <fo:region-before region-name="xsl-region-before-first"
                        extent="{$region.before.extent}"
                        display-align="before"/>
      <fo:region-after region-name="xsl-region-after-first"
                       extent="{$region.after.extent}"
                       display-align="after"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="scons-chapter-odd"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="{$page.margin.top}"
                           margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-chapter-odd</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="{$body.margin.bottom}"
                      margin-top="{$body.margin.top}"
                      column-gap="{$column.gap.body}"
                      column-count="{$column.count.body}">
      </fo:region-body>
      <fo:region-before region-name="xsl-region-before-odd"
                        extent="{$region.before.extent}"
                        display-align="before"/>
      <fo:region-after region-name="xsl-region-after-odd"
                       extent="{$region.after.extent}"
                       display-align="after"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="scons-chapter-even"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="{$page.margin.top}"
                           margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-chapter-even</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="{$body.margin.bottom}"
                      margin-top="{$body.margin.top}"
                      column-gap="{$column.gap.body}"
                      column-count="{$column.count.body}">
      </fo:region-body>
      <fo:region-before region-name="xsl-region-before-even"
                        extent="{$region.before.extent}"
                        display-align="before"/>
      <fo:region-after region-name="xsl-region-after-even"
                       extent="{$region.after.extent}"
                       display-align="after"/>
    </fo:simple-page-master>

    <!-- definition of pagemasters for draft mode -->
    <xsl:if test="$draft.mode != 'no'">
      <!-- draft title pages -->
      <fo:simple-page-master master-name="scons-titlepage-first-draft"
                           page-width="{$page.width}"
                           page-height="{$page.height}"
                           margin-top="{$page.margin.top}"
                           margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-titlepage-first-draft</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
      <fo:region-body margin-bottom="{$body.margin.bottom}"
                      margin-top="{$body.margin.top}"
                      column-gap="{$column.gap.titlepage}"
                      column-count="{$column.count.titlepage}">
          <xsl:if test="$draft.watermark.image != ''">
            <xsl:attribute name="background-image">
              <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$draft.watermark.image"/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="background-attachment">fixed</xsl:attribute>
            <xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
            <xsl:attribute name="background-position-horizontal">center</xsl:attribute>
            <xsl:attribute name="background-position-vertical">center</xsl:attribute>
          </xsl:if>
        </fo:region-body>
        <fo:region-before region-name="xsl-region-before-first"
                          extent="{$region.before.extent}"
                          display-align="before"/>
        <fo:region-after region-name="xsl-region-after-first"
                         extent="{$region.after.extent}"
                         display-align="after"/>
      </fo:simple-page-master>

      <fo:simple-page-master master-name="scons-titlepage-odd-draft"
                             page-width="{$page.width}"
                             page-height="{$page.height}"
                             margin-top="{$page.margin.top}"
                             margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-titlepage-odd-draft</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
        <fo:region-body margin-bottom="{$body.margin.bottom}"
                        margin-top="{$body.margin.top}"
                        column-gap="{$column.gap.titlepage}"
                        column-count="{$column.count.titlepage}">
          <xsl:if test="$draft.watermark.image != ''">
            <xsl:attribute name="background-image">
              <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$draft.watermark.image"/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="background-attachment">fixed</xsl:attribute>
            <xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
            <xsl:attribute name="background-position-horizontal">center</xsl:attribute>
            <xsl:attribute name="background-position-vertical">center</xsl:attribute>
          </xsl:if>
        </fo:region-body>
        <fo:region-before region-name="xsl-region-before-odd"
                          extent="{$region.before.extent}"
                          display-align="before"/>
        <fo:region-after region-name="xsl-region-after-odd"
                         extent="{$region.after.extent}"
                         display-align="after"/>
      </fo:simple-page-master>

      <fo:simple-page-master master-name="scons-titlepage-even-draft"
                             page-width="{$page.width}"
                             page-height="{$page.height}"
                             margin-top="{$page.margin.top}"
                             margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-titlepage-even-draft</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
        <fo:region-body margin-bottom="{$body.margin.bottom}"
                        margin-top="{$body.margin.top}"
                        column-gap="{$column.gap.titlepage}"
                        column-count="{$column.count.titlepage}">
          <xsl:if test="$draft.watermark.image != ''">
            <xsl:attribute name="background-image">
              <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$draft.watermark.image"/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="background-attachment">fixed</xsl:attribute>
            <xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
            <xsl:attribute name="background-position-horizontal">center</xsl:attribute>
            <xsl:attribute name="background-position-vertical">center</xsl:attribute>
          </xsl:if>
        </fo:region-body>
        <fo:region-before region-name="xsl-region-before-even"
                          extent="{$region.before.extent}"
                          display-align="before"/>
        <fo:region-after region-name="xsl-region-after-even"
                         extent="{$region.after.extent}"
                         display-align="after"/>
      </fo:simple-page-master>

      <!-- draft chapter pages -->
      <fo:simple-page-master master-name="scons-chapter-first-draft"
                             page-width="{$page.width}"
                             page-height="{$page.height}"
                             margin-top="{$page.margin.top}"
                             margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-chapter-first-draft</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
        <fo:region-body margin-bottom="{$body.margin.bottom}"
                        margin-top="{$body.margin.top}"
                        column-gap="{$column.gap.titlepage}"
                        column-count="{$column.count.titlepage}">
          <xsl:if test="$draft.watermark.image != ''">
            <xsl:attribute name="background-image">
              <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$draft.watermark.image"/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="background-attachment">fixed</xsl:attribute>
            <xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
            <xsl:attribute name="background-position-horizontal">center</xsl:attribute>
            <xsl:attribute name="background-position-vertical">center</xsl:attribute>
          </xsl:if>
        </fo:region-body>
        <fo:region-before region-name="xsl-region-before-first"
                          extent="{$region.before.extent}"
                          display-align="before"/>
        <fo:region-after region-name="xsl-region-after-first"
                         extent="{$region.after.extent}"
                         display-align="after"/>
      </fo:simple-page-master>

      <fo:simple-page-master master-name="scons-chapter-odd-draft"
                             page-width="{$page.width}"
                             page-height="{$page.height}"
                             margin-top="{$page.margin.top}"
                             margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-chapter-odd-draft</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
        <fo:region-body margin-bottom="{$body.margin.bottom}"
                        margin-top="{$body.margin.top}"
                        column-gap="{$column.gap.body}"
                        column-count="{$column.count.body}">
          <xsl:if test="$draft.watermark.image != ''">
            <xsl:attribute name="background-image">
              <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$draft.watermark.image"/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="background-attachment">fixed</xsl:attribute>
            <xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
            <xsl:attribute name="background-position-horizontal">center</xsl:attribute>
            <xsl:attribute name="background-position-vertical">center</xsl:attribute>
          </xsl:if>
        </fo:region-body>
        <fo:region-before region-name="xsl-region-before-odd"
                          extent="{$region.before.extent}"
                          display-align="before"/>
        <fo:region-after region-name="xsl-region-after-odd"
                         extent="{$region.after.extent}"
                         display-align="after"/>
      </fo:simple-page-master>

      <fo:simple-page-master master-name="scons-chapter-even-draft"
                             page-width="{$page.width}"
                             page-height="{$page.height}"
                             margin-top="{$page.margin.top}"
                             margin-bottom="{$page.margin.bottom}">
      <xsl:attribute name="margin-{$direction.align.start}">
        <xsl:value-of select="$page.margin.outer"/>
	<xsl:if test="$fop.extensions != 0">
	  <xsl:value-of select="concat(' - (',$title.margin.left,')')"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:attribute name="margin-{$direction.align.end}">
        <xsl:value-of select="$page.margin.inner"/>
      </xsl:attribute>
      <xsl:if test="$axf.extensions != 0">
        <xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">scons-chapter-even-draft</xsl:with-param>
        </xsl:call-template>
      </xsl:if>
        <fo:region-body margin-bottom="{$body.margin.bottom}"
                        margin-top="{$body.margin.top}"
                        column-gap="{$column.gap.body}"
                        column-count="{$column.count.body}">
          <xsl:if test="$draft.watermark.image != ''">
            <xsl:attribute name="background-image">
              <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$draft.watermark.image"/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="background-attachment">fixed</xsl:attribute>
            <xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
            <xsl:attribute name="background-position-horizontal">center</xsl:attribute>
            <xsl:attribute name="background-position-vertical">center</xsl:attribute>
          </xsl:if>
        </fo:region-body>
        <fo:region-before region-name="xsl-region-before-even"
                          extent="{$region.before.extent}"
                          display-align="before"/>
        <fo:region-after region-name="xsl-region-after-even"
                         extent="{$region.after.extent}"
                         display-align="after"/>
      </fo:simple-page-master>
    </xsl:if>

    <!-- setup for title page(s) -->
    <fo:page-sequence-master master-name="scons-titlepage">
      <fo:repeatable-page-master-alternatives>
        <fo:conditional-page-master-reference master-reference="scons-titlepage-first"
                                              page-position="first"/>
        <fo:conditional-page-master-reference master-reference="scons-titlepage-odd"
                                              odd-or-even="odd"/>
        <fo:conditional-page-master-reference 
                                              odd-or-even="even">
          <xsl:attribute name="master-reference">
            <xsl:choose>
              <xsl:when test="$double.sided != 0">scons-titlepage-even</xsl:when>
              <xsl:otherwise>scons-titlepage-odd</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </fo:conditional-page-master-reference>
      </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>

    <!-- definition of pagemasters for draft mode -->
    <xsl:if test="$draft.mode != 'no'">
      <!-- draft title pages -->

    <fo:page-sequence-master master-name="scons-titlepage-draft">
      <fo:repeatable-page-master-alternatives>
        <fo:conditional-page-master-reference master-reference="scons-titlepage-first-draft"
                                              page-position="first"/>
        <fo:conditional-page-master-reference master-reference="body-odd-draft"
                                              odd-or-even="odd"/>
        <fo:conditional-page-master-reference 
                                              odd-or-even="even">
          <xsl:attribute name="master-reference">
            <xsl:choose>
              <xsl:when test="$double.sided != 0">body-even-draft</xsl:when>
              <xsl:otherwise>body-odd-draft</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </fo:conditional-page-master-reference>
      </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>
    </xsl:if>
    
    <!-- setup for chapter pages -->
    <fo:page-sequence-master master-name="scons-chapter">
      <fo:repeatable-page-master-alternatives>
        <fo:conditional-page-master-reference master-reference="scons-chapter-first"
                                              page-position="first"/>
        <fo:conditional-page-master-reference master-reference="scons-chapter-odd"
                                              odd-or-even="odd"/>
        <fo:conditional-page-master-reference 
                                              odd-or-even="even">
          <xsl:attribute name="master-reference">
            <xsl:choose>
              <xsl:when test="$double.sided != 0">scons-chapter-even</xsl:when>
              <xsl:otherwise>scons-chapter-odd</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </fo:conditional-page-master-reference>
      </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>
    <!-- setup for draft chapter pages -->
    <xsl:if test="$draft.mode != 'no'">
      <!-- draft chapter pages -->
    <fo:page-sequence-master master-name="scons-chapter-draft">
      <fo:repeatable-page-master-alternatives>
        <fo:conditional-page-master-reference master-reference="scons-chapter-first-draft"
                                              page-position="first"/>
        <fo:conditional-page-master-reference master-reference="scons-chapter-odd-draft"
                                              odd-or-even="odd"/>
        <fo:conditional-page-master-reference 
                                              odd-or-even="even">
          <xsl:attribute name="master-reference">
            <xsl:choose>
              <xsl:when test="$double.sided != 0">scons-chapter-even-draft</xsl:when>
              <xsl:otherwise>scons-chapter-odd-draft</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </fo:conditional-page-master-reference>
      </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>
    </xsl:if>

</xsl:template>

<!-- selecting our SCons pagemasters -->
<xsl:template name="select.user.pagemaster">
  <xsl:param name="element"/>
  <xsl:param name="pageclass"/>
  <xsl:param name="default-pagemaster"/>

  <xsl:choose>
    <xsl:when test="$default-pagemaster = 'titlepage'">
      <xsl:value-of select="'scons-titlepage'" />
    </xsl:when>
    <xsl:when test="$element = 'reference' and 
                    $default-pagemaster = 'body'">
      <xsl:value-of select="'scons-titlepage'" />
    </xsl:when>
    <xsl:when test="$element = 'reference' and 
                    $default-pagemaster = 'body-draft'">
      <xsl:value-of select="'scons-titlepage-draft'" />
    </xsl:when>
    <xsl:when test="$element = 'chapter' and 
                    $default-pagemaster = 'body-draft'">
      <xsl:value-of select="'scons-chapter-draft'" />
    </xsl:when>
    <xsl:when test="$element = 'chapter'">
      <xsl:value-of select="'scons-chapter'" />
    </xsl:when>
    <xsl:when test="$default-pagemaster = 'titlepage-draft'">
      <xsl:value-of select="'scons-titlepage-draft'" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$default-pagemaster"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>



<xsl:template match="title" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" text-align="left" display-align="after" color="#C51410" font-size="75pt" space-before="0pt" space-after="0pt" font-weight="bold" font-family="'serif'">
<xsl:call-template name="division.title">
<xsl:with-param name="node" select="ancestor-or-self::book[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" text-align="left" display-align="after" font-size="28pt" space-before="0pt" space-after="0pt" font-family="{$title.fontset}" font-weight="normal">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="edition" mode="book.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" text-align="left" display-align="after" color="#C51410" font-size="56pt" space-before="0pt" space-after="0pt" font-family="'serif'" font-weight="normal">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>


<xsl:template match="title" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style" text-align="left" display-align="after" color="#C51410" font-size="75pt" space-before="0pt" space-after="0pt" font-weight="bold" font-family="'serif'">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style" text-align="left" display-align="after" font-size="28pt" space-before="0pt" space-after="0pt" font-family="{$title.fontset}" font-weight="normal">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="edition" mode="reference.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="reference.titlepage.recto.style" text-align="left" display-align="after" color="#C51410" font-size="56pt" space-before="0pt" space-after="0pt" font-family="'serif'" font-weight="normal">
<xsl:apply-templates select="." mode="reference.titlepage.recto.mode"/>
</fo:block>
</xsl:template>



<xsl:attribute-set name="chap.label.properties">
  <xsl:attribute name="font-family">
    <xsl:value-of select="$title.fontset"/>
  </xsl:attribute>
  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="color">#C51410</xsl:attribute>
  <xsl:attribute name="keep-with-next.within-column">always</xsl:attribute>
  <xsl:attribute name="text-align">center</xsl:attribute>
  <xsl:attribute name="display-align">after</xsl:attribute>
  <xsl:attribute name="space-before">0pt</xsl:attribute>
  <xsl:attribute name="space-after">0pt</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="chap.title.properties">
  <xsl:attribute name="font-family">
    <xsl:value-of select="$title.fontset"/>
  </xsl:attribute>
  <xsl:attribute name="font-size">24pt</xsl:attribute>
  <xsl:attribute name="color">#C51410</xsl:attribute>
  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="keep-with-next.within-column">always</xsl:attribute>
  <xsl:attribute name="text-align">left</xsl:attribute>
  <xsl:attribute name="display-align">after</xsl:attribute>
  <xsl:attribute name="space-before">0pt</xsl:attribute>
  <xsl:attribute name="space-after">0pt</xsl:attribute>
  <xsl:attribute name="space-start">0.7em</xsl:attribute>
</xsl:attribute-set>


<!-- customization of chapter titles -->
<xsl:template name="chap.title">
  <xsl:param name="node" select="."/>
  <xsl:param name="pagewide" select="0"/>

  <xsl:variable name="id">
    <xsl:call-template name="object.id">
      <xsl:with-param name="object" select="$node"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="title">
    <xsl:apply-templates select="$node" mode="object.title.markup">
      <xsl:with-param name="allow-anchors" select="1"/>
    </xsl:apply-templates>
  </xsl:variable>

  <xsl:variable name="titleabbrev">
    <xsl:apply-templates select="$node" mode="titleabbrev.markup"/>
  </xsl:variable>

  <xsl:variable name="level">
    <xsl:choose>
      <xsl:when test="ancestor::section">
        <xsl:value-of select="count(ancestor::section)+1"/>
      </xsl:when>
      <xsl:when test="ancestor::sect5">6</xsl:when>
      <xsl:when test="ancestor::sect4">5</xsl:when>
      <xsl:when test="ancestor::sect3">4</xsl:when>
      <xsl:when test="ancestor::sect2">3</xsl:when>
      <xsl:when test="ancestor::sect1">2</xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:if test="$passivetex.extensions != 0">
    <fotex:bookmark xmlns:fotex="http://www.tug.org/fotex"
                    fotex-bookmark-level="2"
                    fotex-bookmark-label="{$id}">
      <xsl:value-of select="$titleabbrev"/>
    </fotex:bookmark>
  </xsl:if>

    <fo:table table-layout="fixed" width="100%" border-width="0pt" border-style="none">

      <fo:table-column column-width="17mm"/>
      <fo:table-column/>
      <fo:table-column column-width="17mm"/>
	    
       <fo:table-body>
         <fo:table-row text-align="center">
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
          <fo:table-cell xsl:use-attribute-sets="chap.title.properties">
  <fo:block>

    <fo:inline xsl:use-attribute-sets="chap.label.properties" font-size="57pt"><xsl:apply-templates select="$node"
        mode="label.markup"/></fo:inline>

    <fo:inline xsl:use-attribute-sets="chap.title.properties"><xsl:apply-templates select="$node" 
          mode="title.markup"/></fo:inline>
  </fo:block>
         </fo:table-cell>
          <fo:table-cell>
            <fo:block></fo:block>
          </fo:table-cell>
 </fo:table-row>
       </fo:table-body>
 </fo:table>
</xsl:template>

<xsl:template match="title" mode="chapter.titlepage.recto.auto.mode">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format">
<xsl:call-template name="chap.title">
<xsl:with-param name="node" select="ancestor-or-self::chapter[1]"/>
</xsl:call-template>
</fo:block>
</xsl:template>


<xsl:template match="title" mode="header.content">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" space-before="0pt" space-after="0pt">
<xsl:apply-templates select="."/>
</fo:block>
</xsl:template>

<xsl:template match="subtitle" mode="header.content">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" space-before="0pt" space-after="0pt">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>

<xsl:template match="edition" mode="header.content">
<fo:block xmlns:fo="http://www.w3.org/1999/XSL/Format" xsl:use-attribute-sets="book.titlepage.recto.style" space-before="0pt" space-after="0pt">
<xsl:apply-templates select="." mode="book.titlepage.recto.mode"/>
</fo:block>
</xsl:template>


<xsl:template name="header.table">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="element" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <!-- default is a single table style for all headers -->
  <!-- Customize it for different page classes or sequence location -->

  <xsl:choose>
      <xsl:when test="$pageclass = 'index'">
          <xsl:attribute name="margin-left">0pt</xsl:attribute>
      </xsl:when>
  </xsl:choose>

  <xsl:variable name="column1">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">1</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">1</xsl:when>
      <xsl:otherwise>3</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="column3">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">3</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">3</xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="candidate">
    <fo:table table-layout="fixed" width="100%">
      <xsl:call-template name="head.sep.rule">
        <xsl:with-param name="pageclass" select="$pageclass"/>
        <xsl:with-param name="sequence" select="$sequence"/>
        <xsl:with-param name="gentext-key" select="$gentext-key"/>
      </xsl:call-template>

      <fo:table-column column-number="1">
        <xsl:attribute name="column-width">
          <xsl:text>proportional-column-width(</xsl:text>
          <xsl:call-template name="header.footer.width">
            <xsl:with-param name="location">header</xsl:with-param>
            <xsl:with-param name="position" select="$column1"/>
          </xsl:call-template>
          <xsl:text>)</xsl:text>
        </xsl:attribute>
      </fo:table-column>
      <fo:table-column column-number="2">
        <xsl:attribute name="column-width">
          <xsl:text>proportional-column-width(</xsl:text>
          <xsl:call-template name="header.footer.width">
            <xsl:with-param name="location">header</xsl:with-param>
            <xsl:with-param name="position" select="2"/>
          </xsl:call-template>
          <xsl:text>)</xsl:text>
        </xsl:attribute>
      </fo:table-column>
      <fo:table-column column-number="3">
        <xsl:attribute name="column-width">
          <xsl:text>proportional-column-width(</xsl:text>
          <xsl:call-template name="header.footer.width">
            <xsl:with-param name="location">header</xsl:with-param>
            <xsl:with-param name="position" select="$column3"/>
          </xsl:call-template>
          <xsl:text>)</xsl:text>
        </xsl:attribute>
      </fo:table-column>

      <fo:table-body>
        <fo:table-row>
          <xsl:attribute name="block-progression-dimension.minimum">
            <xsl:value-of select="$header.table.height"/>
          </xsl:attribute>
          <fo:table-cell text-align="left"
                         display-align="before">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="header.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'left'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="center"
                         display-align="before">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="header.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'center'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="right"
                         display-align="before">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="header.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'right'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
        </fo:table-row>
      </fo:table-body>
    </fo:table>
  </xsl:variable>

  <!-- Really output a header? -->
  <xsl:choose>
    <xsl:when test="$pageclass = 'titlepage' and $gentext-key = 'book'
                    and $sequence='first'">
      <!-- no, book titlepages have no headers at all -->
    </xsl:when>
    <xsl:when test="$pageclass = 'scons-titlepage'">
      <!-- no, book titlepages have no headers at all -->
    </xsl:when>
    <xsl:when test="$pageclass = 'scons-chapter' and
                    $sequence = 'first'">
      <!-- no, book chapters have no headers at all -->
    </xsl:when>
    <xsl:when test="$sequence = 'blank' and $headers.on.blank.pages = 0">
      <!-- no output -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:copy-of select="$candidate"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template name="header.content">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="position" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <fo:block>

    <!-- sequence can be odd, even, first, blank -->
    <!-- position can be left, center, right -->
    <xsl:choose>

      <xsl:when test="$pageclass = 'titlepage'">
        <!-- nop; no footer on title pages -->
      </xsl:when>

      <xsl:when test="$double.sided != 0 and $sequence = 'even'
                      and $position='left'">
        <fo:retrieve-marker 
      retrieve-class-name="section.head.marker"
      retrieve-position="first-including-carryover"
      retrieve-boundary="page-sequence"/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and 
                      ($sequence = 'odd' or $sequence = 'first' or $sequence = 'blank')
                      and $position='right'">
        <fo:retrieve-marker 
      retrieve-class-name="section.head.marker"
      retrieve-position="first-including-carryover"
      retrieve-boundary="page-sequence"/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and 
                      ($sequence = 'odd' or $sequence = 'first' or $sequence = 'blank')
                      and $position='left'">
        <xsl:value-of select="/book/title"/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and $sequence = 'even'
                      and $position='right'">
        <xsl:value-of select="/book/title"/>
      </xsl:when>


      <xsl:when test="$double.sided = 0 and $sequence = 'even'
                      and $position='right'">
        <xsl:value-of select="/book/title"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and $sequence = 'even'
                      and $position='left'">
        <xsl:value-of select="/book/title"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and ($sequence = 'odd' or $sequence = 'first')
                      and $position='right'">
        <fo:retrieve-marker 
      retrieve-class-name="section.head.marker"
      retrieve-position="first-including-carryover"
      retrieve-boundary="page-sequence"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and ($sequence = 'odd' or $sequence = 'first')
                      and $position='left'">
        <xsl:value-of select="/book/title"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and $sequence = 'even'
                      and $position='right'">
        <fo:retrieve-marker 
      retrieve-class-name="section.head.marker"
      retrieve-position="first-including-carryover"
      retrieve-boundary="page-sequence"/>
      </xsl:when>


      <xsl:when test="$position='center'">
<!--      <xsl:apply-templates select="." 
  mode="titleabbrev.markup"/>
-->
	  </xsl:when>

      <xsl:when test="$sequence='blank'">
        <!-- nop -->
      </xsl:when>

      <xsl:otherwise>
        <!-- nop -->
      </xsl:otherwise>

    </xsl:choose>
  </fo:block>
</xsl:template>


<xsl:template name="footer.table">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <!-- default is a single table style for all footers -->
  <!-- Customize it for different page classes or sequence location -->

  <xsl:choose>
      <xsl:when test="$pageclass = 'index'">
          <xsl:attribute name="margin-left">0pt</xsl:attribute>
      </xsl:when>
  </xsl:choose>

  <xsl:variable name="column1">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">1</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">1</xsl:when>
      <xsl:otherwise>3</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="column3">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">3</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">3</xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="candidate">
    <fo:table table-layout="fixed" width="100%">
      <xsl:call-template name="foot.sep.rule">
        <xsl:with-param name="pageclass" select="$pageclass"/>
        <xsl:with-param name="sequence" select="$sequence"/>
        <xsl:with-param name="gentext-key" select="$gentext-key"/>
      </xsl:call-template>
      <fo:table-column column-number="1">
        <xsl:attribute name="column-width">
          <xsl:text>proportional-column-width(</xsl:text>
          <xsl:call-template name="header.footer.width">
            <xsl:with-param name="location">footer</xsl:with-param>
            <xsl:with-param name="position" select="$column1"/>
          </xsl:call-template>
          <xsl:text>)</xsl:text>
        </xsl:attribute>
      </fo:table-column>
      <fo:table-column column-number="2">
        <xsl:attribute name="column-width">
          <xsl:text>proportional-column-width(</xsl:text>
          <xsl:call-template name="header.footer.width">
            <xsl:with-param name="location">footer</xsl:with-param>
            <xsl:with-param name="position" select="2"/>
          </xsl:call-template>
          <xsl:text>)</xsl:text>
        </xsl:attribute>
      </fo:table-column>
      <fo:table-column column-number="3">
        <xsl:attribute name="column-width">
          <xsl:text>proportional-column-width(</xsl:text>
          <xsl:call-template name="header.footer.width">
            <xsl:with-param name="location">footer</xsl:with-param>
            <xsl:with-param name="position" select="$column3"/>
          </xsl:call-template>
          <xsl:text>)</xsl:text>
        </xsl:attribute>
      </fo:table-column>

      <fo:table-body>
        <fo:table-row>
          <xsl:attribute name="block-progression-dimension.minimum">
            <xsl:value-of select="$footer.table.height"/>
          </xsl:attribute>
          <fo:table-cell text-align="left"
                         display-align="after">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="footer.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'left'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="center"
                         display-align="after">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="footer.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'center'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="right"
                         display-align="after">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="footer.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'right'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
        </fo:table-row>
      </fo:table-body>
    </fo:table>
  </xsl:variable>

  <!-- Really output a footer? -->
  <xsl:choose>
    <xsl:when test="$pageclass='titlepage' and $gentext-key='book'
                    and $sequence='first'">
      <!-- no, book titlepages have no footers at all -->
    </xsl:when>
    <xsl:when test="$pageclass = 'scons-titlepage'">
      <!-- no, book titlepages have no footers at all -->
    </xsl:when>
    <xsl:when test="$pageclass = 'scons-chapter' and
                    $sequence='first'">
      <!-- no, book chapters have no footers on first page -->
    </xsl:when>
    <xsl:when test="$sequence = 'blank' and $footers.on.blank.pages = 0">
      <!-- no output -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:copy-of select="$candidate"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template name="footer.content">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="position" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <fo:block>
    <!-- pageclass can be front, body, back -->
    <!-- sequence can be odd, even, first, blank -->
    <!-- position can be left, center, right -->
    <xsl:choose>
      <xsl:when test="$pageclass = 'titlepage'">
        <!-- nop; no footer on title pages -->
      </xsl:when>

      <xsl:when test="$double.sided != 0 and $sequence = 'even'
                      and $position='left'">
        <fo:page-number/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and
                      ($sequence = 'odd' or $sequence = 'first' or $sequence = 'blank')
                      and $position='right'">
        <fo:page-number/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and
                      ($sequence = 'odd' or $sequence = 'first' or $sequence = 'blank')
                      and $position='left'">
        <fo:external-graphic
                src="url(titlepage/SCons_path.svg)"
                width="20mm" content-width="scale-to-fit"
                scaling="uniform"/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and $sequence = 'even'
                      and $position='right'">
        <fo:external-graphic
                src="url(titlepage/SCons_path.svg)"
                width="20mm" content-width="scale-to-fit"
                scaling="uniform"/>
      </xsl:when>


      <xsl:when test="$double.sided = 0 and $sequence = 'even'
                      and $position='right'">
        <fo:external-graphic
                src="url(titlepage/SCons_path.svg)"
                width="20mm" content-width="scale-to-fit"
                scaling="uniform"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and $sequence = 'even'
                      and $position='left'">
        <fo:external-graphic
                src="url(titlepage/SCons_path.svg)"
                width="20mm" content-width="scale-to-fit"
                scaling="uniform"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and ($sequence = 'odd' or $sequence = 'first')
                      and $position='right'">
        <fo:page-number/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and ($sequence = 'odd' or $sequence = 'first')
                      and $position='left'">
        <fo:external-graphic
                src="url(titlepage/SCons_path.svg)"
                width="20mm" content-width="scale-to-fit"
                scaling="uniform"/>
      </xsl:when>

      <xsl:when test="$double.sided = 0 and $sequence = 'even'
                      and $position='right'">
        <fo:page-number/>
      </xsl:when>


      <xsl:when test="$position='center'">
      </xsl:when>

      <xsl:when test="$sequence='blank'">
        <!-- nop -->
      </xsl:when>


      <xsl:otherwise>
        <!-- nop -->
      </xsl:otherwise>
    </xsl:choose>
  </fo:block>
</xsl:template>

<xsl:template name="head.sep.rule">
  <xsl:param name="pageclass"/>
  <xsl:param name="sequence"/>
  <xsl:param name="gentext-key"/>

  <xsl:if test="$header.rule != 0">
    <xsl:attribute name="border-bottom-width">0.5pt</xsl:attribute>
    <xsl:attribute name="border-bottom-style">solid</xsl:attribute>
    <xsl:attribute name="border-bottom-color">#C51410</xsl:attribute>
  </xsl:if>
</xsl:template>


<xsl:template name="foot.sep.rule">
  <xsl:param name="pageclass"/>
  <xsl:param name="sequence"/>
  <xsl:param name="gentext-key"/>

  <xsl:if test="$footer.rule != 0">
    <xsl:attribute name="border-top-width">0.5pt</xsl:attribute>
    <xsl:attribute name="border-top-style">solid</xsl:attribute>
    <xsl:attribute name="border-top-color">#C51410</xsl:attribute>
  </xsl:if>
</xsl:template>

<xsl:param name="header.column.widths">1 0 1</xsl:param>
<xsl:param name="footer.column.widths">1 0 1</xsl:param>
<xsl:param name="headers.on.blank.pages" select="1"/>
<xsl:param name="footers.on.blank.pages" select="1"/>

</xsl:stylesheet>

