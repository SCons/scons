<?xml version='1.0'?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY RE "&#10;">
<!ENTITY nbsp "&#160;">
]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dtm="http://syntext.com/Extensions/DocumentTypeMetadata-1.0"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                extension-element-prefixes="dtm"
                version='1.0'>

<dtm:doc dtm:idref="cmdsynopsis"/>
<xsl:template match="cmdsynopsis" dtm:id="cmdsynopsis">
  <fo:block>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="cmdsynopsis.command"/>
<xsl:template match="cmdsynopsis/command" dtm:id="cmdsynopsis.command">
  <xsl:call-template name="inline.monoseq"/>
  <xsl:text> </xsl:text>
</xsl:template>

<dtm:doc dtm:idref="cmdsynopsis.command[1]"/>
<xsl:template match="cmdsynopsis/command[1]" priority="2" dtm:id="cmdsynopsis.command[1]">
  <xsl:call-template name="inline.monoseq"/>
  <xsl:text> </xsl:text>
</xsl:template>

<dtm:doc dtm:idref="grouporarg"/>
<xsl:template match="group|arg" name="group-or-arg" dtm:id="grouporarg">
  <xsl:variable name="choice" select="@choice"/>
  <xsl:variable name="rep" select="@rep"/>
  <xsl:variable name="sepchar">
    <xsl:choose>
      <xsl:when test="ancestor-or-self::*/@sepchar">
        <xsl:value-of select="ancestor-or-self::*/@sepchar"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text> </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <fo:inline>
    <xsl:if test="node()">
    <xsl:if test="position()>1"><xsl:value-of select="$sepchar"/></xsl:if>
    <xsl:choose>
      <xsl:when test="$choice='plain'">
        <xsl:value-of select="$arg.choice.plain.open.str"/>
      </xsl:when>
      <xsl:when test="$choice='req'">
        <xsl:value-of select="$arg.choice.req.open.str"/>
      </xsl:when>
      <xsl:when test="$choice='opt'">
        <xsl:value-of select="$arg.choice.opt.open.str"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$arg.choice.def.open.str"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when test="$rep='repeat'">
        <xsl:value-of select="$arg.rep.repeat.str"/>
      </xsl:when>
      <xsl:when test="$rep='norepeat'">
        <xsl:value-of select="$arg.rep.norepeat.str"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$arg.rep.def.str"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test="$choice='plain'">
        <xsl:value-of select="$arg.choice.plain.close.str"/>
      </xsl:when>
      <xsl:when test="$choice='req'">
        <xsl:value-of select="$arg.choice.req.close.str"/>
      </xsl:when>
      <xsl:when test="$choice='opt'">
        <xsl:value-of select="$arg.choice.opt.close.str"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$arg.choice.def.close.str"/>
      </xsl:otherwise>
    </xsl:choose>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="arg.group"/>
<xsl:template match="group/arg" dtm:id="arg.group">
  <xsl:variable name="choice" select="@choice"/>
  <xsl:variable name="rep" select="@rep"/>
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="position()>1"><xsl:value-of select="$arg.or.sep"/></xsl:if>
    </xsl:if>
    <xsl:call-template name="group-or-arg"/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="sbr"/>
<xsl:template match="sbr" dtm:id="sbr">
  <fo:block><xsl:text> </xsl:text></fo:block>
</xsl:template>

<!-- ==================================================================== -->

<dtm:doc dtm:idref="synopfragmentref"/>
<xsl:template match="synopfragmentref" dtm:id="synopfragmentref">
  <xsl:variable name="ref" select="id(@linkend)"/>
  <fo:inline font-style="italic">
    <xsl:for-each select="$ref/parent::*[1]/synopfragment">
      <xsl:if test="self::synopfragment/@id = $ref/@id">
        <xsl:text>(</xsl:text>
        <xsl:value-of select="position()"/>
        <xsl:text>)</xsl:text> 
      </xsl:if>
    </xsl:for-each>
    <xsl:text>&#160;</xsl:text>
    <xsl:apply-templates/>
  </fo:inline>
