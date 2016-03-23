env = Environment(DOCBOOK_PREFER_XSLTPROC=1, tools=['docbook'])
env.DocbookSlidesHtml('virt', xsl='slides.xsl', base_dir='output/')

