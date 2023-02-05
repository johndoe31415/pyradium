#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2023 Johannes Bauer
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

import xml.dom.minidom
from .SVGPath import SVGPath
from .SVGText import SVGText

class SVGWriter():
	_NAMESPACES = {
		"inkscape": "http://www.inkscape.org/namespaces/inkscape",
		"sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
		"svg": "http://www.w3.org/2000/svg",
		"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
		"cc": "http://creativecommons.org/ns#",
		"dc": "http://purl.org/dc/elements/1.1/",
	}

	def __init__(self):
		self._doc = xml.dom.minidom.Document()
		self._root = self._doc.createElement("svg")
		self._root.setAttribute("xmlns", self._NAMESPACES["svg"])
		for (nsname, nsvalue) in self._NAMESPACES.items():
			self._root.setAttribute(f"xmlns:{nsname}", nsvalue)
		self._doc.appendChild(self._root)
		self._defs = None
		self._groups = { }
		self._uid = 0

	def _genid(self):
		self._uid += 1
		return f"id{self._uid}"

	def _add_definition(self, def_node):
		if self._defs is None:
			self._defs = self._doc.createElement("defs")
			self._root.appendChild(self._defs)
		def_id = self._genid()
		def_node.setAttribute("id", def_id)
		self._defs.appendChild(def_node)
		return def_id

	def group(self, group_name):
		if group_name not in self._groups:
			group = self._root.appendChild(self._doc.createElement("g"))
			group.setAttribute("inkscape:groupmode", "layer")
			group.setAttribute("inkscape:label", group_name)
			self._groups[group_name] = group
		return self._groups[group_name]

	def new_path(self, x, y, group_name = "default"):
		path_node = self._doc.createElement("path")
		self.group(group_name).appendChild(path_node)
		svg_path = SVGPath(path_node)
		svg_path.move_to(x, y)
		return svg_path

	def new_text_span(self, x, y, width, height, text, group_name = "default"):
		rect_node = self._doc.createElement("rect")
		rect_node.setAttribute("x", str(x))
		rect_node.setAttribute("y", str(y))
		rect_node.setAttribute("width", str(width))
		rect_node.setAttribute("height", str(height))
		def_id = self._add_definition(rect_node)
		text_node = self.group(group_name).appendChild(self._doc.createElement("text"))
		svg_text = SVGText(text_node)
		svg_text.text = text
		svg_text.style["shape-inside"] = f"url(#{def_id})"
		return svg_text

	def write(self, f):
		self._doc.writexml(f)

	def writefile(self, filename):
		with open(filename, "w") as f:
			self.write(f)
