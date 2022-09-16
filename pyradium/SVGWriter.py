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
		return self._style_dict.get(key)

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

	def new_path(self, x, y):
		path_node = self._doc.createElement("path")
		self._root.appendChild(path_node)
		path = SVGPath(path_node)
		path.move_to(x, y)
		return path

	def write(self, filename):
		with open(filename, "w") as f:
			self._doc.writexml(f)

