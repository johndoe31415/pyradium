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
from .Exceptions import InvalidTransformationException
from .StyleDict import StyleDict

class SVGLayer():
	def __init__(self, group_node):
		self._node = group_node

	@property
	def label(self):
		return self._node.getAttribute("inkscape:label")

	@property
	def layer_id(self):
		return self._node.getAttribute("id")

	@property
	def is_visible(self):
		return StyleDict.from_node(self._node).is_visible

	def modify_style(self, callback):
		style = StyleDict.from_node(self._node)
		callback(style)
		style.to_node(self._node)

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
		self._svg = XMLTools.findfirst(self._xml, "svg")
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

	def _format_text(self, variables):
		for text_node in XMLTools.findall_recurse(self._xml, "text"):
			for tspan_node in XMLTools.findall(text_node, "tspan"):
				for cdata_node in XMLTools.findall_text(tspan_node, recursive = True):
					try:
						replacement_text = cdata_node.wholeText.format(**variables)
					except KeyError as e:
						raise InvalidTransformationException(f"Requested variable substitution is missing variable name: {e}") from e
					cdata_node.replaceWholeText(replacement_text)

	def apply(self, transformation_dict):
		if transformation_dict["cmd"] == "show_layer":
			self.get_layer(transformation_dict["layer_id"]).show()
		elif transformation_dict["cmd"] == "hide_layer":
			self.get_layer(transformation_dict["layer_id"]).hide()
		elif transformation_dict["cmd"] == "format_text":
			self._format_text(transformation_dict["variables"])
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
