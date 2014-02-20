<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:se="http://syntext.com/XSL/Format-1.0"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

  <!-- This template helps to see chapter when its titlethings are
       still empty -->

  <dtm:doc dtm:idref="handle.empty"/>
  <xsl:template name="handle.empty" dtm:id="handle.empty">
    <xsl:param name="titles" select="''"/>
    <xsl:param name="preamble" select="''"/>
    <xsl:param name="content" select="*"/>

    <xsl:variable name="toc">
      <xsl:call-template name="decorations"/>
    </xsl:variable>

    <xsl:variable name="type">
      <xsl:call-template name="get.type"/>
    </xsl:variable>

    <xsl:choose>
      <xsl:when test="string-length($titles)">
        <xsl:copy-of select="$titles"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="." mode="empty.title.mode"/>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="contains($toc, 'toc')">
      <xsl:choose>
        <xsl:when test="self::set">
          <xsl:call-template name="set.toc"/>
        </xsl:when>
        <xsl:when test="$type = 'division'">
          <xsl:call-template name="division.toc"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="component.toc"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="$show.preamble.editing">
      <fo:block padding-bottom="0.5em">
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
        </fo:block>
        <xsl:apply-templates select="$preamble"/>
      </fo:block>
      </fo:block>
      </xsl:when>
      <xsl:when test="processing-instruction('se:choice')">
        <fo:block>
          <xsl:apply-templates select="processing-instruction('se:choice')"/>
        </fo:block>
      </xsl:when>
    </xsl:choose>

    <xsl:apply-templates select="$content"/>
  </xsl:template>

  <dtm:doc dtm:idref="sbpr.empty-title-mode"/>
  <xsl:template match="set|book|part|reference" mode="empty.title.mode" dtm:id="sbpr.empty-title-mode">
    <fo:block
      background-color="#e0e0e0"
      xsl:use-attribute-sets="title.content.properties 
                              division.title.properties">
      <xsl:call-template name="gentext.template">
        <xsl:with-param name="context" select="'empty'"/>
        <xsl:with-param name="name" select="local-name(.)"/>
      </xsl:call-template>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="aacp.empty-title-mode"/>
  <xsl:template match="appendix|article|chapter|preface" mode="empty.title.mode" dtm:id="aacp.empty-title-mode">
    <fo:block
      background-color="#e0e0e0"
      xsl:use-attribute-sets="title.content.properties 
                             component.title.properties">
      <xsl:call-template name="gentext.template">
        <xsl:with-param name="context" select="'empty'"/>
        <xsl:with-param name="name" select="local-name(.)"/>
      </xsl:call-template>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="sections.empty-title-mode"/>
  <xsl:template match="section|sect1|sect2|sect3|sect4|sect5|bibliodiv|glossary" 
                mode="empty.title.mode" dtm:id="sections.empty-title-mode">
    <fo:block
      background-color="#e0e0e0"
      xsl:use-attribute-sets="title.content.properties 
                              section.title.level1.properties">
      <xsl:call-template name="gentext.template">
        <xsl:with-param name="context" select="'empty'"/>
        <xsl:with-param name="name" select="local-name(.)"/>
      </xsl:call-template>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="all.empty-title-mode"/>
  <xsl:template match="*" mode="empty.title.mode" dtm:id="all.empty-title-mode">
    <fo:block>
      <xsl:call-template name="gentext.template">
        <xsl:with-param name="context" select="'empty'"/>
        <xsl:with-param name="name" select="local-name(.)"/>
      </xsl:call-template>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="empty-title"/>
  <xsl:template name="empty-title" dtm:id="empty-title">
    <xsl:choose>
      <xsl:when test="node()">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="gentext.template">
          <xsl:with-param name="context" select="'empty'"/>
          <xsl:with-param name="name" select="'title'"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Commonly met elements -->

  <dtm:doc dtm:idref="titles.count"/>
  <xsl:template name="count.title" dtm:id="titles.count">
    <xsl:param name="need.dot"/>
    <xsl:choose>
      <xsl:when test="self::title or self::subtitle">
        <xsl:for-each select="..">
            <xsl:call-template name="count.title">
                <xsl:with-param name="need.dot" select="$need.dot"/>
            </xsl:call-template>
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="ancestor::appendix">
            <xsl:number level="multiple" count="appendix|section|sect1|
                sect2|sect3|sect4|sect5|simplesect" format="A.1."/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:number level="multiple" count="chapter|section|sect1|
                sect2|sect3|sect4|sect5|simplesect" format="1.1."/>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
          <xsl:when test="$need.dot">
            <xsl:number level="any" from="chapter|article|book|part"
                format="1. "/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:number level="any" from="chapter|article|book|part"
                format="1"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
     </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="title.formal-title-mode"/>
  <xsl:template match="title" mode="formal.title.mode" dtm:id="title.formal-title-mode">
    <xsl:param name="key" select="''"/>
    <xsl:variable name="title">
      <fo:inline>
        <xsl:call-template name="gentext">
          <xsl:with-param name="key" select="$key"/>
        </xsl:call-template>
        <xsl:text> </xsl:text>
        <xsl:call-template name="count.title">
            <xsl:with-param name="need.dot" select="1"/>
        </xsl:call-template>
      </fo:inline>
      <xsl:apply-templates/>
    </xsl:variable>
    <fo:block 
      xsl:use-attribute-sets="title.content.properties formal.title.properties">
      <xsl:choose>
        <xsl:when test="string-length($title)">
          <xsl:copy-of select="$title"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>Title:</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="title.formal-title-mode"/>
  <xsl:template match="title" mode="plain.formal.title.mode">
    <fo:block 
      xsl:use-attribute-sets="title.content.properties formal.title.properties">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="formal-title-gentext"/>
  <xsl:template name="formal.title.gentext" dtm:id="formal-title-gentext">
    <xsl:param name="key" select="''"/>
    <fo:block 
      xsl:use-attribute-sets="title.content.properties formal.title.properties">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="$key"/>
      </xsl:call-template>
    </fo:block>
  </xsl:template>

  <!-- Article Titles -->
  <dtm:doc dtm:idref="title.article-titles-mode"/>
  <xsl:template match="title" mode="article.titles.mode" dtm:id="title.article-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Appendix Titles -->
  <dtm:doc dtm:idref="title.appendix-titles-mode"/>
  <xsl:template match="title" mode="appendix.titles.mode" dtm:id="title.appendix-titles-mode">
    <fo:block>
      <xsl:choose>
        <xsl:when test="$appendix.autolabel">
          <xsl:call-template name="gentext">
            <xsl:with-param name="key" select="'appendix'"/>
          </xsl:call-template>
          <xsl:text> </xsl:text>
          <xsl:number level="single" count="appendix" format="A. "/>
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="empty-title"/>
        </xsl:otherwise>
      </xsl:choose>
    </fo:block>
  </xsl:template>

  <!-- Part Titles -->
  <dtm:doc dtm:idref="title.part-titles-mode"/>
  <xsl:template match="title" mode="part.titles.mode" dtm:id="title.part-titles-mode">
    <fo:block>
      <xsl:choose>
        <xsl:when test="$part.autolabel">
          <xsl:number level="single" count="part" format="I. "/>
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="empty-title"/>
        </xsl:otherwise>
      </xsl:choose>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="title.reference-titles-mode"/>
  <xsl:template match="title" mode="reference.titles.mode" dtm:id="title.reference-titles-mode">
    <fo:block 
      xsl:use-attribute-sets="title.content.properties 
                              division.title.properties">
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Chapter Titles -->
  <dtm:doc dtm:idref="title.chapter-titles-mode"/>
  <xsl:template match="title" mode="chapter.titles.mode" dtm:id="title.chapter-titles-mode">
    <fo:block>
      <xsl:choose>
        <xsl:when test="$chapter.autolabel">
          <fo:inline>
            <xsl:call-template name="gentext">
              <xsl:with-param name="key" select="'chapter'"/>
            </xsl:call-template>
            <xsl:text> </xsl:text>
            <xsl:number level="single" count="chapter" format="1. "/>
          </fo:inline>
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="empty-title"/>
        </xsl:otherwise>
      </xsl:choose>
    </fo:block>
  </xsl:template>

  <!-- Simplesect titles -->
  <dtm:doc dtm:idref="title.simplesect-titles-mode"/>
  <xsl:template match="title" mode="simplesect.titles.mode" dtm:id="title.simplesect-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Preface Titles -->
  <dtm:doc dtm:idref="title.preface-titles-mode"/>
  <xsl:template match="title" mode="preface.titles.mode" dtm:id="title.preface-titles-mode">
    <fo:block>
      <xsl:choose>
        <xsl:when test="$preface.autolabel">
          <fo:inline>
            <xsl:call-template name="gentext">
              <xsl:with-param name="key" select="'preface'"/>
            </xsl:call-template>
            <xsl:text> </xsl:text>
            <xsl:number level="single" count="preface" format="I. "/>
          </fo:inline>
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="empty-title"/>
        </xsl:otherwise>
      </xsl:choose>
    </fo:block>
  </xsl:template>

  <!-- Section Titles -->
  <dtm:doc dtm:idref="title.section-titles-mode"/>
  <xsl:template match="title" mode="section.titles.mode" dtm:id="title.section-titles-mode">
    <xsl:param name="level">
      <xsl:call-template name="section.level"/>
    </xsl:param>
    <xsl:param name="heading">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'section'"/>
      </xsl:call-template>
      <xsl:text> </xsl:text>
    </xsl:param>
    <xsl:variable name="title.content">
      <xsl:choose>
        <xsl:when test="$section.autolabel">
          <xsl:if test="not(ancestor::refentry)">
            <xsl:value-of select="$heading"/>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="$section.label.includes.component.label">
              <xsl:choose>
                <xsl:when test="ancestor::appendix">
                  <xsl:number 
                    level="multiple" 
                    count="appendix|section|sect1|sect2|sect3|sect4|sect5|
                           refsect1|refsect2|refsect3"
                    format="A.1. "/>
                </xsl:when>
                <xsl:when test="ancestor::refentry">
                </xsl:when>
                <xsl:otherwise>
                  <xsl:number 
                    level="multiple" 
                    count="chapter|qandadiv|section|
                           sect1|sect2|sect3|sect4|sect5|
                           refsect1|refsect2|refsect3"
                    format="1. "/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
              <xsl:number 
                level="multiple" 
                count="qandadiv|section|sect1|sect2|sect3|sect4|sect5|
                       refsect1|refsect2|refsect3"
                format="1. "/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <xsl:call-template name="empty-title"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$level = 1">
        <fo:block
          xsl:use-attribute-sets="section.title.level1.properties">
          <xsl:copy-of select="$title.content"/>
        </fo:block>
      </xsl:when>
      <xsl:when test="$level = 2">
        <fo:block
          xsl:use-attribute-sets="section.title.level2.properties">
          <xsl:copy-of select="$title.content"/>
        </fo:block>
      </xsl:when>
      <xsl:when test="$level = 3">
        <fo:block
          xsl:use-attribute-sets="section.title.level3.properties">
          <xsl:copy-of select="$title.content"/>
        </fo:block>
      </xsl:when>
      <xsl:when test="$level = 4">
        <fo:block
          xsl:use-attribute-sets="section.title.level4.properties">
          <xsl:copy-of select="$title.content"/>
        </fo:block>
      </xsl:when>
      <xsl:when test="$level = 5">
        <fo:block
          xsl:use-attribute-sets="section.title.level5.properties">
          <xsl:copy-of select="$title.content"/>
        </fo:block>
      </xsl:when>
      <xsl:otherwise>
        <fo:block
          xsl:use-attribute-sets="section.title.level5.properties">
          <xsl:copy-of select="$title.content"/>
        </fo:block>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Set Titles -->
  <dtm:doc dtm:idref="title.set-titles-mode"/>
  <xsl:template match="title" mode="set.titles.mode" dtm:id="title.set-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Book Titles -->
  <dtm:doc dtm:idref="title.book-titles-mode"/>
  <xsl:template match="title" mode="book.titles.mode" dtm:id="title.book-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Bibliodiv Titles -->
  <dtm:doc dtm:idref="title.bibliodiv-titles-mode"/>
  <xsl:template match="title" mode="bibliodiv.titles.mode" dtm:id="title.bibliodiv-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Bibliography Titles -->
  <dtm:doc dtm:idref="bibliography.title"/>
  <xsl:template name="bibliography.title" dtm:id="bibliography.title">
    <xsl:param name="node" select="."/>
    <fo:block>
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'bibliography'"/>
      </xsl:call-template>
    </fo:block>
    <xsl:apply-templates select="title"/>
  </xsl:template>

  <!-- Glossary Titles -->
  <dtm:doc dtm:idref="title.glossary-titles-mode"/>
  <xsl:template name="title" mode="glossary.titles.mode" dtm:id="title.glossary-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Glossdiv Titles -->
  <dtm:doc dtm:idref="title.glossdiv-titles-mode"/>
  <xsl:template match="title" mode="glossdiv.titles.mode" dtm:id="title.glossdiv-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

  <!-- Information wrappers -->
  <dtm:doc dtm:idref="infoes"/>
  <xsl:template match="articleinfo|artheader|bookbiblio|docinfo|objectinfo|refsynopsisdivinfo|sect1info|sect2info|sect3info|sect4info|sect5info|sectioninfo|setinfo" dtm:id="infoes">
    <fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <dtm:doc dtm:idref="title.refsynopsisdiv-titles-mode"/>
  <xsl:template match="title" mode="refsynopsisdiv.titles.mode" dtm:id="title.refsynopsisdiv-titles-mode">
    <fo:block>
      <xsl:call-template name="empty-title"/>
    </fo:block>
  </xsl:template>

 <dtm:doc dtm:idref="serna.fold.template"/>
 <xsl:template name="serna.fold.template" dtm:id="serna.fold.template">
   <xsl:apply-templates select="." mode="serna.fold" 
                        xse:apply-serna-fold-template="false"/>
 </xsl:template>

 <dtm:doc dtm:idref="all.serna-fold"/>
 <xsl:template match="*" mode="serna.fold" dtm:id="all.serna-fold">
   <se:fold se:fold=""/>
 </xsl:template>

</xsl:stylesheet>

