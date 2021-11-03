#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.Tools import XMLTools

@XMLHookRegistry.register_hook
class TexHook(BaseHook):
	_TAG_NAME = "tex"

	@classmethod
	def handle(cls, rendered_presentation, node):
		properties = {
			"formula":	XMLTools.inner_text(node),
			"long":		XMLTools.get_bool_attr(node, "long"),
		}
		if node.hasAttribute("scale"):
			user_scale = float(node.getAttribute("scale"))
		else:
			user_scale = 1
		tex_renderer = rendered_presentation.renderer.get_custom_renderer("latex")
		rendered_formula = tex_renderer.render(properties)
		local_filename = "imgs/latex/%s.png" % (rendered_formula.keyhash)
		uri = "%simgs/latex/%s.png" % (rendered_presentation.renderer.rendering_params.resource_uri, rendered_formula.keyhash)

		scale_factor = 0.625 * user_scale
		width_px = round(rendered_formula.data["info"]["width"] * scale_factor)
		baseline_px = round(rendered_formula.data["info"]["baseline"] * scale_factor)
		#print(properties["formula"], rendered_formula.data["info"], width_px)

		replacement_node = node.ownerDocument.createElement("img")
		replacement_node.setAttribute("src", uri)
		if properties["long"]:
			replacement_node.setAttribute("style", "width: %dpx; margin-top: 5px" % (width_px))
		else:
			replacement_node.setAttribute("style", "width: %dpx; margin-bottom: %dpx; margin-top: 5px" % (width_px, -baseline_px + 1))
		replacement_node.setAttribute("alt", properties["formula"])

		rendered_presentation.add_file(local_filename, rendered_formula.data["png_data"])
		return replacement_node
