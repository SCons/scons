#!/usr/bin/env python
from __future__ import print_function

import sys
import datetime

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
	  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print('<table width="100%">')
def row(*cells, **kw):
	td = kw.get('tr','td')
	print('  <tr>')
	for cell in cells:
		print('    <%s>%s</%s>' % (td,cell,td))
	print('  </tr>')
row('Estimated&nbsp;date', 'Type', 'Comments', tr = 'th')

if len(sys.argv) > 1:
	f = open(sys.argv[1])
else:	f = open('schedule')
now = None
current = 'UNKNOWN'
for line in f:
	if line[0] == '#': continue	# comment
	if line[0] == '=':
		date,current = line[1:].strip().split(None, 1)
		now = datetime.date(*tuple([int(i) for i in date.split('-')]))
		continue
	if line[0] == '+':
		incr,type,desc = line[1:].strip().split(None,2)
		now = now + datetime.timedelta(int(incr))
	else:
		print('dunna understand code', line[0])
		sys.exit(1)
	#name = current + '.d' + str(now).replace('-','')
	date = '%s-%s-%s' % (now.day,months[now.month-1],now.year)
	if type == 'ck':
		category = 'Ckpt'
	elif type == 'rc':
		category = 'RC'
	else:
		category = current = type
	row(date, category, desc)
print('</table>')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
