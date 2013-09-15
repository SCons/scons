<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:doc="http://nwalsh.com/xsl/documentation/1.0"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                exclude-result-prefixes="doc"
                version='1.0'>

<dtm:doc dtm:idref="all.intralabel-punctuation"/>
<xsl:template match="*" mode="intralabel.punctuation" dtm:id="all.intralabel-punctuation">
  <xsl:text>.</xsl:text>
</xsl:template>

<dtm:doc dtm:idref="all.label-markup"/>
<xsl:template match="*" mode="label.markup" dtm:id="all.label-markup">
  <xsl:text>UNKNOWN LABEL MARKUP</xsl:text>
</xsl:template>

<dtm:doc dtm:idref="sb.label-markup"/>
<xsl:template match="set|book" mode="label.markup" dtm:id="sb.label-markup">
  <xsl:if test="@label">
    <xsl:value-of select="@label"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="part.label-markup"/>
<xsl:template match="part" mode="label.markup" dtm:id="part.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$part.autolabel != 0">
      <xsl:number from="book" count="part" format="I"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="partintro.label-markup"/>
<xsl:template match="partintro" mode="label.markup" dtm:id="partintro.label-markup">
  <!-- no label -->
</xsl:template>

<dtm:doc dtm:idref="preface.label-markup"/>
<xsl:template match="preface" mode="label.markup" dtm:id="preface.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$preface.autolabel != 0">
      <xsl:choose>
        <xsl:when test="$label.from.part != 0 and ancestor::part">
          <xsl:number from="part" count="preface" format="1" level="any"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:number from="book" count="preface" format="1" level="any"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="chapter.label-markup"/>
<xsl:template match="chapter" mode="label.markup" dtm:id="chapter.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$chapter.autolabel != 0">
      <xsl:choose>
        <xsl:when test="$label.from.part != 0 and ancestor::part">
          <xsl:number from="part" count="chapter" format="1" level="any"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:number from="book" count="chapter" format="1" level="any"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="appendix.label-markup"/>
<xsl:template match="appendix" mode="label.markup" dtm:id="appendix.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$appendix.autolabel != 0">
      <xsl:choose>
        <xsl:when test="$label.from.part != 0 and ancestor::part">
          <xsl:number from="part" count="appendix" format="A" level="any"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:number from="book|article"
                      count="appendix" format="A" level="any"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="article.label-markup"/>
<xsl:template match="article" mode="label.markup" dtm:id="article.label-markup">
  <xsl:if test="@label">
    <xsl:value-of select="@label"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="dc.label-markup"/>
<xsl:template match="dedication|colophon" mode="label.markup" dtm:id="dc.label-markup">
  <xsl:if test="@label">
    <xsl:value-of select="@label"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="reference.label-markup"/>
<xsl:template match="reference" mode="label.markup" dtm:id="reference.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$part.autolabel != 0">
      <xsl:number from="book" count="reference" format="I" level="any"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="refentry.label-markup"/>
<xsl:template match="refentry" mode="label.markup" dtm:id="refentry.label-markup">
  <xsl:if test="@label">
    <xsl:value-of select="@label"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="section.label-markup"/>
<xsl:template match="section" mode="label.markup" dtm:id="section.label-markup">
  <!-- if this is a nested section, label the parent -->
  <xsl:if test="local-name(..) = 'section'">
    <xsl:variable name="parent.section.label">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    </xsl:variable>
    <xsl:if test="$parent.section.label != ''">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
      <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
    </xsl:if>
  </xsl:if>

  <!-- if the parent is a component, maybe label that too -->
  <xsl:variable name="parent.is.component">
    <xsl:call-template name="is.component">
      <xsl:with-param name="node" select=".."/>
    </xsl:call-template>
  </xsl:variable>

  <!-- does this section get labelled? -->
  <xsl:variable name="label">
    <xsl:call-template name="label.this.section">
      <xsl:with-param name="section" select="."/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:if test="$section.label.includes.component.label != 0
                and $parent.is.component != 0">
    <xsl:variable name="parent.label">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    </xsl:variable>
    <xsl:if test="$parent.label != ''">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
      <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
    </xsl:if>
  </xsl:if>


  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$label != 0">
      <xsl:number count="section"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="sect1.label-markup"/>
<xsl:template match="sect1" mode="label.markup" dtm:id="sect1.label-markup">
  <!-- if the parent is a component, maybe label that too -->
  <xsl:variable name="parent.is.component">
    <xsl:call-template name="is.component">
      <xsl:with-param name="node" select=".."/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:if test="$section.label.includes.component.label != 0
                and $parent.is.component">
    <xsl:variable name="parent.label">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    </xsl:variable>
    <xsl:if test="$parent.label != ''">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
      <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
    </xsl:if>
  </xsl:if>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$section.autolabel != 0">
      <xsl:number count="sect1"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="sections.label-markup"/>
