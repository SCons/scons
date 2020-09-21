env = Environment(DOCBOOK_PREFER_XSLTPROC=1, tools=['docbook'])
env.Append(DOCBOOK_XSLTPROCFLAGS=['--novalid', '--nonet'])
env.DocbookSlidesPdf('virt')