</xsl:template>

<xsl:template match="synopfragment" mode="synopfragment.number" dtm:id="synopfragment.number">
  <xsl:number format="1"/>
</xsl:template>

<dtm:doc dtm:elements="synopfragment" dtm:idref="synopfragment synopfragment.number"/>
<xsl:template match="synopfragment" dtm:id="synopfragment">
  <xsl:variable name="snum">
    <xsl:apply-templates select="." mode="synopfragment.number"/>
  </xsl:variable>
  <fo:block>
    <xsl:text>(</xsl:text>
    <xsl:value-of select="$snum"/>
    <xsl:text>)</xsl:text>
    <xsl:text> </xsl:text>
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="funcsynopsis"/>
<xsl:template match="funcsynopsis" dtm:id="funcsynopsis">
  <xsl:call-template name="informal.object"/>
</xsl:template>

<dtm:doc dtm:idref="funcsynopsisinfo"/>
<xsl:template match="funcsynopsisinfo" dtm:id="funcsynopsisinfo">
  <fo:block padding-bottom="1em">
    <xsl:apply-templates/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="funcprototype"/>
<xsl:template match="funcprototype" dtm:id="funcprototype">
  <fo:block font-family="{$monospace.font.family}">
    <xsl:apply-templates/>
    <xsl:if test="$funcsynopsis.style='kr'">
      <xsl:apply-templates select="./paramdef" mode="kr-funcsynopsis-mode"/>
    </xsl:if>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="funcdef"/>
<xsl:template match="funcdef" dtm:id="funcdef">
  <fo:inline font-family="{$monospace.font.family}">
    <xsl:apply-templates/>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="funcdef.function"/>
<xsl:template match="funcdef/function" dtm:id="funcdef.function">
  <xsl:choose>
    <xsl:when test="$funcsynopsis.decoration != 0">
      <fo:inline font-weight="bold">
        <xsl:apply-templates/>
      </fo:inline>
    </xsl:when>
    <xsl:otherwise>
      <fo:inline><xsl:apply-templates/></fo:inline>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="void"/>
<xsl:template match="void" dtm:id="void">
  <xsl:choose>
    <xsl:when test="$funcsynopsis.style='ansi'">
      <xsl:text>(void);</xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text>();</xsl:text>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<dtm:doc dtm:idref="varargs"/>
<xsl:template match="varargs" dtm:id="varargs">
  <xsl:text>(...);</xsl:text>
</xsl:template>

<dtm:doc dtm:idref="paramdef paramdef.funcsynopsys.mode"/>
<xsl:template match="paramdef" dtm:id="paramdef">
  <xsl:variable name="paramnum">
    <xsl:number count="paramdef" format="1"/>
  </xsl:variable>
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="$paramnum=1">(</xsl:if>
      <xsl:choose>
        <xsl:when test="$funcsynopsis.style='ansi'">
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="./parameter"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:choose>
        <xsl:when test="following-sibling::paramdef">
          <xsl:text>, </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>);</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="paramdef.parameter"/>
<xsl:template match="paramdef/parameter" dtm:id="paramdef.parameter">
  <fo:inline>
    <xsl:choose>
      <xsl:when test="$funcsynopsis.decoration != 0">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="following-sibling::parameter">
      <xsl:text>, </xsl:text>
    </xsl:if>
  </fo:inline>
</xsl:template>

<xsl:template match="paramdef" mode="kr-funcsynopsis-mode" dtm:id="paramdef.funcsynopsys.mode">
  <fo:block>
    <xsl:apply-templates/>
    <xsl:text>;</xsl:text>
  </fo:block>
</xsl:template>

