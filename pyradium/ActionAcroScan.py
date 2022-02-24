#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2022 Johannes Bauer
#
#	This file is part of pyradium.
#
#	pyradium is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pyradium is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pyradium; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import re
import xml.dom.minidom
from .Tools import XMLTools
from .Acrofile import Acrofile
from .BaseAction import BaseAction

class ActionAcroScan(BaseAction):
	_WHITESPACE_RE = re.compile(r"(\s+)")

	def _slide_callback(self, node):
		if node.nodeType == node.TEXT_NODE:
			split_text = self._WHITESPACE_RE.split(node.wholeText)
			display_text = node.wholeText.replace("\t", "  ").replace("\n", " ")
			performed_replacement = False

			processed_split_text = [ ]
			for word in split_text:
				if self._acrofile.has(word):
					acro = self._acrofile.get(word)
					print("Found possible acronym on slide %d:" % (self._slideno))
					print("%s = %s" % (word, acro["text"]))
					print("Context: %s" % (display_text))
					yn = input("Replace (y/n)? ")
					print()
					if yn.lower() == "y":
						self._performed_change = True
						performed_replacement = True
						processed_split_text.append([ word ])
					else:
						processed_split_text.append(word)
				else:
					processed_split_text.append(word)

			if performed_replacement:
				replacement_nodes = [ ]
				for element in processed_split_text:
					if isinstance(element, str):
						replacement_nodes.append(node.ownerDocument.createTextNode(element))
					else:
						ac_node = node.ownerDocument.createElement("s:ac")
						ac_node.appendChild(node.ownerDocument.createTextNode(element[0]))
						replacement_nodes.append(ac_node)
				XMLTools.replace_node(node, replacement_nodes)

	def _process_slide(self, slide):
		XMLTools.walk(slide, self._slide_callback, cancel_descent_predicate = lambda node: (node.nodeType == node.ELEMENT_NODE) and (node.tagName in [ "s:ac", "s:tex", "s:code", "s:term", "s:var" ]))

	def run(self):
		self._acrofile = Acrofile.load_from_file(self._args.acrofile)
		dom = xml.dom.minidom.parse(self._args.infile)
		pres = XMLTools.findall(dom, "presentation")[0]
		slides = XMLTools.findall(pres, "slide")
		self._performed_change = False
		for (slideno, slide) in enumerate(slides, 1):
			self._slideno = slideno
			self._process_slide(slide)

		if self._performed_change:
			while True:
				tempfile_name = self._args.infile + "_" + os.urandom(8).hex()
				if not os.path.exists(tempfile_name):
					break
			with open(tempfile_name, "w") as f:
				dom.writexml(f)
			os.rename(tempfile_name, self._args.infile)
