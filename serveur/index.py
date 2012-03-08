#!/usr/bin/python
# encoding: utf-8

import os.path as op
import os

import cgitb
cgitb.enable()


print "Content-type: text/html; charset=utf-8\n\n"
print """<html>
	<head>
		<title>Liste des galeries</title>
	</head>
	<body>
		<h2>Liste des galeries</h2>
"""

print "<ul>"
for d in os.listdir("."):
	if op.isdir(d):
		print "<li><a href='%s'>%s</a></li>\n"%(d,d)

print "</ul></body></html>" 
	
	