<dtm:doc dtm:idref="funcparams"/>
<xsl:template match="funcparams" dtm:id="funcparams">
  <fo:inline>
    <xsl:if test="node()">
    <xsl:text>(</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>)</xsl:text>
    </xsl:if>
  </fo:inline>
</xsl:template>

<!-- ==================================================================== -->

<xsl:variable name="default-classsynopsis-language">java</xsl:variable>

<dtm:doc dtm:idref="synopsises"/>
<xsl:template match="classsynopsis
                     |fieldsynopsis
                     |methodsynopsis
                     |constructorsynopsis
                     |destructorsynopsis" dtm:id="synopsises">
  <xsl:param name="language">
    <xsl:choose>
      <xsl:when test="@language">
	<xsl:value-of select="@language"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="$default-classsynopsis-language"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:choose>
    <xsl:when test="$language='java'">
      <xsl:apply-templates select="." mode="java"/>
    </xsl:when>
    <xsl:when test="$language='perl'">
      <xsl:apply-templates select="." mode="perl"/>
    </xsl:when>
    <xsl:when test="$language='idl'">
      <xsl:apply-templates select="." mode="idl"/>
    </xsl:when>
    <xsl:when test="$language='cpp'">
      <xsl:apply-templates select="." mode="cpp"/>
    </xsl:when>
    <xsl:otherwise>
      <fo:block>
        <xsl:text>Unrecognized language on </xsl:text>
        <xsl:value-of select="name(.)"/>
        <xsl:text>: </xsl:text>
        <xsl:value-of select="$language"/>
        
        <xsl:apply-templates select=".">
          <xsl:with-param name="language"
            select="$default-classsynopsis-language"/>
        </xsl:apply-templates>
      </fo:block>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="synop-break">
  <xsl:if test="(parent::classsynopsis
                or (following-sibling::fieldsynopsis
                    |following-sibling::methodsynopsis
                    |following-sibling::constructorsynopsis
                    |following-sibling::destructorsynopsis)) and node()">
    <xsl:text>&RE;</xsl:text>
  </xsl:if>
</xsl:template>

<!-- ===== Java ======================================================== -->

<dtm:doc dtm:elements="classsynopsis" dtm:idref="classsynopsis.java classsynopsis.cpp classsynopsis.idl classsynopsis.perl"/>
<xsl:template match="classsynopsis" mode="java" dtm:id="classsynopsis.java">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:apply-templates select="ooclass[1]" mode="java"/>
    <xsl:if test="ooclass[position() &gt; 1]">
      <xsl:text> extends</xsl:text>
      <xsl:apply-templates select="ooclass[position() &gt; 1]" mode="java"/>
      <xsl:if test="oointerface|ooexception">
        <xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="oointerface">
      <xsl:text>implements</xsl:text>
      <xsl:apply-templates select="oointerface" mode="java"/>
      <xsl:if test="ooexception">
	<xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="ooexception">
      <xsl:text>throws</xsl:text>
      <xsl:apply-templates select="ooexception" mode="java"/>
    </xsl:if>
    <xsl:text>&nbsp;{&RE;</xsl:text>
    <xsl:apply-templates select="classname
                                 |extends
                                 |implements
                                 |indexterm
                                 |members
                                 |modifiers
                                 |throws
                                 |type
                                 |constructorsynopsis
                                 |destructorsynopsis
                                 |fieldsynopsis
                                 |methodsynopsis
                                 |classsynopsisinfo
                                 |processing-instruction('se:choice')" mode="java"/>
    <xsl:text>}</xsl:text>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="classsynopsisinfo" dtm:idref="classsynopsisinfo.java classsynopsisinfo.cpp classsynopsisinfo.idl classsynopsisinfo.perl"/>
<xsl:template match="classsynopsisinfo" mode="java" dtm:id="classsynopsisinfo.java">
  <fo:block>
    <xsl:apply-templates mode="java"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="ooclass|oointerface|ooexception" dtm:idref="ooelements.java ooelements.cpp ooelements.idl ooelements.perl"/>