<xsl:template match="sect2|sect3|sect4|sect5" mode="label.markup" dtm:id="sections.label-markup">
  <!-- label the parent -->
  <xsl:variable name="parent.label">
    <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
  </xsl:variable>
  <xsl:if test="$parent.label != ''">
    <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
  </xsl:if>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$section.autolabel != 0">
      <xsl:choose>
        <xsl:when test="local-name(.) = 'sect2'">
	  <xsl:number count="sect2"/>
	</xsl:when>
	<xsl:when test="local-name(.) = 'sect3'">
	  <xsl:number count="sect3"/>
	</xsl:when>
	<xsl:when test="local-name(.) = 'sect4'">
	  <xsl:number count="sect4"/>
	</xsl:when>
	<xsl:when test="local-name(.) = 'sect5'">
	  <xsl:number count="sect5"/>
	</xsl:when>
      </xsl:choose>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="bridgehead.label-markup"/>
<xsl:template match="bridgehead" mode="label.markup" dtm:id="bridgehead.label-markup">
  <!-- FIXME: could we do a better job here? -->
  <xsl:variable name="contsec"
                select="(ancestor::section
                         |ancestor::simplesect
                         |ancestor::sect1
                         |ancestor::sect2
                         |ancestor::sect3
                         |ancestor::sect4
                         |ancestor::sect5
                         |ancestor::refsect1
                         |ancestor::refsect2
                         |ancestor::refsect3
                         |ancestor::chapter
                         |ancestor::appendix
                         |ancestor::preface)[last()]"/>

  <xsl:apply-templates select="$contsec" mode="label.markup" xse:apply-serna-fold-template="false"/>
</xsl:template>

<dtm:doc dtm:idref="refsect1.label-markup"/>
<xsl:template match="refsect1" mode="label.markup" dtm:id="refsect1.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$section.autolabel != 0">
      <xsl:number count="refsect1"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="refsects.label-markup"/>
<xsl:template match="refsect2|refsect3" mode="label.markup" dtm:id="refsects.label-markup">
  <!-- label the parent -->
  <xsl:variable name="parent.label">
    <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
  </xsl:variable>
  <xsl:if test="$parent.label != ''">
    <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
  </xsl:if>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$section.autolabel != 0">
      <xsl:choose>
        <xsl:when test="local-name(.) = 'refsect2'">
	  <xsl:number count="refsect2"/>
	</xsl:when>
        <xsl:otherwise>
	  <xsl:number count="refsect3"/>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="simplesect.label-markup"/>
<xsl:template match="simplesect" mode="label.markup" dtm:id="simplesect.label-markup">
  <!-- if this is a nested section, label the parent -->
  <xsl:if test="local-name(..) = 'section'
                or local-name(..) = 'sect1'
                or local-name(..) = 'sect2'
                or local-name(..) = 'sect3'
                or local-name(..) = 'sect4'
                or local-name(..) = 'sect5'">
    <xsl:variable name="parent.section.label">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    </xsl:variable>
    <xsl:if test="$parent.section.label != ''">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
      <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
    </xsl:if>
  </xsl:if>

  <!-- if the parent is a component, maybe label that too -->
  <xsl:variable name="parent.is.component">
    <xsl:call-template name="is.component">
      <xsl:with-param name="node" select=".."/>
    </xsl:call-template>
  </xsl:variable>

  <!-- does this section get labelled? -->
  <xsl:variable name="label">
    <xsl:call-template name="label.this.section">
      <xsl:with-param name="section" select="."/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:if test="$section.label.includes.component.label != 0
                and $parent.is.component != 0">
    <xsl:variable name="parent.label">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
    </xsl:variable>
    <xsl:if test="$parent.label != ''">
      <xsl:apply-templates select=".." mode="label.markup" xse:apply-serna-fold-template="false"/>
      <xsl:apply-templates select=".." mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
    </xsl:if>
  </xsl:if>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$label != 0">
      <xsl:number count="simplesect"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="qandadiv.label-markup"/>
<xsl:template match="qandadiv" mode="label.markup" dtm:id="qandadiv.label-markup">
  <xsl:variable name="lparent" select="(ancestor::set
                                       |ancestor::book
                                       |ancestor::chapter
                                       |ancestor::appendix
                                       |ancestor::preface
                                       |ancestor::section
                                       |ancestor::simplesect
                                       |ancestor::sect1
                                       |ancestor::sect2
                                       |ancestor::sect3
                                       |ancestor::sect4
                                       |ancestor::sect5
                                       |ancestor::refsect1
                                       |ancestor::refsect2
                                       |ancestor::refsect3)[last()]"/>

  <xsl:variable name="lparent.prefix">
    <xsl:apply-templates select="$lparent" mode="label.markup" xse:apply-serna-fold-template="false"/>
  </xsl:variable>

  <xsl:variable name="prefix">
    <xsl:if test="$qanda.inherit.numeration != 0">
      <xsl:if test="$lparent.prefix != ''">
        <xsl:apply-templates select="$lparent" mode="label.markup" xse:apply-serna-fold-template="false"/>
        <xsl:apply-templates select="$lparent" mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
      </xsl:if>
    </xsl:if>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="$prefix"/>
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="$qandadiv.autolabel != 0">
      <xsl:value-of select="$prefix"/>
      <xsl:number level="multiple" count="qandadiv" format="1"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="bgis.label-markup"/>
