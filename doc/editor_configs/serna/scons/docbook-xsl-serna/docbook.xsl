<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                extension-element-prefixes="xse"
                version='1.0'>
<!-- 

     DocBook XSL Stylesheet for Syntext Serna (c) 2003, Syntext Inc.

     The Stylesheet is based on Norman Walsh XSL DocBook Stylesheet 
     distribution. See file NW-COPYING for Norman Walsh Copyright 
     information.

-->
  <xsl:import href="http://www.syntext.com/xslbricks-1.0/fo/fonts.xsl"/>
  <xsl:import href="http://www.syntext.com/xslbricks-1.0/fo/common.xsl"/>
  <xsl:import href="http://www.syntext.com/xslbricks-1.0/fo/layoutsetup.xsl"/>
  <xsl:import href="http://www.syntext.com/xslbricks-1.0/fo/default-elements.xsl"/>
  <xsl:import href="http://www.syntext.com/xslbricks-1.0/fo/page-sizes.xsl"/>

  <xsl:include href="table.xsl" xse:alt-href="serna-table.xsl"/>
  <xsl:include href="titlepage.templates.xsl"/>
  <xsl:include href="titlepage.xsl"/>

  <xsl:include href="parameters.xsl"/>
  <xsl:include href="divisions.xsl"/>
  <xsl:include href="compounds.xsl"/>
  <xsl:include href="common.xsl"/>
  <xsl:include href="blocks.xsl"/>
  <xsl:include href="inlines.xsl"/>
  <xsl:include href="glossary.xsl"/>

  <xsl:include href="l10n.xsl"/>

  <xsl:include href="titles.xsl"/>
  <xsl:include href="refentry.xsl"/>
  <xsl:include href="synopsis.xsl"/>
  <xsl:include href="formal.xsl"/>
  <xsl:include href="graphics.xsl"/>
  <xsl:include href="qandaset.xsl"/>
  <xsl:include href="biblio.xsl"/>
  <xsl:include href="lists.xsl"/>
  <xsl:include href="xref.xsl"/>


  <xsl:include href="toc.titles.xsl"/>
  <xsl:include href="toc.labels.xsl"/>
  <xsl:include href="toc.xsl"/>

  <xsl:output method="xml"/>
  <xsl:strip-space elements="*"/>
  <xsl:preserve-space elements="programlisting screen para synopsis literallayout sconstruct scons_example_file example_commands scons_output_command file directory"/>
</xsl:stylesheet>