<xsl:template match="ooclass|oointerface|ooexception" mode="java" dtm:id="ooelements.java">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:choose>
        <xsl:when test="position() &gt; 1">
          <xsl:text>, </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text> </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates mode="java"/>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:idref="meitt.java"/>
<xsl:template match="modifiers|extends|implements|throws|type" mode="java" dtm:id="meitt.java">
  <fo:inline>
    <xsl:apply-templates mode="java"/>
    <xsl:text>&nbsp;</xsl:text>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="classname" dtm:idref="classname.java classname.cpp classname.idl classname.perl"/>
<xsl:template match="classname" mode="java" dtm:id="classname.java">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="name(preceding-sibling::*[1]) = 'classname'">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:apply-templates mode="java"/>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="interfacename" dtm:idref="interfacename.java interfacename.cpp interfacename.idl interfacename.perl"/>
<xsl:template match="interfacename" mode="java" dtm:id="interfacename.java">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="name(preceding-sibling::*[1]) = 'interfacename'">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:apply-templates mode="java"/>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="exceptionname" dtm:idref="exceptionname.java exceptionname.cpp exceptionname.idl exceptionname.perl"/>
<xsl:template match="exceptionname" mode="java" dtm:id="exceptionname.java">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="name(preceding-sibling::*[1]) = 'exceptionname'">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:apply-templates mode="java"/>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="fieldsynopsis" dtm:idref="fieldsynopsis.java fieldsynopsis.cpp fieldsynopsis.idl fieldsynopsis.perl"/>
<xsl:template match="fieldsynopsis" mode="java" dtm:id="fieldsynopsis.java">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>&nbsp;&nbsp;</xsl:text>
    <xsl:apply-templates mode="java"/>
    <xsl:text>;</xsl:text>
    <xsl:call-template name="synop-break"/>
  </fo:block>
</xsl:template>

<dtm:doc dtm:elements="varname" dtm:idref="varname.java varname.cpp varname.idl varname.perl"/>
<xsl:template match="varname" mode="java" dtm:id="varname.java">
  <xsl:apply-templates mode="java"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<dtm:doc dtm:elements="initializer" dtm:idref="initializer.java initializer.cpp initializer.idl initializer.perl"/>
<xsl:template match="initializer" mode="java" dtm:id="initializer.java">
  <xsl:text>=&nbsp;</xsl:text>
  <xsl:apply-templates mode="java"/>
</xsl:template>

<dtm:doc dtm:elements="void" dtm:idref="void.java void.cpp void.idl void.perl"/>
<xsl:template match="void" mode="java" dtm:id="void.java">
  <xsl:text>void&nbsp;</xsl:text>
</xsl:template>

<dtm:doc dtm:elements="methodname" dtm:idref="methodname.java methodname.cpp methodname.idl methodname.perl"/>
<xsl:template match="methodname" mode="java" dtm:id="methodname.java">
  <xsl:apply-templates mode="java"/>
</xsl:template>

<dtm:doc dtm:elements="methodparam" dtm:idref="methodparam.java methodparam.cpp methodparam.idl methodparam.perl"/>
<xsl:template match="methodparam" mode="java" dtm:id="methodparam.java">
  <xsl:param name="indent">0</xsl:param>
  <xsl:if test="position() &gt; 1">
    <xsl:text>,&RE;</xsl:text>
    <xsl:if test="$indent &gt; 0">
      <xsl:call-template name="copy-string">
	<xsl:with-param name="string">&nbsp;</xsl:with-param>
	<xsl:with-param name="count" select="$indent + 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:if>
  <xsl:apply-templates mode="java"/>
</xsl:template>

<dtm:doc dtm:elements="parameter" dtm:idref="parameter.java parameter.cpp parameter.idl parameter.perl"/>
<xsl:template match="parameter" mode="java" dtm:id="parameter.java">
  <xsl:apply-templates mode="java"/>
</xsl:template>

