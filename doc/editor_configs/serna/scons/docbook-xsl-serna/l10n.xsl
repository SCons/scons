<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:l="http://docbook.sourceforge.net/xmlns/l10n/1.0"
                exclude-result-prefixes="l"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                extension-element-prefixes="dtm"
                version='1.0'>

<xsl:param name="l10n.xml.en" select="document('l10n/en.xml')/l:l10n"/>

<xsl:param name="supported.languages" 
           select="'af bg ca cs da de el en es et eu fi fr he hu id it ja ko lt
                    nl nn no pl pt ro ru sk sl sr sv th tr ok vi zh'"/>
<xsl:param name="supported.dlanguages" select="'pt_br zh_cn zh_tw'"/>

<dtm:doc dtm:idref="l10n.language"/>
<xsl:template name="l10n.language" dtm:id="l10n.language">
  <xsl:param name="target" select="."/>
  <xsl:param name="xref-context" select="false()"/>

  <xsl:variable name="mc-language">
    <xsl:choose>
      <xsl:when test="$l10n.gentext.language != ''">
        <xsl:value-of select="$l10n.gentext.language"/>
      </xsl:when>

      <xsl:when test="$xref-context or $l10n.gentext.use.xref.language != 0">
        <!-- can't do this one step: attributes are unordered! -->
        <xsl:variable name="lang-scope"
                      select="($target/ancestor-or-self::*[@lang]
                               |$target/ancestor-or-self::*[@xml:lang])[last()]"/>
        <xsl:variable name="lang-attr"
                      select="($lang-scope/@lang | $lang-scope/@xml:lang)[1]"/>
        <xsl:choose>
          <xsl:when test="string($lang-attr) = ''">
            <xsl:value-of select="$l10n.gentext.default.language"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$lang-attr"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <xsl:otherwise>
        <!-- can't do this one step: attributes are unordered! -->
        <xsl:variable name="lang-scope"
                      select="(ancestor-or-self::*[@lang]
                               |ancestor-or-self::*[@xml:lang])[last()]"/>
        <xsl:variable name="lang-attr"
                      select="($lang-scope/@lang | $lang-scope/@xml:lang)[1]"/>

        <xsl:choose>
          <xsl:when test="string($lang-attr) = ''">
            <xsl:value-of select="$l10n.gentext.default.language"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$lang-attr"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="language" select="translate($mc-language,
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                        'abcdefghijklmnopqrstuvwxyz')"/>

  <xsl:variable name="adjusted.language">
    <xsl:choose>
      <xsl:when test="contains($language,'-')">
        <xsl:value-of select="substring-before($language,'-')"/>
        <xsl:text>_</xsl:text>
        <xsl:value-of select="substring-after($language,'-')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$language"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="subs.language">
    <xsl:choose>
        <xsl:when test="contains($adjusted.language, '_')">
            <xsl:value-of select="substring-before($adjusted.language, '_')"/>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$adjusted.language"/>
        </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
 
  <xsl:choose>
    <xsl:when test="contains($adjusted.language, '_') and 
                    contains($supported.dlanguages, $adjusted.language)">
        <xsl:value-of select="$adjusted.language"/>
    </xsl:when>
    <xsl:when test="contains($supported.languages, $subs.language)">
        <xsl:value-of select="$subs.language"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:message>
        <xsl:text>l10n.language: No localization exists for "</xsl:text>
        <xsl:value-of select="$adjusted.language"/>
        <xsl:text>" or "</xsl:text>
        <xsl:value-of select="substring-before($adjusted.language,'_')"/>
        <xsl:text>". Using default "</xsl:text>
        <xsl:value-of select="$l10n.gentext.default.language"/>
        <xsl:text>".</xsl:text>
      </xsl:message>
      <xsl:value-of select="$l10n.gentext.default.language"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="language.attribute"/>
<xsl:template name="language.attribute" dtm:id="language.attribute">
  <xsl:param name="node" select="."/>

  <xsl:variable name="language">
    <xsl:choose>
      <xsl:when test="$l10n.gentext.language != ''">
        <xsl:value-of select="$l10n.gentext.language"/>
      </xsl:when>

      <xsl:otherwise>
        <!-- can't do this one step: attributes are unordered! -->
        <xsl:variable name="lang-scope"
                      select="($node/ancestor-or-self::*[@lang]
                               |$node/ancestor-or-self::*[@xml:lang])[last()]"/>
        <xsl:variable name="lang-attr"
                      select="($lang-scope/@lang | $lang-scope/@xml:lang)[1]"/>

        <xsl:choose>
          <xsl:when test="string($lang-attr) = ''">
            <xsl:value-of select="$l10n.gentext.default.language"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$lang-attr"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:if test="$language != ''">
    <xsl:attribute name="lang">
      <xsl:value-of select="$language"/>
    </xsl:attribute>
  </xsl:if>
