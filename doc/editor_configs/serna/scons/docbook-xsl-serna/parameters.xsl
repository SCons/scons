<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
  version="1.0">
  <!--XSLT Params-->
  <xsl:param name="show.preamble.editing" select="1" xse:type="numeric"
    xse:annotation="Show draft areas?"/>
  <xsl:param name="appendix.autolabel" select="1" xse:type="numeric"
    xse:annotation="Are Appendixes automatically enumerated?"/>
  <xsl:param name="chapter.autolabel" select="1" xse:type="numeric"
    xse:annotation="Are chapters automatically enumerated?"/>
  <xsl:param name="part.autolabel" select="1" xse:type="numeric"
    xse:annotation="Are parts and references enumerated?"/>
  <xsl:param name="preface.autolabel" select="0" xse:type="numeric"
    xse:annotation="Are prefaces enumerated?"/>
  <xsl:param name="qandadiv.autolabel" select="1" xse:type="numeric" 
    xse:annotation="Are divisions in QAndASets enumerated?"/>
  <xsl:param name="label.from.part" select="'1'" xse:type="numeric"
    xse:annotation="Renumber chapters in each part?"/>
  <xsl:param name="section.autolabel" select="1" xse:type="numeric"
    xse:annotation="Are sections enumerated?"/>
  <xsl:param name="section.label.includes.component.label" select="1" xse:type="numeric"
    xse:annotation="Do section labels include the component label?"/>
  <xsl:param name="formal.title.placement" select="'
                   figure before 
                   example before 
                   equation before 
                   table before 
                   procedure before'" xse:type="string"
    xse:annotation="Specifies where formal object titles should occur"/>
  <xsl:param name="toc.indent.width" select="24" xse:type="numeric"
    xse:annotation="Amount of indentation for TOC entries"/>
  <xsl:param name="toc.section.depth" select="5" xse:type="numeric"
    xse:annotation="How deep should recursive sections appear in the TOC?"/>
  <xsl:param name="autotoc.label.separator" select="'. '" xse:type="string"
    xse:annotation="Separator between labels and titles in the ToC"/>
  <xsl:param name="qanda.defaultlabel" select="'number'" 
    xse:annotation="What labels do qanda entries have?" xse:type="string"/>
  <xsl:param name="qanda.inherit.numeration" select="1" xse:type="numeric"
    xse:annotation="Does enumeration of QandASet components inherit the numeration of parent elements?"/>
  <xsl:param name="variablelist.as.blocks" select="1" xse:type="numeric"
    xse:annotation="Format variablelists lists as blocks?"/>
  <!-- TOC generation table. After division keyword (e.g "part") there 
       should be a list of non-whitespace separated tokens (like "toc,lot"),
       that state what will be shown in the division. -->

  <xsl:param name="generate.toc" select="normalize-space('
                          set  toc
                          book toc
                          part toc
                          ')" xse:type="string"
    xse:annotation="Control generation of ToCs and LoTs"/>

  <!-- General -->

  <xsl:variable name="default.indent.shift" select="'20'"/>
  <xsl:param name="default.units" select="'pt'"/>
  <xsl:param name="show.remarks" select="'1'"/>
  <xsl:param name="make.single.year.ranges" select="0"/>
  <xsl:param name="make.year.ranges" select="0"/>
  <xsl:param name="punct.honorific" select="'.'"/>
  <xsl:param name="author.othername.in.middle" select="1"/>
  <xsl:param name="ignore.image.scaling" select="0"/>
  <xsl:param name="l10n.gentext.default.language" select="'en'"/>
  <xsl:param name="l10n.gentext.language" select="''"/>
  <xsl:param name="l10n.gentext.use.xref.language" select="0"/>
  <xsl:param name="formal.procedures" select="1"/>

  <xsl:param name="body.margin.bottom" select="'0.5in'"/>
  <xsl:param name="body.margin.top" select="'0.5in'"/>
  <xsl:param name="page.margin.bottom" select="'0.5in'"/>  
  <xsl:param name="page.margin.inner" select="'1in'"/>
  <xsl:param name="page.margin.outer" select="'1in'"/>
  <xsl:param name="page.margin.top" select="'0.5in'"/>
  <xsl:param name="page.margin.left" select="'1in'"/>
  <xsl:param name="page.margin.right" select="'1in'"/>
  <xsl:param name="page.orientation" select="'portrait'"/>
  <xsl:param name="paper.type" select="'A4'"/>

  <xsl:param name="body.font.size">
    <xsl:value-of select="$body.font.master"/><xsl:text>pt</xsl:text>
  </xsl:param>

  <xsl:param name="title1.font.size">
    <xsl:value-of select="$body.font.master * 2.07"/><xsl:text>pt</xsl:text>
  </xsl:param>
  <xsl:param name="title2.font.size">
    <xsl:value-of select="$body.font.master * 1.73"/><xsl:text>pt</xsl:text>
  </xsl:param>
  <xsl:param name="title3.font.size">
    <xsl:value-of select="$body.font.master * 1.2"/><xsl:text>pt</xsl:text>
  </xsl:param>
  <xsl:param name="footnote.font.size">
    <xsl:value-of select="$body.font.master * 0.7"/><xsl:text>pt</xsl:text>
  </xsl:param>

  <xsl:attribute-set name="root">
    <xsl:attribute name="font-family"><xsl:value-of select="$body.font.family"/></xsl:attribute>
    <xsl:attribute name="font-size"><xsl:value-of select="$body.font.size"/></xsl:attribute>
  </xsl:attribute-set>

  <!-- Title General -->
  <xsl:param name="title.margin.left" select="'-2pc'"/>

  <xsl:attribute-set name="title.content.properties">
    <xsl:attribute name="font-family">
      <xsl:value-of select="$title.font.family"/>
    </xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
    <xsl:attribute name="text-align">center</xsl:attribute>
    <xsl:attribute name="margin-left">
      <xsl:value-of select="$title.margin.left"/>
    </xsl:attribute>
    <xsl:attribute name="margin-right">
      <xsl:value-of select="$title.margin.left"/>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="titlepage.verso.style">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 0.8"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="preamble.attributes">
    <xsl:attribute name="border-style">solid</xsl:attribute>
    <xsl:attribute name="border-top-width">1pt</xsl:attribute>
    <xsl:attribute name="border-left-width">1pt</xsl:attribute>    
    <xsl:attribute name="border-right-width">1pt</xsl:attribute>    
    <xsl:attribute name="border-bottom-width">1pt</xsl:attribute>
    <xsl:attribute name="border-top-color">#000000</xsl:attribute>
    <xsl:attribute name="border-bottom-color">#000000</xsl:attribute>
    <xsl:attribute name="border-left-color">#000000</xsl:attribute>
    <xsl:attribute name="border-right-color">#000000</xsl:attribute>
    <xsl:attribute name="background-color">#e0e0e0</xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 0.8"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <!-- Divisions -->

  <xsl:param name="division.title.font.master">
    <xsl:value-of select="$body.font.master * 2.8"/>
  </xsl:param>

  <xsl:attribute-set name="division.title.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$division.title.font.master"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="padding-bottom">
      <xsl:value-of select="$division.title.font.master * 0.5"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="division.subtitle.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$division.title.font.master * 0.96"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="padding-bottom">
      <xsl:value-of select="$division.title.font.master * 0.5"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="book.titlepage.recto.style">
    <xsl:attribute name="font-family">
      <xsl:value-of select="$title.font.family"/>
    </xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <!-- Components -->

  <xsl:param name="component.title.font.master">
    <xsl:value-of select="$body.font.master * 2.4"/>
  </xsl:param>

  <xsl:attribute-set name="component.title.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$component.title.font.master"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="padding-bottom">
      <xsl:value-of select="$component.title.font.master * 0.7"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="component.block.properties">
    <xsl:attribute name="padding-bottom">
      <xsl:value-of select="0"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <!-- Sections -->

  <xsl:attribute-set name="section.block.properties">
    <xsl:attribute name="padding">0.2em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="section.title.level1.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 2.0736"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="padding-bottom">
      <xsl:value-of select="$body.font.master"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="section.title.level2.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.728"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="section.title.level3.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.44"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="section.title.level4.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.2"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="section.title.level5.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="section.title.level6.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <!-- Glossary -->

  <xsl:param name="glossary.presentation" select="'lists'"/>
  <xsl:param name="glossary.as.blocks" select="0"/>
  <xsl:param name="glossary.collection" select="''"/>
  <xsl:param name="glossentry.show.acronym" select="'yes'"/>
  <xsl:param name="glosslist.as.blocks" select="0"/>
  <xsl:param name="glossterm.auto.link" select="'0'"/>
  <xsl:param name="glossterm.separation" select="'0.25in'"/>
  <xsl:param name="glossterm.width" select="'2in'"/>


  <!-- Refentry & Synopsis -->

  <xsl:param name="refentry.generate.name" select="1"/>
  <xsl:param name="refentry.generate.title" select="0"/>
  <xsl:attribute-set name="refentry.title.properties">
    <xsl:attribute name="font-family">
      <xsl:value-of select="$title.font.family"/>
    </xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.5"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
    <xsl:attribute name="hyphenate">false</xsl:attribute>
    <xsl:attribute name="keep-with-next.within-column">always</xsl:attribute>
    <xsl:attribute name="padding-bottom">0.5em</xsl:attribute>
  </xsl:attribute-set>
  
  <xsl:param name="funcsynopsis.decoration" select="1"/>
  <xsl:param name="funcsynopsis.style">kr</xsl:param>

  <!-- Blocks -->

  <xsl:attribute-set name="sidebar.properties" use-attribute-sets="formal.object.properties">
    <xsl:attribute name="border-style">solid</xsl:attribute>
    <xsl:attribute name="border-width">1pt</xsl:attribute>
    <xsl:attribute name="border-color">black</xsl:attribute>
    <xsl:attribute name="background-color">#e0e0e0</xsl:attribute>
    <xsl:attribute name="padding-left">12pt</xsl:attribute>
    <xsl:attribute name="padding-right">12pt</xsl:attribute>
    <xsl:attribute name="padding-bottom">6pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="normal.para.properties">
    <xsl:attribute name="padding-bottom">0.5em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="blockquote.properties">
    <xsl:attribute name="start-indent">0.5in</xsl:attribute>
    <xsl:attribute name="end-indent">0.5in</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="note.properties">
    <xsl:attribute name="padding-bottom">1em</xsl:attribute>
    <xsl:attribute name="start-indent">0.5in</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="list.block.properties">
    <xsl:attribute name="padding-bottom">1em</xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="list.item.properties">
    <xsl:attribute name="padding-bottom">1em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="admonition.title.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.2"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="verbatim.properties">
    <xsl:attribute name="border-top-width">1em</xsl:attribute>
    <xsl:attribute name="border-bottom-width">1em</xsl:attribute>
    <xsl:attribute name="font-family">
      <xsl:value-of select="$monospace.font.family"/>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="monospace.verbatim.properties" 
       use-attribute-sets="verbatim.properties monospace.properties">
    <xsl:attribute name="text-align">start</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="shade.verbatim.style">
    <xsl:attribute name="background-color">#E0E0E0</xsl:attribute>
  </xsl:attribute-set>

  <!-- Formals -->

  <xsl:attribute-set name="equation.properties" use-attribute-sets="formal.object.properties"/>
  <xsl:attribute-set name="example.properties" use-attribute-sets="formal.object.properties"/>
  <xsl:attribute-set name="figure.properties" use-attribute-sets="formal.object.properties"/>
  <xsl:attribute-set name="table.properties" use-attribute-sets="formal.object.properties"/>
  <xsl:attribute-set name="procedure.properties" use-attribute-sets="formal.object.properties"/>

  <xsl:attribute-set name="formal.title.properties">
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.2"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="padding-bottom">
      <xsl:value-of select="$body.font.master * 0.5"/><xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="formal.object.properties">
    <xsl:attribute name="padding-bottom">1em</xsl:attribute>
  </xsl:attribute-set>

  <!-- TOC -->
  <xsl:attribute-set name="toc.margin.properties">
    <xsl:attribute name="padding-bottom">1em</xsl:attribute>
  </xsl:attribute-set>

  <!-- Tables -->
  <xsl:param name="table.cell.border.color" select="'#000000'"/>
  <xsl:param name="table.cell.border.style" select="'solid'"/>
  <xsl:param name="table.cell.border.thickness" select="'1px'"/>
  <xsl:attribute-set name="table.cell.padding">
    <xsl:attribute name="padding-left">2pt</xsl:attribute>
    <xsl:attribute name="padding-right">2pt</xsl:attribute>
    <xsl:attribute name="padding-top">2pt</xsl:attribute>
    <xsl:attribute name="padding-bottom">2pt</xsl:attribute>
  </xsl:attribute-set>


  <xsl:param name="default.table.width" select="''"/>
  <xsl:param name="table.footnote.number.format" select="'a'"/>
  <xsl:param name="table.footnote.number.symbols" select="''"/>

  <xsl:param name="table.frame.border.color" select="'#000000'"/>
  <xsl:param name="table.frame.border.style" select="'solid'"/>
  <xsl:param name="table.frame.border.thickness" select="'1px'"/>
  <xsl:attribute-set name="table.properties" use-attribute-sets="formal.object.properties"/>

  <!-- Misc -->
  <xsl:param name="bibliography.collection" select="''"/>


  <xsl:param name="menuchoice.menu.separator" select="'-&gt;'"/>
  <xsl:param name="menuchoice.separator" select="'+'"/>

  <xsl:param name="shade.verbatim" select="1"/>

  <xsl:attribute-set name="shade.verbatim.style">
    <xsl:attribute name="background-color">#E0E0E0</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="monospace.properties">
    <xsl:attribute name="font-family">
      <xsl:value-of select="$monospace.font.family"/>
    </xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 0.9"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:param name="title.end.punct" select="'.!?:'"/>
  <xsl:param name="default.title.end.punct" select="'.'"/>

  <xsl:param name="biblioentry.item.separator">. </xsl:param>
  <xsl:param name="bibliography.numbered" select="0"/>  

  <xsl:attribute-set name="list.block.spacing">
    <xsl:attribute name="padding-bottom">0.5em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="list.item.spacing">
    <xsl:attribute name="padding-top">0.3em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="compact.list.item.spacing">
    <xsl:attribute name="padding-top">0.3em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="normal.para.spacing">
    <xsl:attribute name="padding-bottom">0.5em</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="xref.properties"/>
  <xsl:param name="use.role.as.xrefstyle" select="1"/>
  <xsl:param name="xref.with.number.and.title" select="1"/>   
  <xsl:param name="insert.xref.page.number" select="0"/>
</xsl:stylesheet>