<dtm:doc dtm:elements="constructorsynopsis|destructorsynopsis|methodsynopsis" dtm:idref="synopsises.java synopsises.cpp synopsises.idl synopsises.perl"/>
<xsl:template mode="java"
  match="constructorsynopsis|destructorsynopsis|methodsynopsis" dtm:id="synopsises.java">
  <xsl:variable name="modifiers" select="modifier"/>
  <xsl:variable name="notmod" select="*[name(.) != 'modifier']"/>
  <xsl:variable name="decl">
    <xsl:text>  </xsl:text>
    <xsl:apply-templates select="$modifiers" mode="java"/>

    <!-- type -->
    <xsl:if test="name($notmod[1]) != 'methodname'">
      <xsl:apply-templates select="$notmod[1]" mode="java"/>
    </xsl:if>

    <xsl:apply-templates select="methodname" mode="java"/>
  </xsl:variable>

  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:copy-of select="$decl"/>
    <xsl:text>(</xsl:text>
    <xsl:apply-templates select="methodparam" mode="java">
      <xsl:with-param name="indent" select="string-length($decl)"/>
    </xsl:apply-templates>
    <xsl:text>)</xsl:text>
    <xsl:if test="exceptionname">
      <xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;throws&nbsp;</xsl:text>
      <xsl:apply-templates select="exceptionname" mode="java"/>
    </xsl:if>
    <xsl:text>;</xsl:text>
  </fo:block>
  <xsl:call-template name="synop-break"/>
</xsl:template>

<!-- ===== C++ ========================================================= -->

<xsl:template match="classsynopsis" mode="cpp" dtm:id="classsynopsis.cpp">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:apply-templates select="ooclass[1]" mode="cpp"/>
    <xsl:if test="ooclass[position() &gt; 1]">
      <xsl:text>: </xsl:text>
      <xsl:apply-templates select="ooclass[position() &gt; 1]" mode="cpp"/>
      <xsl:if test="oointerface|ooexception">
	<xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="oointerface">
      <xsl:text> implements</xsl:text>
      <xsl:apply-templates select="oointerface" mode="cpp"/>
      <xsl:if test="ooexception">
	<xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="ooexception">
      <xsl:text> throws</xsl:text>
      <xsl:apply-templates select="ooexception" mode="cpp"/>
    </xsl:if>
    <xsl:if test="constructorsynopsis
                                 |destructorsynopsis
                                 |fieldsynopsis
                                 |methodsynopsis
                                 |classsynopsisinfo">
      <xsl:text>&nbsp;{&RE;</xsl:text>
      <xsl:apply-templates select="constructorsynopsis
                                   |destructorsynopsis
                                   |fieldsynopsis
                                   |methodsynopsis
                                   |classsynopsisinfo" mode="cpp"/>
      <xsl:text>}</xsl:text>
    </xsl:if>
  </fo:block>
</xsl:template>

<xsl:template match="classsynopsisinfo" mode="cpp" dtm:id="classsynopsisinfo.cpp">
  <xsl:apply-templates mode="cpp"/>
</xsl:template>

<xsl:template match="ooclass|oointerface|ooexception" mode="cpp" dtm:id="ooelements.cpp">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="position() &gt; 1">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:apply-templates mode="cpp"/>
    </xsl:if>
  </fo:inline>
</xsl:template>

<dtm:doc dtm:elements="modifier" dtm:idref="modifier.cpp modifier.idl modifier.perl"/>
<xsl:template match="modifier" mode="cpp" dtm:id="modifier.cpp">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:apply-templates mode="cpp"/>
      <xsl:text>&nbsp;</xsl:text>
    </xsl:if>
  </fo:inline>
</xsl:template>

<xsl:template match="classname" mode="cpp" dtm:id="classname.cpp">
  <fo:inline>
    <xsl:if test="node()">
      <xsl:if test="name(preceding-sibling::*[1]) = 'classname'">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:apply-templates mode="cpp"/>
    </xsl:if>
  </fo:inline>
