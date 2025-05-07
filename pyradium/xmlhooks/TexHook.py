#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2025 Johannes Bauer
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

import dataclasses
from pysvgedit import SVGStyle
from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry, ReplacementFragment
from pyradium.Tools import XMLTools
from pyradium.Enums import PresentationFeature

@dataclasses.dataclass
class TexFormula():
	formula: str
	long: bool
	scale: float | None = None
	indent: float | None = None

	@property
	def to_dict(self):
		return {
			"formula": self.formula,
			"long": self.long,
		}

@XMLHookRegistry.register_hook
class TexHook(BaseHook):
	_TAG_NAME = "tex"

	@classmethod
	def handle(cls, rendered_presentation, node):
		formula = {
			"formula":	XMLTools.inner_text(node),
			"long":		XMLTools.get_bool_attr(node, "long"),
		}
		if node.hasAttribute("scale"):
			formula["scale"] = float(node.getAttribute("scale"))
		if node.hasAttribute("indent"):
			formula["indent"] = float(node.getAttribute("indent"))
		formula = TexFormula(**formula)

		render_as_vector = PresentationFeature.MathJax in rendered_presentation.renderer.rendering_params.presentation_features
		if render_as_vector:
			inner_node = cls._handle_vector_formula(formula, node)
		else:
			inner_node = cls._handle_rasterized_formula(formula, node, rendered_presentation)

		# If we need indentation or are a long formula, wrap in a div
		if formula.long or (formula.indent is not None):
			replacement_node = node.ownerDocument.createElement("div")
			if formula.long:
				replacement_node.setAttribute("class", "texformula")
			if formula.indent is not None:
				indent_px = round(formula.indent * 50)
				replacement_node.setAttribute("style", f"margin-left: {indent_px}px")
			replacement_node.appendChild(inner_node)
		else:
			replacement_node = inner_node
		return ReplacementFragment(replacement = replacement_node)

	@classmethod
	def _handle_vector_formula(cls, formula, node):
		(begin, end) = {
			True:		("QBEntEozXWio", "kIt7msRdzcHK"),
			False:		("Q4mta4Ck5NLH", "Zf1qH71g5gJY"),
		}[formula.long]
		text_node = node.ownerDocument.createTextNode(begin + formula.formula + end)

		span = node.ownerDocument.createElement("span")
		span.appendChild(text_node)
		span.setAttribute("class", "mathjax-enable")

		scale = 1 if formula.scale is None else formula.scale
		if formula.long:
			scale *= 0.85
		if scale != 1:
			span.setAttribute("style", f"font-size: {scale * 100:.1f}%")

		return span

	@classmethod
	def _handle_rasterized_formula(cls, formula, node, rendered_presentation):
		tex_renderer = rendered_presentation.renderer.get_custom_renderer("latex")
		rendered_formula = tex_renderer.render(formula.to_dict)
		local_filename = "imgs/latex/%s.png" % (rendered_formula.keyhash)
		uri = "%simgs/latex/%s.png" % (rendered_presentation.renderer.rendering_params.resource_uri, rendered_formula.keyhash)

		scale_factor = 0.625 * (formula.scale or 1)
		width_px = round(rendered_formula.data["info"]["width"] * scale_factor)
		baseline_px = round(rendered_formula.data["info"]["baseline"] * scale_factor)

		img_node = node.ownerDocument.createElement("img")
		img_node.setAttribute("src", uri)
		img_node.setAttribute("alt", formula.formula)

		img_style = SVGStyle.from_node(img_node)
		img_style["width"] = f"{width_px}px"
		img_style["margin-top"] = "5px"
		if not formula.long:
			img_style["margin-bottom"] = f"{-baseline_px + 1}px"
		img_style.sync_node_style()
		rendered_presentation.add_file(local_filename, rendered_formula.data["png_data"])
		return img_node
