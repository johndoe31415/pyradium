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

import contextlib
import xml.dom.minidom
from pyradium.StyleDict import StyleDict

class Vector2D():
	def __init__(self, x = 0, y = 0):
		self._x = x
		self._y = y

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	def __iadd__(self, vector):
		return Vector2D(self.x + vector.x, self.y + vector.y)

class SVGStyle():
	def __init__(self, node):
		self._node = node
		if node.hasAttribute("style"):
			self._style_dict = StyleDict.from_style_str(node.getAttribute("style"))
		else:
			self._style_dict = StyleDict()

	def __getitem__(self, key):
		return self._style_dict[key]

	def __setitem__(self, key, value):
		self._style_dict[key] = value
		self._style_dict.to_node(self._node)

	def update(self, style_dict: dict):
		for (key, value) in style_dict.items():
			self._style_dict[key] = value
		self._style_dict.to_node(self._node)

	@classmethod
	def default_path(cls, node):
		style = cls(node)
		style.update({
			"fill":				"none",
			"stroke":			"#000000",
			"stroke-width":		"1px",
			"stroke-linecap":	"butt",
			"stroke-linejoin":	"miter",
			"stroke-opacity":	"1",
		})
		return style

	@classmethod
	def default_text(cls, node):
		style = cls(node)
		style.update({
			"font-style":		"normal",
			"font-weight":		"normal",
			"font-size":		"12px",
			"line-height":		"1.25",
			"font-family":		"sans-serif",
			"white-space":		"pre",
			"fill":				"#000000",
			"fill-opacity":		"1",
			"stroke":			"none",
		})
		return style

class SVGPath():
	def __init__(self, path_node):
		self._node = path_node
		self._style = SVGStyle.default_path(self._node)
		self._cmds = [ ]
		self._pos = Vector2D()

	@property
	def pos(self):
		return self._pos

	@property
	def style(self):
		return self._style

	@contextlib.contextmanager
	def returnto(self):
		prev = self._pos
		yield
		self.move_to(prev.x, prev.y)

	def _append(self, *cmds):
		self._cmds += cmds
		self._node.setAttribute("d", " ".join(self._cmds))

	def move_to(self, x, y):
		self._append("M", f"{x},{y}")
		self._pos = Vector2D(x, y)
		return self

	def move_rel(self, x, y):
		self._append("m", f"{x},{y}")
		self._pos += Vector2D(x, y)
		return self

	def line_to(self, x, y):
		self._append("L", f"{x},{y}")
		self._pos += Vector2D(x, y)
		return self

	def line_rel(self, x, y):
		self._append("l", f"{x},{y}")
		self._pos += Vector2D(x, y)
		return self

	def horiz_rel(self, x):
		self._append("h", f"{x}")
		self._pos += Vector2D(x, 0)
		return self

class SVGText():
	def __init__(self, text_node, textdata_node):
		self._node = text_node
		self._textdata_node = textdata_node
		self._style = SVGStyle.default_text(self._node)

	@property
	def text(self):
		return self._textdata_node.wholeText

	@text.setter
	def text(self, value):
		self._textdata_node.replaceWholeText(value)

	@property
	def style(self):
		return self._style

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

	def new_path(self, x, y):
		path_node = self._doc.createElement("path")
		self._root.appendChild(path_node)
		svg_path = SVGPath(path_node)
		svg_path.move_to(x, y)
		return svg_path

	def new_text_span(self, x, y, width, height, text):
		rect_node = self._doc.createElement("rect")
		rect_node.setAttribute("x", str(x))
		rect_node.setAttribute("y", str(y))
		rect_node.setAttribute("width", str(width))
		rect_node.setAttribute("height", str(height))
		def_id = self._add_definition(rect_node)

		text_node = self._root.appendChild(self._doc.createElement("text"))
		text_node.setAttribute("xml:space", "preserve")
		tspan_node = text_node.appendChild(self._doc.createElement("tspan"))
		textdata_node = tspan_node.appendChild(self._doc.createTextNode(""))

		svg_text = SVGText(text_node, textdata_node)
		svg_text.text = text
		svg_text.style["shape-inside"] = f"url(#{def_id})"
		return svg_text

	def write(self, filename):
		with open(filename, "w") as f:
			self._doc.writexml(f)
