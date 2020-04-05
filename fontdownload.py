#!/usr/bin/python3
import sys
import re
import os
import requests

class FontDownloader():
	_REGEX = re.compile(r"(?P<prefix>/\* (?P<comment>[-a-zA-Z]+) \*/.*?local\('(?P<name>[-A-Za-z_]+)'\)), url\((?P<uri>[^)]+)\)", flags = re.MULTILINE | re.DOTALL)

	def __init__(self, cssfile):
		self._cssfile = cssfile
		self._sess = requests.Session()

	def _replace(self, match):
		#local_filename = os.path.basename(match["uri"])
		local_filename = "%s-%s.woff2" % (match["name"], match["comment"])
		replacement = "%s, url(%s)" % (match["prefix"], local_filename)
		print(local_filename, file = sys.stderr)
		if not os.path.exists(local_filename):
			response = self._sess.get(match["uri"])
			with open(local_filename, "wb") as f:
				f.write(response.content)
		return replacement

	def run(self):
		with open(self._cssfile) as f:
			content = f.read()

		content = self._REGEX.sub(self._replace, content)
		print(content)

fdl = FontDownloader(sys.argv[1])
fdl.run()
