#!/usr/bin/env python

# Download the issues from Issuzilla as XML; this creates a file named
# 'issues.xml'.  Run this script to translate 'issues.xml' into a CSV
# file named 'editlist.csv'.  Upload the CSV into a Google spreadsheet.

# In the spreadsheet, select the last column and delete it (added by the
# upload to allow for expansion; we don't need it).
# Select all the columns and pick "align-->top"
# Select the ID and votes columns and pick "align-->right"
# Select the priority column and pick "align-->center"
# Select the first row and click on the "bold" button
# Grab the lines between the column headers to adjust the column widths
# Grab the sort bar on the far left (just above the "1" for row one)
# and move it down one row.  (Row one becomes a floating header)
# Voila!

# The team members
# FIXME: These names really should be external to this script
team = 'Bill Greg Steven Gary Ken Brandon Sohail Jim'.split()
team.sort()

# The elements to be picked out of the issue
PickList = [
	# sort key -- these are used to sort the entry
	'target_milestone', 'priority', 'votes_desc', 'creation_ts',
	# payload -- these are displayed
	'issue_id', 'votes', 'issue_type', 'target_milestone',
	'priority', 'assigned_to', 'short_desc',
	]

# Conbert a leaf element into its value as a text string
# We assume it's "short enough" that there's only one substring
def Value(element):
	v = element.firstChild
	if v is None: return ''
	return v.nodeValue

# Parse the XML issues file and produce a DOM for it
# FIXME: parameterize the input file name
from xml.dom.minidom import parse
xml = parse('issues.xml')

# Go through the issues in the DOM, pick out the elements we want,
# and put them in our list of issues.
issues = []
for issuezilla in xml.childNodes:
	# The Issuezilla element contains the issues
	if issuezilla.nodeType != issuezilla.ELEMENT_NODE: continue
	for issue in issuezilla.childNodes:
		# The issue elements contain the info for an issue
		if issue.nodeType != issue.ELEMENT_NODE: continue
		# Accumulate the pieces we want to include
		d = {}
		for element in issue.childNodes:
			if element.nodeName in PickList:
				d[element.nodeName] = Value(element)
		# convert 'votes' to numeric, ascending and descending
		try:
			v = int('0' + d['votes'])
		except KeyError:
			pass
		else:
			d['votes_desc'] = -v
			d['votes'] = v
		# Marshal the elements and add them to the list
		issues.append([ d[ix] for ix in PickList ])
issues.sort()

# Transcribe the issues into comma-separated values.
# FIXME: parameterize the output file name
import csv
writer = csv.writer(open('editlist.csv', 'w'))
# header
writer.writerow(['ID', 'Votes', 'Type/Member', 'Milestone',
		'Pri', 'Owner', 'Summary/Comments'])
for issue in issues:
	row = issue[4:]		# strip off sort key
	#row[0] = """=hyperlink("http://scons.tigris.org/issues/show_bug.cgi?id=%s","%s")""" % (row[0],row[0])
	if row[3] == '-unspecified-': row[3] = 'triage'
	writer.writerow(['','','','','','',''])
	writer.writerow(row)
	writer.writerow(['','','consensus','','','',''])
	writer.writerow(['','','','','','',''])
	for member in team: writer.writerow(['','',member,'','','',''])