<xsl:template match="bibliography|glossary|index|setindex" mode="label.markup" dtm:id="bgis.label-markup">
  <xsl:if test="@label">
    <xsl:value-of select="@label"/>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="ftep.label-markup"/>
<xsl:template match="figure|table|example|procedure" mode="label.markup" dtm:id="ftep.label-markup">
  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:when test="local-name() = 'procedure' and
                    $formal.procedures = 0">
      <!-- No label -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="count.title"/>
    </xsl:otherwise>
  </xsl:choose>

</xsl:template>

<dtm:doc dtm:idref="equation.label-markup"/>
<xsl:template match="equation" mode="label.markup" dtm:id="equation.label-markup">
  <xsl:variable name="pchap"
                select="ancestor::chapter
                        |ancestor::appendix
                        |ancestor::article[ancestor::book]"/>

  <xsl:variable name="prefix">
    <xsl:if test="count($pchap) &gt; 0">
      <xsl:apply-templates select="$pchap" mode="label.markup" xse:apply-serna-fold-template="false"/>
    </xsl:if>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="count($pchap)>0">
          <xsl:if test="$prefix != ''">
            <xsl:apply-templates select="$pchap" mode="label.markup" xse:apply-serna-fold-template="false"/>
            <xsl:apply-templates select="$pchap" mode="intralabel.punctuation" xse:apply-serna-fold-template="false"/>
          </xsl:if>
          <xsl:number format="1" count="equation[title]" from="chapter|appendix" level="any"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:number format="1" count="equation[title]" from="book|article" level="any"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="abstract.label-markup"/>
<xsl:template match="abstract" mode="label.markup" dtm:id="abstract.label-markup">
  <!-- nop -->
</xsl:template>

<!-- ============================================================ -->
<dtm:doc dtm:idref="label.this.sect"/>
<xsl:template name="label.this.section" dtm:id="label.this.sect">
  <xsl:param name="section" select="."/>
  <xsl:value-of select="$section.autolabel"/>
</xsl:template>

<!-- ============================================================ -->
<dtm:doc dtm:idref="qa.label-markup"/>
<xsl:template match="question|answer" mode="label.markup" dtm:id="qa.label-markup">
  <!-- xsl:variable name="lparent" select="(ancestor::set
                                       |ancestor::book
                                       |ancestor::chapter
                                       |ancestor::appendix
                                       |ancestor::preface
                                       |ancestor::section
                                       |ancestor::simplesect
                                       |ancestor::sect1
                                       |ancestor::sect2
                                       |ancestor::sect3
                                       |ancestor::sect4
                                       |ancestor::sect5
                                       |ancestor::refsect1
                                       |ancestor::refsect2
                                       |ancestor::refsect3)[last()]"/ -->

  <!-- xsl:variable name="lparent.prefix">
    <xsl:apply-templates select="$lparent" mode="label.markup"/>
  </xsl:variable -->

  <xsl:variable name="prefix">
    <xsl:if test="$qanda.inherit.numeration != 0">
      <!-- xsl:if test="$lparent.prefix != ''">
        <xsl:apply-templates select="$lparent" mode="label.markup"/>
        <xsl:apply-templates select="$lparent" mode="intralabel.punctuation"/>
      </xsl:if -->
      <xsl:if test="ancestor::qandadiv">
        <xsl:apply-templates select="ancestor::qandadiv[1]" mode="label.markup" xse:apply-serna-fold-template="false"/>
        <xsl:apply-templates select="ancestor::qandadiv[1]"
                             mode="intralabel.punctuation"
          xse:apply-serna-fold-template="false"/>
      </xsl:if>
    </xsl:if>
  </xsl:variable>

  <xsl:variable name="inhlabel"
                select="ancestor-or-self::qandaset/@defaultlabel[1]"/>

  <xsl:variable name="deflabel">
    <xsl:choose>
      <xsl:when test="$inhlabel != ''">
        <xsl:value-of select="$inhlabel"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$qanda.defaultlabel"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="label" select="label[not(self::processing-instruction('se:choice'))]"/>

  <xsl:choose>
    <xsl:when test="count($label)>0">
      <xsl:apply-templates select="$label" xse:apply-serna-fold-template="false"/>
    </xsl:when>

    <xsl:when test="$deflabel = 'qanda' and self::question">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'Question'"/>
      </xsl:call-template>
    </xsl:when>

    <xsl:when test="$deflabel = 'qanda' and self::answer">
      <xsl:call-template name="gentext">
        <xsl:with-param name="key" select="'Answer'"/>
      </xsl:call-template>
    </xsl:when>

    <xsl:when test="$deflabel = 'number' and self::question">
      <xsl:value-of select="$prefix"/>
      <xsl:number level="multiple" count="qandaentry" format="1"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>
