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

from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.Tools import XMLTools
from pyradium.StyleDict import StyleDict

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

		# For now, always wrap in div for long formulae. Could easily add an
		# option to override this if it's useful.
		wrap_in_div = properties["long"]

		img_node = node.ownerDocument.createElement("img")
		img_node.setAttribute("src", uri)
		img_node.setAttribute("alt", properties["formula"])

		img_style = StyleDict()
		img_style["width"] = f"{width_px}px"
		img_style["margin-top"] = "5px"
		if not properties["long"]:
			img_style["margin-bottom"] = f"{-baseline_px + 1}px"
		if node.hasAttribute("indent"):
			indent = float(node.getAttribute("indent"))
			indent_px = round(indent * 50)
			img_style["margin-left"] = f"{indent_px}px"
		img_style.to_node(img_node)

		if not wrap_in_div:
			replacement_node = img_node
		else:
			replacement_node = node.ownerDocument.createElement("div")
			replacement_node.setAttribute("class", "texformula")
			replacement_node.appendChild(img_node)

		rendered_presentation.add_file(local_filename, rendered_formula.data["png_data"])
		return replacement_node
