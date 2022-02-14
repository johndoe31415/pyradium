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

import sys
import xml.dom.minidom

class Helper():
	def __init__(self):
		pass

	@classmethod
	def print_tag(cls, tagname, text):
		doc = xml.dom.minidom.Document()
		node = doc.createElement("raw")
		node.setAttributeNS("xmls", "xmlns:s", "https://github.com/johndoe31415/pyradium")
		child = doc.createElement(tagname)
		child.appendChild(doc.createTextNode(text))
		node.appendChild(child)
		doc.appendChild(node)
		doc.writexml(sys.stdout)

	@classmethod
	def print_tt(cls, text):
		return cls.print_tag("s:tt", text)

	@classmethod
	def print_tex(cls, text):
		return cls.print_tag("s:tex", text)
