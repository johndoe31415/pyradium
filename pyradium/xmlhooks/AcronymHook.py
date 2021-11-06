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
from pyradium.Enums import PresentationFeature

@XMLHookRegistry.register_hook
class AcronymHook(BaseHook):
	_TAG_NAME = "ac"

	@classmethod
	def handle(cls, rendered_presentation, node):
		acronym_id = XMLTools.inner_text(node)

		acronym = rendered_presentation.renderer.get_custom_renderer("acronym")
		resolved = acronym.resolve(acronym_id)
		if resolved is None:
			replacement_node = node.ownerDocument.createTextNode(acronym_id)
		else:
			rendered_presentation.add_feature(PresentationFeature.Acronyms)

			outer_span_node = node.ownerDocument.createElement("span")
			replacement_node = outer_span_node

			if resolved.uri is not None:
				link_node = outer_span_node.appendChild(node.ownerDocument.createElement("a"))
				link_node.setAttribute("href", resolved.uri)
				link_node.setAttribute("class", "tooltip-link")
				chain_node = link_node
			else:
				chain_node = outer_span_node

			chain_node.setAttribute("class", "tooltip")
			chain_node.appendChild(node.ownerDocument.createTextNode(resolved.acronym))

			inner_span = chain_node.appendChild(node.ownerDocument.createElement("span"))
			inner_span.setAttribute("class", "text")
			inner_span.appendChild(node.ownerDocument.createTextNode(resolved.text))

		return replacement_node