</xsl:template>

<xsl:template match="interfacename" mode="cpp" dtm:id="interfacename.cpp">
  <xsl:if test="name(preceding-sibling::*[1]) = 'interfacename'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="cpp"/>
</xsl:template>

<xsl:template match="exceptionname" mode="cpp" dtm:id="exceptionname.cpp">
  <xsl:if test="name(preceding-sibling::*[1]) = 'exceptionname'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="cpp"/>
</xsl:template>

<xsl:template match="fieldsynopsis" mode="cpp" dtm:id="fieldsynopsis.cpp">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>&nbsp;&nbsp;</xsl:text>
    <xsl:apply-templates mode="cpp"/>
    <xsl:text>;</xsl:text>
  </fo:block>
  <xsl:call-template name="synop-break"/>
</xsl:template>

<dtm:doc dtm:elements="type" dtm:idref="type.cpp type.idl type.perl"/>
<xsl:template match="type" mode="cpp" dtm:id="type.cpp">
<fo:inline>
  <xsl:if test="node()">
    <xsl:apply-templates mode="cpp"/>
  <xsl:text>&nbsp;</xsl:text>
  </xsl:if>
</fo:inline>
</xsl:template>

<xsl:template match="varname" mode="cpp" dtm:id="varname.cpp">
  <xsl:apply-templates mode="cpp"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="initializer" mode="cpp" dtm:id="initializer.cpp">
<fo:inline>
  <xsl:if test="node()">
  <xsl:text>=&nbsp;</xsl:text>
  <xsl:apply-templates mode="cpp"/>
  </xsl:if>
</fo:inline>
</xsl:template>

<xsl:template match="void" mode="cpp" dtm:id="void.cpp">
  <fo:inline><xsl:text>void&nbsp;</xsl:text></fo:inline>
</xsl:template>

<xsl:template match="methodname" mode="cpp" dtm:id="methodname.cpp">
  <fo:inline><xsl:apply-templates mode="cpp"/></fo:inline>
</xsl:template>

<xsl:template match="methodparam" mode="cpp" dtm:id="methodparam.cpp">
  <fo:inline>
  <xsl:if test="(position() &gt; 1) and node()">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="cpp"/>
  </fo:inline>
</xsl:template>

<xsl:template match="parameter" mode="cpp" dtm:id="parameter.cpp">
  <fo:inline>
    <xsl:apply-templates mode="cpp"/>
  </fo:inline>
</xsl:template>

<xsl:template mode="cpp"
  match="constructorsynopsis|destructorsynopsis|methodsynopsis" dtm:id="synopsises.cpp">
  <xsl:variable name="modifiers" select="modifier"/>
  <xsl:variable name="notmod" select="*[name(.) != 'modifier']"/>

  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:if test="node()">
      <xsl:text>  </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="$modifiers" mode="cpp"/>

    <!-- type -->
    <xsl:if test="name($notmod[1]) != 'methodname'">
      <xsl:apply-templates select="$notmod[1]" mode="cpp"/>
    </xsl:if>

    <xsl:apply-templates select="methodname" mode="cpp"/>
    <xsl:if test="methodparam">
      <xsl:text>(</xsl:text>
      <xsl:apply-templates select="methodparam" mode="cpp"/>
      <xsl:text>)</xsl:text>
    </xsl:if>
    <xsl:if test="exceptionname">
      <xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;throws&nbsp;</xsl:text>
      <xsl:apply-templates select="exceptionname" mode="cpp"/>
    </xsl:if>
    <xsl:if test="node()">
      <xsl:text>;</xsl:text>
    </xsl:if>
  <xsl:call-template name="synop-break"/>
  </fo:block>
</xsl:template>

<!-- ===== IDL ========================================================= -->

