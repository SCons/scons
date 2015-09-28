<?xml version='1.0' encoding='utf-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:exsl="http://exslt.org/common"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                extension-element-prefixes="dtm"
                exclude-result-prefixes="xse exsl" version="1.0">

  <xsl:include href="gentext.xsl"/>

  <dtm:doc dtm:idref="xref"/>
  <xsl:template match="xref" name="xref" dtm:id="xref">
    <xsl:variable name="target" select="id(@linkend)"/>
    <xsl:variable name="refelem" select="local-name($target)"/>

    <fo:inline>
    <xsl:choose>
      <xsl:when test="not($refelem)">
        <fo:inline color="#F00000">[XRef: Nonexistent linkend ID "<xsl:value-of select="@linkend"/>"]</fo:inline>
      </xsl:when>
      <xsl:when test="@endterm">
        <fo:inline xsl:use-attribute-sets="xref.properties">
          <xsl:variable name="etarget" select="id(@endterm)"/>
          <xsl:choose>
            <xsl:when test="count($etarget) = 0">
              <fo:inline color="#F00000">[XRef: Nonexistent endterm ID "<xsl:value-of select="@endterm"/>"]</fo:inline>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="$etarget" mode="endterm"
                xse:apply-serna-fold-template="false"/>
            </xsl:otherwise>
          </xsl:choose>
        </fo:inline>
      </xsl:when>
      <xsl:when test="$target/@xreflabel">
        <fo:inline xsl:use-attribute-sets="xref.properties">
          <xsl:call-template name="xref.xreflabel">
            <xsl:with-param name="target" select="$target"/>
          </xsl:call-template>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@xreflabel">
        <fo:inline xsl:use-attribute-sets="xref.properties">
          <xsl:value-of select="@xreflabel"/>
        </fo:inline>
      </xsl:when>
      <xsl:otherwise>
        <fo:inline xsl:use-attribute-sets="xref.properties">
          <xsl:apply-templates select="$target" mode="xref-to"
                xse:apply-serna-fold-template="false">
            <xsl:with-param name="referrer" select="."/>
            <xsl:with-param name="xrefstyle">
              <xsl:choose>
                <xsl:when test="@role and not(@xrefstyle) and $use.role.as.xrefstyle != 0">
                  <xsl:value-of select="@role"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="@xrefstyle"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:with-param>
          </xsl:apply-templates>
        </fo:inline>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="$insert.xref.page.number != 0 or local-name($target) = 'para'">
      <xsl:apply-templates select="$target" mode="page.citation"
                xse:apply-serna-fold-template="false">
        <xsl:with-param name="id" select="@linkend"/>
      </xsl:apply-templates>
    </xsl:if>
  </fo:inline>
  </xsl:template>

  <dtm:doc dtm:idref="endterm.childs"/>
  <xsl:template match="*" mode="endterm" dtm:id="endterm.childs">
    <!-- Process the children of the endterm element -->    
    <xsl:variable name="endterm">
      <xsl:apply-templates select="child::node()"/>
    </xsl:variable>
    <xsl:apply-templates select="$endterm" mode="remove-ids"/>
  </xsl:template>
  <xsl:template match="*" mode="remove-ids">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:choose>
          <xsl:when test="name(.) != 'id'">
            <xsl:copy/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:message>removing <xsl:value-of select="name(.)"/>
