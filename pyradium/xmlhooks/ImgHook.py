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
from pyradium.Exceptions import InvalidTransformationException, MalformedXMLInputException

@XMLHookRegistry.register_hook
class ImgHook(BaseHook):
	_TAG_NAME = "img"

	@classmethod
	def _parse_transformations(cls, node):
		transformations = [ ]

		variables = { }
		for child_node in node.childNodes:
			if (child_node.nodeType == child_node.ELEMENT_NODE) and (child_node.tagName == "s:format"):
				if not (child_node.hasAttribute("name") and child_node.hasAttribute("value")):
					raise InvalidTransformationException("s:format element needs a 'name' and 'value' attribute.")
				name = child_node.getAttribute("name")
				value = child_node.getAttribute("value")

				if child_node.hasAttribute("type"):
					vtype = child_node.getAttribute("type")
					match vtype:
						case "int":
							value = int(value)
						case _:
							raise InvalidTransformationException(f"s:format element recevied unsupported type '{vtype}'.")
				variables[name] = value

		if len(variables) > 0:
			transformations.append({
				"cmd":			"format_text",
				"variables":	variables,
			})
		return transformations

	@classmethod
	def handle(cls, rendered_presentation, node):
		transformations = cls._parse_transformations(node)

		if node.hasAttribute("src") and node.hasAttribute("value"):
			raise MalformedXMLInputException("Image node may not have both 'src' and 'value' attribute.")
		elif not node.hasAttribute("src") and not node.hasAttribute("value"):
			raise MalformedXMLInputException("Image node needs at least a 'src' or 'value' node.")
		elif node.hasAttribute("value") and not node.hasAttribute("filetype"):
			raise MalformedXMLInputException("Image node with a 'value' literal specification also needs a 'filetype' attribute to specify how to interpret the data.")

		properties = {
			"max_dimension":	rendered_presentation.renderer.rendering_params.image_max_dimension,
		}
		if node.hasAttribute("src"):
			properties["src"] = rendered_presentation.renderer.lookup_include(node.getAttribute("src"))
		else:
			# Literal specification as value
			properties["value"] = node.getAttribute("value").encode("utf-8")

		if node.hasAttribute("filetype"):
			properties["filetype"] = node.getAttribute("filetype")

		if len(transformations) > 0:
			properties["svg_transform"] = transformations
		img_renderer = rendered_presentation.renderer.get_custom_renderer("img")
		rendered_image = img_renderer.render(properties)
		local_filename = "imgs/img/%s.%s" % (rendered_image.keyhash, rendered_image.data["extension"])
		uri = "%simgs/img/%s.%s" % (rendered_presentation.renderer.rendering_params.resource_uri, rendered_image.keyhash, rendered_image.data["extension"])

		img_style = [ ]
		if node.hasAttribute("width"):
			img_style.append(("width", node.getAttribute("width")))
		if node.hasAttribute("height"):
			img_style.append(("height", node.getAttribute("height")))
		if node.hasAttribute("render"):
			img_style.append(("image-rendering", node.getAttribute("render")))

		create_filldiv = XMLTools.get_bool_attr(node, "fill", default_value = True)

		img_node = node.ownerDocument.createElement("img")
		img_node.setAttribute("src", uri)
		img_node.setAttribute("class", "fill")
		if len(img_style) > 0:
			img_node.setAttribute("style", ";".join("%s:%s" %  (key, value) for (key, value) in img_style))

		if create_filldiv:
			replacement_node = node.ownerDocument.createElement("div")
			replacement_node.setAttribute("class", "fillimg")
			replacement_node.appendChild(img_node)
		else:
			replacement_node = img_node

		rendered_presentation.add_file(local_filename, rendered_image.data["img_data"])
		return replacement_node