<xsl:template match="classsynopsis" mode="idl" dtm:id="classsynopsis.idl">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>interface </xsl:text>
    <xsl:apply-templates select="ooclass[1]" mode="idl"/>
    <xsl:if test="ooclass[position() &gt; 1]">
      <xsl:text>: </xsl:text>
      <xsl:apply-templates select="ooclass[position() &gt; 1]" mode="idl"/>
      <xsl:if test="oointerface|ooexception">
	<xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="oointerface">
      <xsl:text> implements</xsl:text>
      <xsl:apply-templates select="oointerface" mode="idl"/>
      <xsl:if test="ooexception">
	<xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="ooexception">
      <xsl:text> throws</xsl:text>
      <xsl:apply-templates select="ooexception" mode="idl"/>
    </xsl:if>
    <xsl:text>&nbsp;{&RE;</xsl:text>
    <xsl:apply-templates select="constructorsynopsis
                                 |destructorsynopsis
                                 |fieldsynopsis
                                 |methodsynopsis
                                 |classsynopsisinfo" mode="idl"/>
    <xsl:text>}</xsl:text>
  </fo:block>
</xsl:template>

<xsl:template match="classsynopsisinfo" mode="idl" dtm:id="classsynopsisinfo.idl">
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="ooclass|oointerface|ooexception" mode="idl" dtm:id="ooelements.idl">
  <xsl:if test="position() &gt; 1">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="modifier" mode="idl" dtm:id="modifier.idl">
  <xsl:apply-templates mode="idl"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="classname" mode="idl" dtm:id="classname.idl">
  <xsl:if test="name(preceding-sibling::*[1]) = 'classname'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="interfacename" mode="idl" dtm:id="interfacename.idl">
  <xsl:if test="name(preceding-sibling::*[1]) = 'interfacename'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="exceptionname" mode="idl" dtm:id="exceptionname.idl">
  <xsl:if test="name(preceding-sibling::*[1]) = 'exceptionname'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="fieldsynopsis" mode="idl" dtm:id="fieldsynopsis.idl">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>&nbsp;&nbsp;</xsl:text>
    <xsl:apply-templates mode="idl"/>
    <xsl:text>;</xsl:text>
  </fo:block>
  <xsl:call-template name="synop-break"/>
</xsl:template>

<xsl:template match="type" mode="idl" dtm:id="type.idl">
  <xsl:apply-templates mode="idl"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="varname" mode="idl" dtm:id="varname.idl">
  <xsl:apply-templates mode="idl"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="initializer" mode="idl" dtm:id="initializer.idl">
  <xsl:text>=&nbsp;</xsl:text>
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="void" mode="idl" dtm:id="void.idl">
  <xsl:text>void&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="methodname" mode="idl" dtm:id="methodname.idl">
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="methodparam" mode="idl" dtm:id="methodparam.idl">
  <xsl:if test="position() &gt; 1">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template match="parameter" mode="idl" dtm:id="parameter.idl">
  <xsl:apply-templates mode="idl"/>
</xsl:template>

<xsl:template mode="idl"
  match="constructorsynopsis|destructorsynopsis|methodsynopsis" dtm:id="synopsises.idl">
  <xsl:variable name="modifiers" select="modifier"/>
  <xsl:variable name="notmod" select="*[name(.) != 'modifier']"/>

  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>  </xsl:text>
    <xsl:apply-templates select="$modifiers" mode="idl"/>

    <!-- type -->
    <xsl:if test="name($notmod[1]) != 'methodname'">
      <xsl:apply-templates select="$notmod[1]" mode="idl"/>
    </xsl:if>

    <xsl:apply-templates select="methodname" mode="idl"/>
    <xsl:text>(</xsl:text>
    <xsl:apply-templates select="methodparam" mode="idl"/>
    <xsl:text>)</xsl:text>
    <xsl:if test="exceptionname">
      <xsl:text>&RE;&nbsp;&nbsp;&nbsp;&nbsp;raises(</xsl:text>
      <xsl:apply-templates select="exceptionname" mode="idl"/>
      <xsl:text>)</xsl:text>
    </xsl:if>
    <xsl:text>;</xsl:text>
  </fo:block>
  <xsl:call-template name="synop-break"/>
