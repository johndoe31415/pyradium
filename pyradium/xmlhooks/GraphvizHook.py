#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2022 Johannes Bauer
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

@XMLHookRegistry.register_hook
class GraphvizHook(BaseHook):
	_TAG_NAME = "graphviz"

	@classmethod
	def handle(cls, rendered_presentation, node):
		properties = {
			"src":				rendered_presentation.renderer.lookup_include(node.getAttribute("src")),
		}
		graphviz_renderer = rendered_presentation.renderer.get_custom_renderer("graphviz")
		rendered_graph = graphviz_renderer.render(properties)
		local_filename = f"imgs/graphviz/{rendered_graph.keyhash}.{rendered_graph.data['extension']}"
		uri = f"{rendered_presentation.renderer.rendering_params.resource_uri}imgs/graphviz/{rendered_graph.keyhash}.{rendered_graph.data['extension']}"

		replacement_node = node.ownerDocument.createElement("div")
		replacement_node.setAttribute("class", "fillimg")

		img_node = node.ownerDocument.createElement("img")
		img_node.setAttribute("src", uri)
		img_node.setAttribute("class", "fill")
		replacement_node.appendChild(img_node)

		rendered_presentation.add_file(local_filename, rendered_graph.data["img_data"])
		return replacement_node
