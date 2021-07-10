#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

from pybeamer.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pybeamer.Tools import XMLTools

@XMLHookRegistry.register_hook
class TexHook(BaseHook):
	_TAG_NAME = "tex"

	@classmethod
	def handle(cls, rendered_presentation, node):
		properties = {
			"formula":	XMLTools.inner_text(node),
			"long":		XMLTools.get_bool_attr(node, "long"),
		}
		tex_renderer = rendered_presentation.renderer.get_custom_renderer("latex")
		rendered_formula = tex_renderer.render(properties)

		scale_factor = 0.5
		width_px = round(rendered_formula.data["info"]["width"] * scale_factor)
		baseline_px = round(rendered_formula.data["info"]["baseline"] * scale_factor)

		replacement_node = node.ownerDocument.createElement("img")
		replacement_node.setAttribute("src", "latex_%s.png" % (rendered_formula.keyhash))
		replacement_node.setAttribute("style", "width: %dpx; margin-bottom: -%dpx; margin-top: 5px" % (width_px, baseline_px))
		replacement_node.setAttribute("alt", properties["formula"])
		return replacement_node