</xsl:template>

<!-- ===== Perl ======================================================== -->

<xsl:template match="classsynopsis" mode="perl" dtm:id="classsynopses.perl">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>package </xsl:text>
    <xsl:apply-templates select="ooclass[1]" mode="perl"/>
    <xsl:text>;&RE;</xsl:text>

    <xsl:if test="ooclass[position() &gt; 1]">
      <xsl:text>@ISA = (</xsl:text>
      <xsl:apply-templates select="ooclass[position() &gt; 1]" mode="perl"/>
      <xsl:text>);&RE;</xsl:text>
    </xsl:if>

    <xsl:apply-templates select="constructorsynopsis
                                 |destructorsynopsis
                                 |fieldsynopsis
                                 |methodsynopsis
                                 |classsynopsisinfo" mode="perl"/>
  </fo:block>
</xsl:template>

<xsl:template match="classsynopsisinfo" mode="perl" dtm:id="classsynopsesinfo.perl">
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="ooclass|oointerface|ooexception" mode="perl" dtm:id="ooelements.perl">
  <xsl:if test="position() &gt; 1">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="modifier" mode="perl" dtm:id="modifier.perl">
  <xsl:apply-templates mode="perl"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="classname" mode="perl" dtm:id="classname.perl">
  <xsl:if test="name(preceding-sibling::*[1]) = 'classname'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="interfacename" mode="perl" dtm:id="interfacename.perl">
  <xsl:if test="name(preceding-sibling::*[1]) = 'interfacename'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="exceptionname" mode="perl" dtm:id="exceptionname.perl">
  <xsl:if test="name(preceding-sibling::*[1]) = 'exceptionname'">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="fieldsynopsis" mode="perl" dtm:id="fieldsynopsis.perl">
  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>&nbsp;&nbsp;</xsl:text>
    <xsl:apply-templates mode="perl"/>
    <xsl:text>;</xsl:text>
  </fo:block>
  <xsl:call-template name="synop-break"/>
</xsl:template>

<xsl:template match="type" mode="perl" dtm:id="type.perl">
  <xsl:apply-templates mode="perl"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="varname" mode="perl" dtm:id="varname.perl">
  <xsl:apply-templates mode="perl"/>
  <xsl:text>&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="initializer" mode="perl" dtm:id="initializer.perl">
  <xsl:text>=&nbsp;</xsl:text>
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="void" mode="perl" dtm:id="void.perl">
  <xsl:text>void&nbsp;</xsl:text>
</xsl:template>

<xsl:template match="methodname" mode="perl" dtm:id="methodname.perl">
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="methodparam" mode="perl" dtm:id="methodparam.perl">
  <xsl:if test="position() &gt; 1">
    <xsl:text>, </xsl:text>
  </xsl:if>
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template match="parameter" mode="perl" dtm:id="parameter.perl">
  <xsl:apply-templates mode="perl"/>
</xsl:template>

<xsl:template mode="perl"
  match="constructorsynopsis|destructorsynopsis|methodsynopsis" dtm:id="synopsises.perl">
  <xsl:variable name="modifiers" select="modifier"/>
  <xsl:variable name="notmod" select="*[name(.) != 'modifier']"/>

  <fo:block 
            white-space-collapse='false'
            linefeed-treatment="preserve"
            xsl:use-attribute-sets="monospace.verbatim.properties">
    <xsl:text>sub </xsl:text>

    <xsl:apply-templates select="methodname" mode="perl"/>
    <xsl:text> { ... };</xsl:text>
    <xsl:call-template name="synop-break"/>
  </fo:block>
</xsl:template>

<!-- ==================================================================== -->

</xsl:stylesheet>
