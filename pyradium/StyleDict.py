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

class StyleDict():
	def __init__(self, style_dict: dict | None = None):
		assert((style_dict is None) or isinstance(style_dict, dict))
		self._style = style_dict if (style_dict is not None) else { }

	@classmethod
	def from_style_str(cls, style_str: str):
		style_dict = { }
		for style_item in style_str.split(";"):
			style_item = style_item.strip()
			if style_item == "":
				continue
			style_item = style_item.split(":", maxsplit = 1)
			if len(style_item) == 2:
				(key, value) = style_item
				key = key.strip()
				value = value.strip()
				style_dict[key] = value
		return cls(style_dict)

	@classmethod
	def from_node(cls, node):
		return cls.from_style_str(node.getAttribute("style"))

	def to_node(self, node):
		if (len(self._style) == 0) and node.hasAttribute("style"):
			node.removeAttribute("style")
		else:
			node.setAttribute("style", self.serialize())

	@property
	def is_visible(self):
		if "display" in self._style:
			hidden = (self["display"] == "none")
			return not hidden
		return True

	def serialize(self):
		return ";".join("%s:%s" % (key, value) for (key, value) in self._style.items())

	def __setitem__(self, key: str, value: str):
		self._style[key] = value

	def __getitem__(self, key: str):
		return self._style.get(key)

	def __str__(self):
		return f"StyleDict<{self._style}>"
