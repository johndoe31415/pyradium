#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2020 Johannes Bauer
#
#	This file is part of pybeamer.
#
#	pybeamer is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pybeamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pybeamer; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import io
import xml.etree.ElementTree

class XMLTools():
	@classmethod
	def dump(cls, node, indent = 0):
		if isinstance(node, xml.etree.ElementTree.ElementTree):
			node = node.getroot()
		spc = ("  " * indent)
		attr_str = "" if (len(node.attrib) == 0) else str(node.attrib)
		print("%s%s %s" %  (spc, node.tag, attr_str))
		for child in node:
			cls.dump(child, indent + 1)

	@classmethod
	def dumpxml(cls, node):
		if isinstance(node, xml.etree.ElementTree.ElementTree):
			node = node.getroot()
		tree = xml.etree.ElementTree.ElementTree(node)
		f = io.BytesIO()
		tree.write(f)
		return f.getvalue().decode()

	@classmethod
	def dump_innerxml(cls, node):
		doc = [ ]
		if node.text is not None:
			doc.append(node.text)
		for child in node:
			doc.append(cls.dumpxml(child))
			if child.tail is not None:
				doc.append(child.tail)
		return "".join(doc)

	@classmethod
	def remove_namespace(cls, node, ns):
		return node
