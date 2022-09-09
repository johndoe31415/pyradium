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

import logging
from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.CircuitJS import CircuitJSCircuit
from pyradium.Exceptions import MalformedXMLInputException, FailedToLookupFileException

_log = logging.getLogger(__spec__.name)

@XMLHookRegistry.register_hook
class CircuitHook(BaseHook):
	_TAG_NAME = "circuit"

	@classmethod
	def handle(cls, rendered_presentation, node):
		circuit = CircuitJSCircuit.from_xml(node, find_file_function = rendered_presentation.renderer.lookup_include)

		replacement_node = node.ownerDocument.createElement("a")
		replacement_node.setAttribute("href", circuit.full_url(include_circuit = True))

		name = circuit.get_presentation_parameter("name")
		content = circuit.get_presentation_parameter("content")
		if content is not None:
			match content:
				case "image":
					if name is None:
						raise MalformedXMLInputException("s:circuit requires an image by 'content' parameter, but does not name the circuit.")

					filename = f"circuit_{name}.svg"
					try:
						lookup = rendered_presentation.renderer.lookup_include(filename)
						img = node.ownerDocument.createElement("s:img")
						img.setAttribute("src", filename)
						replacement_node.appendChild(img)
					except FailedToLookupFileException:
						error_text = f"Missing rendered circuit: {name}"
						replacement_node.appendChild(node.ownerDocument.createTextNode(error_text))
						_log.warning(error_text)
				case _:
					raise MalformedXMLInputException(f"s:circuit has unknown 'content' parameter: {content}")
		else:
			# Verbatim take the content nodes
			for child_node in circuit.display_content:
				replacement_node.appendChild(child_node)

		return replacement_node