</xsl:template>

<dtm:doc dtm:idref="gentext"/>
<xsl:template name="gentext" dtm:id="gentext">
  <xsl:param name="key" select="local-name(.)"/>
  <xsl:param name="lang">
    <xsl:call-template name="l10n.language"/>
  </xsl:param>

  <xsl:variable name="l10n.xml" 
    select="document(concat('l10n/', $lang, '.xml'))/l:l10n"/>

  <xsl:variable name="l10n.gentext"
                select="$l10n.xml/l:gentext[@key=$key]"/>

  <xsl:variable name="l10n.name">
    <xsl:value-of select="$l10n.gentext/@text"/>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="count($l10n.gentext) &gt; 0">
      <xsl:value-of select="$l10n.gentext/@text"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:message>
        <xsl:text>gentext: No "</xsl:text>
        <xsl:value-of select="$lang"/>
        <xsl:text>" localization of "</xsl:text>
        <xsl:value-of select="$key"/>
        <xsl:text>" exists</xsl:text>
	<xsl:choose>
	  <xsl:when test="$lang = 'en'">
	     <xsl:text>.</xsl:text>
	  </xsl:when>
	  <xsl:otherwise>
	     <xsl:text>; using "en".</xsl:text>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:message>
      <xsl:value-of select="($l10n.xml.en/l:gentext[@key=$key])[1]/@text"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="gentext.element.name"/>
<xsl:template name="gentext.element.name" dtm:id="gentext.element.name">
  <xsl:param name="element.name" select="name(.)"/>
  <xsl:param name="lang">
    <xsl:call-template name="l10n.language"/>
  </xsl:param>

  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="$element.name"/>
    <xsl:with-param name="lang" select="$lang"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.space"/>
<xsl:template name="gentext.space" dtm:id="gentext.space">
  <xsl:text> </xsl:text>
</xsl:template>

<dtm:doc dtm:idref="gentext.edited.by"/>
<xsl:template name="gentext.edited.by" dtm:id="gentext.edited.by">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'Editedby'"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.by"/>
<xsl:template name="gentext.by" dtm:id="gentext.by">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'by'"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.dingbat"/>
<xsl:template name="gentext.dingbat" dtm:id="gentext.dingbat">
  <xsl:param name="dingbat">bullet</xsl:param>
  <xsl:param name="lang">
    <xsl:call-template name="l10n.language"/>
  </xsl:param>

  <xsl:variable name="l10n.xml" 
    select="document(concat('l10n/', $lang, '.xml'))/l:l10n"/>
 
  <xsl:variable name="l10n.dingbat"
                select="($l10n.xml/l:dingbat[@key=$dingbat])[1]"/>

  <xsl:choose>
    <xsl:when test="count($l10n.dingbat) &gt; 0">
      <xsl:value-of select="$l10n.dingbat/@text"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:message>
        <xsl:text>gentext.dingbat: No "</xsl:text>
        <xsl:value-of select="$lang"/>
        <xsl:text>" localization of dingbat </xsl:text>
        <xsl:value-of select="$dingbat"/>
        <xsl:text> exists; using "en".</xsl:text>
      </xsl:message>

      <xsl:value-of select="($l10n.xml.en/l:gentext[@key=$dingbat])[1]/@text"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="gentext.startquote"/>
<xsl:template name="gentext.startquote" dtm:id="gentext.startquote">
  <xsl:call-template name="gentext.dingbat">
    <xsl:with-param name="dingbat">startquote</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.endquote"/>
<xsl:template name="gentext.endquote" dtm:id="gentext.endquote">
  <xsl:call-template name="gentext.dingbat">
    <xsl:with-param name="dingbat">endquote</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.nestedstartquote"/>
<xsl:template name="gentext.nestedstartquote" dtm:id="gentext.nestedstartquote">
  <xsl:call-template name="gentext.dingbat">
    <xsl:with-param name="dingbat">nestedstartquote</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.nestedendquote"/>
<xsl:template name="gentext.nestedendquote" dtm:id="gentext.nestedendquote">
  <xsl:call-template name="gentext.dingbat">
    <xsl:with-param name="dingbat">nestedendquote</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.nav.prev"/>
