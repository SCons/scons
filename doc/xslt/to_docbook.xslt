<?xml version="1.0" encoding="UTF-8"?>
<!-- 
  Changing element names from SCons XSD to real Docbook.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                              xmlns:fo="http://www.w3.org/1999/XSL/Format" 
                              xmlns:scons="http://www.scons.org/dbxsd/v1.0">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
 
  <!-- Copy everything unmatched -->
  <xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:copy-of select="@*"/>      
      <xsl:apply-templates select="node()"/>
    </xsl:element>
  </xsl:template>
 
  <xsl:template match="text() | comment() | processing-instruction()">
    <xsl:copy/>
  </xsl:template>

  <!-- Leaving scons_example empty -->
  <xsl:template match="scons:scons_example">
    <xsl:apply-templates select="node()"/>
  </xsl:template>
 
  <!-- Changing example_commands to screen -->
  <xsl:template match="scons:example_commands">
    <xsl:element name="screen">
      <xsl:apply-templates select="node()"/>
    </xsl:element>
  </xsl:template>

  <!-- Changing scons_output to screen -->
  <xsl:template match="scons:scons_output">
    <xsl:element name="screen">
      <xsl:apply-templates select="node()"/>
    </xsl:element>
  </xsl:template>

  <!-- Leaving scons_output_command empty, should already
       have been handled by xinclude_examples.xslt.
    -->
  <xsl:template match="scons:scons_output_command">
  </xsl:template>

  <!-- Leaving scons_example_file empty, should already
       have been handled by xinclude_examples.xslt.
    -->
  <xsl:template match="scons:scons_example_file">
  </xsl:template>

  <!-- Changing file to programlisting if printme == '1' -->
  <xsl:template match="scons:file">
    <xsl:if test="@printme='1'">
      <xsl:element name="programlisting">
        <xsl:apply-templates select="node()"/>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Changing sconstruct to programlisting -->
  <xsl:template match="scons:sconstruct">
    <xsl:element name="programlisting">
      <xsl:apply-templates select="node()"/>
    </xsl:element>
  </xsl:template>

  <!-- Leave directory empty -->
  <xsl:template match="scons:directory">
  </xsl:template>
 
</xsl:stylesheet>
