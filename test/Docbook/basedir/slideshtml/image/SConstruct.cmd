import xsltver

v = xsltver.detectXsltVersion('/usr/share/xml/docbook/stylesheet/docbook-xsl')

ns_ext = ''
if v >= (1, 78, 0):
    # Use namespace-aware input file
    ns_ext = 'ns'

env = Environment(DOCBOOK_PREFER_XSLTPROC=1, tools=['docbook'])
env.Append(DOCBOOK_XSLTPROCFLAGS=['--novalid', '--nonet'])
env.DocbookSlidesHtml('virt'+ns_ext, xsl='slides.xsl', base_dir='output/')

