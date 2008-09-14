#!/usr/bin/env python

import sys
import datetime

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
	  'August', 'September', 'October', 'November', 'December']

print '<table>'
def row(*cells, **kw):
	td = kw.get('tr','td')
	print '  <tr>'
	for cell in cells:
		print '    <%s>%s</%s>' % (td,cell,td)
	print '  </tr>'
row('Estimated date', 'Type', 'Name', 'Comments', tr = 'th')

if len(sys.argv) > 1:
	f = open(sys.argv[1])
else:	f = open('schedule')
now = None
current = 'UNKNOWN'
for line in f:
	if line[0] == '#': continue	# comment
	if line[0] == '=':
		date,current = line[1:].strip().split()
		now = datetime.date(*tuple([int(i) for i in date.split('-')]))
		continue
	if line[0] == '+':
		incr,type,desc = line[1:].strip().split(None,2)
		now = now + datetime.timedelta(int(incr))
	else:
		print 'dunna understand code', line[0]
		sys.exit(1)
	name = current + '.d' + str(now).replace('-','')
	date = '%s %s %s' % (now.day,months[now.month-1],now.year)
	if type == 'ck':
		category = 'checkpoint'
	elif type == 'rc':
		category = 'candidate'
	else:
		current = name = type
		category = 'release'
	row(date, category, name, desc)
print '</table>'
