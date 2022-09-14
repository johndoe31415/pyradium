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
import lzstr
from pyradium.Tools import XMLTools
from pyradium.Exceptions import MissingParameterException

class CircuitJSCircuit():
	_DEFAULTS = {
		"euroResistors":	"true",
		"IECGates":			"false",
		"whiteBackground":	"true",
		"positiveColor":	"#27ae60",
		"negativeColor":	"#c0392b",
		"selectColor":		"#2c3e50",
	}
	_DEFAULT_URI = "https://www.falstad.com/circuit/circuitjs.html"
	_RESET_CONFIG = "$ 0 5e-6 10.2 50 5 50 5e-11"

	def __init__(self, circuit_text: str | None = None, circuit_params: dict | None = None, uri: str = _DEFAULT_URI, presentation_params: dict | None = None, display_content: list | None = None, original_xml_node = None):
		self._circuit = None
		self.circuit_text = circuit_text
		self._circuit_params = circuit_params if (circuit_params is not None) else { }
		self._uri = uri
		self._presentation_params = presentation_params if (presentation_params is not None) else { }
		self._display_content = display_content if (display_content is not None) else [ ]
		self._original_xml_node = original_xml_node

	def reset_presentation_parameters(self):
		if self._circuit is None:
			self._circuit = [ self._RESET_CONFIG ]
		else:
			self._circuit[0] = self._RESET_CONFIG

	@property
	def circuit_text(self):
		if self._circuit is None:
			return None
		else:
			return "\n".join(self._circuit) + "\n"

	@classmethod
	def automatic_filename_from_circuit_name(cls, circuit_name):
		return f"circuit_{circuit_name}.txt"

	@property
	def automatic_filename(self):
		return self.automatic_filename_from_circuit_name(self.get_presentation_parameter("name"))

	def _parse_text(self, text):
		text = text.strip("\r\n")
		text = [ line.strip(" \t\r\n") for line in text.split("\n") ]
		return text

	@circuit_text.setter
	def circuit_text(self, value):
		if value is None:
			self._circuit = None
		else:
			self._circuit = self._parse_text(value)

	@property
	def display_content(self):
		return self._display_content

	def circuit_params(self, include_circuit: bool = False):
		args = dict(self._circuit_params)
		if include_circuit and (self._circuit is not None):
			ctz = lzstr.LZStringCompressor.compress_to_url_component(self.circuit_text.encode("ascii"), escape = False)
			args["ctz"]	= ctz
		return args

	def full_url(self, include_circuit: bool = False):
		args = self.circuit_params(include_circuit = include_circuit)
		if len(args) == 0:
			return self._uri
		else:
			return f"{self._uri}?{urllib.parse.urlencode(args)}"

	def get_presentation_parameter(self, name):
		return self._presentation_params.get(name)

	def has_presentation_parameter(self, name):
		return name in self._presentation_params

	@classmethod
	def from_xml(cls, xml_node, no_defaults: bool = False, find_file_function = None):
		circuit_text = None
		if no_defaults:
			circuit_params = { }
		else:
			circuit_params = dict(cls._DEFAULTS)
		uri = cls._DEFAULT_URI
		presentation_params = { }
		display_content = [ ]

		for child_node in xml_node.childNodes:
			if (child_node.nodeType == child_node.ELEMENT_NODE) and (child_node.nodeName == "s:param"):
				# Parse parameter
				name = child_node.getAttribute("name")
				value = XMLTools.get_node_value(child_node, find_file_function = find_file_function).strip()
				if name == "uri":
					uri = value
				elif name == "src":
					circuit_text = value
				elif name == "srclink":
					parsed_url = urllib.parse.urlparse(value)
					query = urllib.parse.parse_qs(parsed_url.query)
					if "ctz" not in query:
						raise MissingParameterException(f"The URI provided as a 'srclink' for the 's:circuit' tag is missing the ctz= portion in its query string: {value}")
					srclink = query["ctz"][0]
					circuit_text = lzstr.LZStringDecompressor.decompress_from_url_component(srclink, escape = False).decode("ascii")
				elif name in [ "name", "content" ]:
					presentation_params[name] = value
				else:
					circuit_params[name] = value
			else:
				display_content.append(child_node)

			if circuit_text == "*":
				# Automatically load from filename
				if "name" not in presentation_params:
					raise MissingParameterException("Automatic determination of circuit source requested by using *, but circuit has no 'name' parameter set.")
				if find_file_function is None:
					raise MissingParameterException("Automatic determination of circuit source requested by using *, but no way of determining the included files given.")
				with open(find_file_function(cls.automatic_filename_from_circuit_name(presentation_params["name"]))) as f:
					circuit_text = f.read()
		return cls(circuit_text = circuit_text, circuit_params = circuit_params, uri = uri, presentation_params = presentation_params, display_content = display_content, original_xml_node = xml_node)

	def _find_circuit_nodes(self):
		found = [ ]
		for node in XMLTools.findall(self._original_xml_node, "s:param"):
			name = node.getAttribute("name")
			if name in [ "src", "srclink" ]:
				found.append(node)
		return found

	def _replace_source_node(self, replacement):
		present_nodes = self._find_circuit_nodes()
		first_node = present_nodes[0] if (len(present_nodes) > 0) else None

		if (len(present_nodes) == 1) and (replacement.getAttribute("src") == first_node.getAttribute("src")):
			current_text = XMLTools.inner_text(first_node)
			replacement_text = XMLTools.inner_text(replacement)
			if self._parse_text(current_text) == self._parse_text(replacement_text):
				# Nothing needs to change.
				return False

		if len(present_nodes) > 0:
			XMLTools.replace_node(first_node, replacement)
			for node in present_nodes[1:]:
				XMLTools.remove_node(node)
		else:
			self._original_xml_node.appendChild(replacement)
		return True

	def modify_dom_source_inline(self):
		replacement = self._original_xml_node.ownerDocument.createElement("s:param")
		replacement.setAttribute("name", "src")
		indented_text = "\n\t\t\t\t" + self.circuit_text.rstrip("\n").replace("\n", "\n\t\t\t\t") + "\n\t\t\t"
		replacement.appendChild(self._original_xml_node.ownerDocument.createTextNode(indented_text))
		return self._replace_source_node(replacement)

	def modify_dom_source_external_file(self, filename):
		replacement = self._original_xml_node.ownerDocument.createElement("s:param")
		replacement.setAttribute("name", "src")
		if filename != "*":
			replacement.setAttribute("src", filename)
		else:
			replacement.setAttribute("value", "*")
		return self._replace_source_node(replacement)

	def __str__(self):
		args = [ ]
		if self._circuit is None:
			args.append("no data")
		else:
			args.append(f"{len(self._circuit)} lines")
		args.append(self.full_url(True))
		return f"CircuitJS<{', '.join(args)}>"
