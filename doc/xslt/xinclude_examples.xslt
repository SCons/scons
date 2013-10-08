<?xml version="1.0" encoding="UTF-8"?>
<!-- 
  Changing example command outputs to XIncludes for the UserGuide.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" 
                              xmlns:scons="http://www.scons.org/dbxsd/v1.0"
                              xmlns:xsi="http://www.w3.org/2001/XInclude">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>

  <!-- Copy everything unmatched -->
  <xsl:template match="*">
    <xsl:element name="{name()}" namespace="{namespace-uri()}">
      <xsl:copy-of select="@*"/>      
      <xsl:apply-templates select="node()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="text() | comment() | processing-instruction()">
    <xsl:copy/>
  </xsl:template>

  <!-- Changing scons_output to xinclude -->
  <xsl:template match="scons:scons_output">
    <xsl:element name="xsi:include">
      <xsl:attribute name="href"><xsl:value-of select="concat('../generated/examples/',@example,'_',@suffix,'.xml')"></xsl:value-of></xsl:attribute>
    </xsl:element>
  </xsl:template>

  <!-- Changing scons_example_file to xinclude -->
  <xsl:template match="scons:scons_example_file">
    <xsl:variable name="newfile" select="translate(@name,'/','_')"/>
    <xsl:element name="programlisting">
      <xsl:element name="xsi:include">
        <xsl:attribute name="href"><xsl:value-of select="concat('../generated/examples/',@example,'_',$newfile)"></xsl:value-of></xsl:attribute>
        <xsl:attribute name="parse">text</xsl:attribute>
      </xsl:element>
    </xsl:element>
  </xsl:template>
 
</xsl:stylesheet>