<xsl:template name="gentext.nav.prev" dtm:id="gentext.nav.prev">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'nav-prev'"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.nav.next"/>
<xsl:template name="gentext.nav.next" dtm:id="gentext.nav.next">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'nav-next'"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.nav.home"/>
<xsl:template name="gentext.nav.home" dtm:id="gentext.nav.home">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'nav-home'"/>
  </xsl:call-template>
</xsl:template>

<dtm:doc dtm:idref="gentext.nav.up"/>
<xsl:template name="gentext.nav.up" dtm:id="gentext.nav.up">
  <xsl:call-template name="gentext">
    <xsl:with-param name="key" select="'nav-up'"/>
  </xsl:call-template>
</xsl:template>

<!-- ============================================================ -->
<dtm:doc dtm:idref="gentext.template"/>
<xsl:template name="gentext.template" dtm:id="gentext.template">
  <xsl:param name="context" select="'default'"/>
  <xsl:param name="name" select="'default'"/>
  <xsl:param name="origname" select="$name"/>
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="referrer"/>
  <xsl:param name="lang">
    <xsl:call-template name="l10n.language"/>
  </xsl:param>

  <xsl:variable name="localization.node" 
    select="document(concat('l10n/', $lang, '.xml'))/l:l10n"/>

  <xsl:if test="count($localization.node) = 0">
    <xsl:message>
      <xsl:text>gentext.template: No "</xsl:text>
      <xsl:value-of select="$lang"/>
      <xsl:text>" localization exists.</xsl:text>
    </xsl:message>
  </xsl:if>

  <xsl:variable name="context.node"
                select="$localization.node/l:context[@name=$context]"/>

  <xsl:if test="count($context.node) = 0">
    <xsl:message>
      <xsl:text>gentext.template: No context named "</xsl:text>
      <xsl:value-of select="$context"/>
      <xsl:text>" exists in the "</xsl:text>
      <xsl:value-of select="$lang"/>
      <xsl:text>" localization.</xsl:text>
    </xsl:message>
  </xsl:if>

  <xsl:variable name="template.node"
                select="($context.node/l:template[@name=$name
                                                  and @style
                                                  and @style=$xrefstyle]
                        |$context.node/l:template[@name=$name
                                                  and not(@style)])[1]"/>

  <xsl:choose>
    <xsl:when test="$template.node/@text">
      <xsl:value-of select="$template.node/@text"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="contains($name, '/')">
          <xsl:call-template name="gentext.template">
            <xsl:with-param name="context" select="$context"/>
            <xsl:with-param name="name" select="substring-after($name, '/')"/>
            <xsl:with-param name="origname" select="$origname"/>
            <xsl:with-param name="purpose" select="$purpose"/>
            <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
            <xsl:with-param name="referrer" select="$referrer"/>
            <xsl:with-param name="lang" select="$lang"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:message>
            <xsl:text>gentext.template: No template for "</xsl:text>
            <xsl:value-of select="$origname"/>
            <xsl:text>" (or any of its leaves) exists
in the context named "</xsl:text>
            <xsl:value-of select="$context"/>
            <xsl:text>" in the "</xsl:text>
            <xsl:value-of select="$lang"/>
            <xsl:text>" localization.</xsl:text>
          </xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="gentext.template.exists"/>
<xsl:template name="gentext.template.exists" dtm:id="gentext.template.exists">
  <xsl:param name="context" select="'default'"/>
  <xsl:param name="name" select="'default'"/>
  <xsl:param name="origname" select="$name"/>
  <xsl:param name="purpose"/>
  <xsl:param name="xrefstyle"/>
  <xsl:param name="referrer"/>
  <xsl:param name="lang">
    <xsl:call-template name="l10n.language"/>
  </xsl:param>

  <xsl:variable name="localization.node" 
    select="document(concat('l10n/', $lang, '.xml'))/l:l10n"/>
  
  <xsl:variable name="context.node"
                select="$localization.node/l:context[@name=$context]"/>

  <xsl:variable name="template.node"
                select="($context.node/l:template[@name=$name
                                                  and @style
                                                  and @style=$xrefstyle]
                        |$context.node/l:template[@name=$name
                                                  and not(@style)])[1]"/>

  <xsl:choose>
    <xsl:when test="$template.node/@text">1</xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="contains($name, '/')">
          <xsl:call-template name="gentext.template.exists">
            <xsl:with-param name="context" select="$context"/>
            <xsl:with-param name="name" select="substring-after($name, '/')"/>
            <xsl:with-param name="origname" select="$origname"/>
            <xsl:with-param name="purpose" select="$purpose"/>
            <xsl:with-param name="xrefstyle" select="$xrefstyle"/>
            <xsl:with-param name="referrer" select="$referrer"/>
            <xsl:with-param name="lang" select="$lang"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>