</xsl:message>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      <xsl:apply-templates mode="remove-ids"/>
    </xsl:copy>
  </xsl:template>

  <dtm:doc dtm:idref="all.xref-to"/>  
  <xsl:template match="*" mode="xref-to" dtm:id="all.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:message>
      <xsl:text>Don&apos;t know what gentext to create for xref to: &quot;</xsl:text>
      <xsl:value-of select="name(.)"/>
      <xsl:text>&quot;</xsl:text>
    </xsl:message>
    <xsl:text>???</xsl:text>
  </xsl:template>
  <xsl:template match="title" mode="xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <!-- if you xref to a title, xref to the parent... -->    
    <xsl:choose>
      <!-- FIXME: how reliable is this? -->      
      <xsl:when test="contains(local-name(parent::*), 'info')">
        <xsl:apply-templates select="parent::*[2]" mode="xref-to">
          <xsl:with-param name="referrer" select="$referrer"/>
          <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="parent::*" mode="xref-to">
          <xsl:with-param name="referrer" select="$referrer"/>
          <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="elements.xref-to"/>
  <xsl:template match="abstract|article|authorblurb|bibliodiv|bibliomset|
                       biblioset|blockquote|calloutlist|caution|colophon|
                       constraintdef|formalpara|glossdiv|important|indexdiv|
                       itemizedlist|legalnotice|lot|msg|msgexplan|msgmain|
                       msgrel|msgset|msgsub|note|orderedlist|partintro|
                       productionset|qandadiv|refsynopsisdiv|segmentedlist|
                       set|setindex|sidebar|tip|toc|variablelist|warning" mode="xref-to" dtm:id="elements.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <!-- catch-all for things with (possibly optional) titles -->    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="aeop.xref-to"/>
  <xsl:template match="author|editor|othercredit|personname" mode="xref-to" dtm:id="aeop.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:call-template name="person.name"/>
  </xsl:template>

  <dtm:doc dtm:idref="authorgroup.xref-to"/>
  <xsl:template match="authorgroup" mode="xref-to" dtm:id="authorgroup.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:call-template name="person.name.list"/>
  </xsl:template>

  <dtm:doc dtm:idref="fete.xref-to"/>
  <xsl:template match="figure|example|table|equation" mode="xref-to" dtm:id="fete.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="procedure.xref-to"/>
  <xsl:template match="procedure" mode="xref-to" dtm:id="procedure.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="cmdsynopsis.xref-to"/>
  <xsl:template match="cmdsynopsis" mode="xref-to" dtm:id="cmdsynopsis.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="(.//command)[1]" mode="xref"/>
  </xsl:template>

  <dtm:doc dtm:idref="funcsynopsis.xref-to"/>
  <xsl:template match="funcsynopsis" mode="xref-to" dtm:id="funcsynopsis.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="(.//function)[1]" mode="xref"/>
  </xsl:template>

  <dtm:doc dtm:idref="dpca.xref-to"/>
  <xsl:template match="dedication|preface|chapter|appendix" mode="xref-to" dtm:id="dpca.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="bibliography.xref-to"/>
  <xsl:template match="bibliography" mode="xref-to" dtm:id="bibliography.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="biblio.xref-to"/>
  <xsl:template match="biblioentry|bibliomixed" mode="xref-to" dtm:id="biblio.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <!-- handles both biblioentry and bibliomixed -->    
    <xsl:text>[</xsl:text>
    <xsl:choose>
      <xsl:when test="string(.) = ''">
        <xsl:variable name="bib" select="document($bibliography.collection)"/>
        <xsl:variable name="id" select="@id"/>
        <xsl:variable name="entry" select="$bib/bibliography/*[@id=$id][1]"/>
        <xsl:choose>
          <xsl:when test="$entry">
            <xsl:choose>
              <xsl:when test="$bibliography.numbered != 0">
                <xsl:number from="bibliography" count="biblioentry|bibliomixed" level="any" format="1"/>
              </xsl:when>
              <xsl:when test="local-name($entry/*[1]) = 'abbrev'">
                <xsl:apply-templates select="$entry/*[1]"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="@id"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:otherwise>
            <xsl:message>
              <xsl:text>No bibliography entry: </xsl:text>
              <xsl:value-of select="$id"/>
              <xsl:text> found in </xsl:text>
              <xsl:value-of select="$bibliography.collection"/>
            </xsl:message>
            <xsl:value-of select="@id"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$bibliography.numbered != 0">
            <xsl:number from="bibliography" count="biblioentry|bibliomixed" 
                        level="any" format="1"/>
          </xsl:when>
          <xsl:when test="local-name(*[1]) = 'abbrev'">
            <xsl:apply-templates select="*[1]"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@id"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>]</xsl:text>
  </xsl:template>

  <dtm:doc dtm:idref="glossary.xref-to"/>
  <xsl:template match="glossary" mode="xref-to" dtm:id="glossary.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="glossentry.xref-to"/>
  <xsl:template match="glossentry" mode="xref-to" dtm:id="glossentry.xref-to">
    <xsl:choose>
      <xsl:when test="$glossentry.show.acronym = 'primary'">
        <xsl:choose>
          <xsl:when test="acronym|abbrev">
            <xsl:apply-templates select="(acronym|abbrev)[1]"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="glossterm[1]" mode="xref-to"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="glossterm[1]" mode="xref-to"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <dtm:doc dtm:idref="glossterm.xref-to"/>
  <xsl:template match="glossterm" mode="xref-to" dtm:id="glossterm.xref-to">
    <xsl:apply-templates/>
  </xsl:template>

  <dtm:doc dtm:idref="index.xref-to"/>
  <xsl:template match="index" mode="xref-to" dtm:id="index.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="listitem.xref-to"/>
  <xsl:template match="listitem" mode="xref-to" dtm:id="listitem.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="sections.xref-to"/>
  <xsl:template match="section|simplesect|sect1|sect2|sect3|sect4|
                       sect5|refsect1|refsect2|refsect3" mode="xref-to" dtm:id="xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
    <!-- What about "in Chapter X"? -->  
  </xsl:template>

  <dtm:doc dtm:idref="bridgehead.xref-to"/>
  <xsl:template match="bridgehead" mode="xref-to" dtm:id="bridgehead.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
    <!-- What about "in Chapter X"? -->  
  </xsl:template>

  <dtm:doc dtm:idref="qandaset.xref-to"/>
  <xsl:template match="qandaset" mode="xref-to" dtm:id="qandaset.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="qandadiv.xref-to"/>
  <xsl:template match="qandadiv" mode="xref-to" dtm:id="qandadiv.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="qandaentry.xref-to"/>
  <xsl:template match="qandaentry" mode="xref-to" dtm:id="qandaentry.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="question[1]" mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="qa.xref-to"/>
  <xsl:template match="question|answer" mode="xref-to" dtm:id="qa.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="pr.xref-to"/>
  <xsl:template match="part|reference" mode="xref-to" dtm:id="pr.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="refentry.xref-to"/>
  <xsl:template match="refentry" mode="xref-to" dtm:id="refentry.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:choose>
      <xsl:when test="refmeta/refentrytitle">
        <xsl:apply-templates select="refmeta/refentrytitle"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="refnamediv/refname[1]"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates select="refmeta/manvolnum"/>
  </xsl:template>

  <dtm:doc dtm:idref="refnamediv.xref-to"/>
  <xsl:template match="refnamediv" mode="xref-to" dtm:id="refnamediv.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="refname[1]" mode="xref-to">
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="refname.xref-to"/>
  <xsl:template match="refname" mode="xref-to" dtm:id="refname.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates mode="xref-to">
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="step.xref-to"/>
  <xsl:template match="step" mode="xref-to" dtm:id="step.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:call-template name="gentext">
      <xsl:with-param name="key" select="'Step'"/>
    </xsl:call-template>
    <xsl:text/>
    <xsl:apply-templates select="." mode="number"/>
  </xsl:template>

  <dtm:doc dtm:idref="varlistentry.xref-to"/>
  <xsl:template match="varlistentry" mode="xref-to" dtm:id="varlistentry.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="term[1]" mode="xref-to">
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="term.varlistentry.xref-to"/>
  <xsl:template match="varlistentry/term" mode="xref-to" dtm:id="term.varlistentry.xref-to">
    <!-- to avoid the comma that will be generated if there are several terms -->    
    <xsl:apply-templates/>
  </xsl:template>

  <dtm:doc dtm:idref="co.xref-to"/>
  <xsl:template match="co" mode="xref-to" dtm:id="co.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="callout-bug"/>
  </xsl:template>

  <dtm:doc dtm:idref="book.xref-to"/>
  <xsl:template match="book" mode="xref-to" dtm:id="book.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:apply-templates select="." mode="object.xref.markup">
      <xsl:with-param name="purpose" select="'xref'"/>
      <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
      <xsl:with-param name="referrer" select="$referrer"/>
    </xsl:apply-templates>
  </xsl:template>

  <dtm:doc dtm:idref="para.xref-to"/>
  <xsl:template match="para" mode="xref-to" dtm:id="para.xref-to">
    <xsl:param name="referrer"/>
    <xsl:param name="xrefstyle"/>
    <xsl:variable name="context" select="(ancestor::simplesect|ancestor::section|ancestor::sect1|ancestor::sect2|ancestor::sect3|ancestor::sect4|ancestor::sect5|ancestor::refsection                                        |ancestor::refsect1                                        |ancestor::refsect2                                        |ancestor::refsect3                                        |ancestor::chapter                                        |ancestor::appendix|ancestor::preface|ancestor::partintro|ancestor::dedication|ancestor::colophon|ancestor::bibliography|ancestor::index|ancestor::glossary|ancestor::glossentry|ancestor::listitem|ancestor::varlistentry)[last()]"/>
    <xsl:apply-templates select="$context" mode="xref-to"/>
    <!--
  <xsl:apply-templates select="." mode="object.xref.markup">
    <xsl:with-param name="purpose" select="'xref'"/>
    <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
    <xsl:with-param name="referrer" select="$referrer"/>
  </xsl:apply-templates>
-->  
  </xsl:template>

<dtm:doc dtm:idref="title.xref"/>
<xsl:template match="title" mode="xref" dtm:id="title.xref">
  <xsl:apply-templates/>
</xsl:template>

<dtm:doc dtm:idref="command.xref"/>
<xsl:template match="command" mode="xref" dtm:id="command.xref">
  <xsl:call-template name="inline.boldseq"/>
</xsl:template>

<dtm:doc dtm:idref="function.xref"/>
<xsl:template match="function" mode="xref" dtm:id="function.xref">
  <xsl:call-template name="inline.monoseq"/>
</xsl:template>

<dtm:doc dtm:idref="all.page-citation"/>
<xsl:template match="*" mode="page.citation" dtm:id="all.page-citation">
  <xsl:param name="id" select="'???'"/>
  <fo:inline keep-together.within-line="always">
    <xsl:call-template name="substitute-markup">
      <xsl:with-param name="template">
        <xsl:call-template name="gentext.template">
          <xsl:with-param name="name" select="'page.citation'"/>
          <xsl:with-param name="context" select="'xref'"/>
        </xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="all.pagenumber-markup"/>
<xsl:template match="*" mode="pagenumber.markup" dtm:id="all.pagenumber-markup">
  <!--fo:page-number-citation ref-id="{@id}"/-->
</xsl:template>

<dtm:doc dtm:elements="xref/@xreflabel" dtm:idref="xref.xreflabel"/>
<xsl:template name="xref.xreflabel" dtm:id="xref.xreflabel">
  <!-- called to process an xreflabel...you might use this to make  -->
  <!-- xreflabels come out in the right font for different targets, -->
  <!-- for example. -->
  <xsl:param name="target" select="."/>
  <xsl:value-of select="$target/@xreflabel"/>
</xsl:template>

<dtm:doc dtm:idref="all.insert-title-markup"/>
<xsl:template match="*" mode="insert.title.markup" dtm:id="all.insert-title-markup">
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="title"/>

  <xsl:choose>
    <!-- FIXME: what about the case where titleabbrev is inside the info? -->
    <xsl:when test="$purpose = 'xref' and titleabbrev">
      <xsl:apply-templates select="." mode="titleabbrev.markup"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$title"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="ca.insert-title-markup"/>
<xsl:template match="chapter|appendix" mode="insert.title.markup" dtm:id="ca.insert-title-markup">
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="title"/>

  <xsl:choose>
    <xsl:when test="$purpose = 'xref'">
      <fo:inline font-style="italic">
        <xsl:value-of select="$title"/>
      </fo:inline>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$title"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="all.insert-subtitle-markup"/>
<xsl:template match="*" mode="insert.subtitle.markup" dtm:id="all.insert-subtitle-markup">
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="subtitle"/>

  <xsl:value-of select="$subtitle"/>
</xsl:template>

<dtm:doc dtm:idref="all.insert-pagenumber-markup"/>
<xsl:template match="*" mode="insert.pagenumber.markup" dtm:id="all.insert-pagenumber-markup">
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="pagenumber"/>

  <xsl:value-of select="$pagenumber"/>
</xsl:template>

<dtm:doc dtm:idref="all.insert-direction-markup"/>
<xsl:template match="*" mode="insert.direction.markup" dtm:id="all.insert-direction-markup">
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="direction"/>

  <xsl:value-of select="$direction"/>
</xsl:template>

<dtm:doc dtm:idref="all.insert-label-markup"/>
<xsl:template match="*" mode="insert.label.markup" dtm:id="all.insert-label-markup">
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="label"/>

  <xsl:value-of select="$label"/>
</xsl:template>

</xsl:stylesheet>

