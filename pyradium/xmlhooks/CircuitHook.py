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

import urllib.parse
from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.Tools import XMLTools
from pyradium.Exceptions import UnknownParameterException

@XMLHookRegistry.register_hook
class CircuitHook(BaseHook):
	_TAG_NAME = "circuit"

	@classmethod
	def handle(cls, rendered_presentation, node):
		replacement_node = node.ownerDocument.createElement("a")
		params = {
			"euroResistors":	"true",
			"IECGates":			"false",
			"whiteBackground":	"true",
			"positiveColor":	"#27ae60",
			"negativeColor":	"#ff0000",
		}
		uri = "https://www.falstad.com/circuit/circuitjs.html"
		srclink = None

		inner = [ ]
		for child_node in node.childNodes:
			if (child_node.nodeType == child_node.ELEMENT_NODE) and (child_node.nodeName == "s:param"):
				# Parse parameter
				name = child_node.getAttribute("name")
				value = XMLTools.get_node_value(child_node, find_file_function = rendered_presentation.renderer.lookup_include).strip()
				if name in params:
					params[name] = value
				elif name == "uri":
					uri = value
				elif name == "src":
					raise NotImplementedError("Conversion from text to link using compression not implemented.")
				elif name == "srclink":
					srclink = value
				else:
					raise UnknownParameterException(f"Circuit parameter not understood: {name} (value: {value})")
			else:
				# May not move node immediately, because that will modify the
				# iteration
				inner.append(child_node)

		if srclink is not None:
			params["ctz"] = srclink

		for child_node in inner:
			replacement_node.appendChild(child_node)

		full_uri = uri + "?" + urllib.parse.urlencode(params)
		replacement_node.setAttribute("href", full_uri)

		return replacement_node
