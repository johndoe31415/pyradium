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

import xml.dom.minidom
from .Tools import XMLTools

class SVGStyle():
	def __init__(self, style_dict = None):
		assert((style_dict is None) or isinstance(style_dict, dict))
		self._style = style_dict

	@classmethod
	def from_style_str(cls, style_str):
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

	@property
	def is_visible(self):
		if "display" in self._style:
			hidden = (self["display"] == "none")
			return not hidden
		return True

	def serialize(self):
		return ";".join("%s:%s" % (key, value) for (key, value) in self._style.items())

	def __setitem__(self, key, value):
		self._style[key] = value

	def __getitem__(self, key):
		return self._style.get(key)

	def __str__(self):
		return "SVGStyle<%s>" % (str(self._style))

class SVGLayer():
	def __init__(self, group_node):
		self._node = group_node

	@property
	def layer_id(self):
		return self._node.getAttribute("id")

	@property
	def is_visible(self):
		return SVGStyle.from_node(self._node).is_visible

	def modify_style(self, callback):
		style = SVGStyle.from_node(self._node)
		callback(style)
		self._node.setAttribute("style", style.serialize())

	def hide(self):
		def _callback(style):
			style["display"] = "none"
		self.modify_style(_callback)

	def show(self):
		def _callback(style):
			style["display"] = "inline"
		self.modify_style(_callback)

class SVGTransformation():
	def __init__(self, svg_filename):
		self._xml = xml.dom.minidom.parse(svg_filename)
		self._svg = self._xml.childNodes[0]
		self._layers = [ ]
		self._layers_by_id = { }
		for group_node in XMLTools.findall(self._svg, "g", namespace_uri = "http://www.w3.org/2000/svg"):
			groupmode = group_node.getAttributeNS("http://www.inkscape.org/namespaces/inkscape", "groupmode")
			if groupmode == "layer":
				# Inkscape layer node
				layer = SVGLayer(group_node)
				self._layers.append(layer)
				self._layers_by_id[layer.layer_id] = layer

	@property
	def visible_layer_ids(self):
		for layer in self._layers:
			if layer.is_visible:
				yield layer.layer_id

	@property
	def layer_ids(self):
		for layer in self._layers:
			yield layer.layer_id

	@property
	def layers(self):
		return iter(self._layers)

	def get_layer(self, layer_id):
		return self._layers_by_id[layer_id]

	def _search_replace_text(self, search, replace):
		for text_node in XMLTools.findall_recurse(self._xml, "text"):
			for tspan_node in XMLTools.findall(text_node, "tspan"):
				for cdata_node in XMLTools.findall_text(tspan_node, recursive = True):
					cdata_node.replaceWholeText(cdata_node.wholeText.replace(search, replace))

	def apply(self, transformation_dict):
		if transformation_dict["cmd"] == "show_layer":
			self.get_layer(transformation_dict["layer_id"]).show()
		elif transformation_dict["cmd"] == "hide_layer":
			self.get_layer(transformation_dict["layer_id"]).hide()
		elif transformation_dict["cmd"] == "replace_text":
			self._search_replace_text(transformation_dict["search"], transformation_dict["replace"])
		else:
			raise NotImplementedError(transformation_dict["cmd"])

	def apply_all(self, transformation_dicts):
		for transformation_dict in transformation_dicts:
			self.apply(transformation_dict)

	def write(self, f):
		self._xml.writexml(f)

	def write_file(self, filename):
		with open(filename, "w") as f:
			self.write(f)

if __name__ == "__main__":
	svg = SVGTransformation("animation_l2hid.svg")
	print(list(svg.layer_ids))
	layer_ids = list(svg.visible_layer_ids)
	print(layer_ids)
	for layer_id in layer_ids:
		svg.get_layer(layer_id).hide()
	svg.get_layer(layer_ids[0]).show()
	svg.apply({
		"cmd": "replace_text",
		"search": "MUH TEXT",
		"replace": "This was Muh.",
	})
	svg.apply({
		"cmd": "replace_text",
		"search": "FOO TEXT",
		"replace": "This was Foo.",
	})
	svg.write_file("/tmp/x.svg")
