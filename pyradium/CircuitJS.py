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

import lzstr
import urllib.parse
from pyradium.Tools import XMLTools
from pyradium.Exceptions import UnknownParameterException, MissingParameterException

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

	def __init__(self, circuit: list[str] | None = None, circuit_params: dict | None = None, uri: str = _DEFAULT_URI, presentation_params: dict | None = None, display_content: list | None = None):
		self._circuit = circuit
		self._circuit_params = circuit_params if (circuit_params is not None) else { }
		self._uri = uri
		self._presentation_params = presentation_params if (presentation_params is not None) else { }
		self._display_content = display_content if (display_content is not None) else [ ]

	@property
	def circuit_text(self):
		if self._circuit is None:
			return None
		else:
			return "\n".join(self._circuit) + "\n"

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
		circuit = None
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
					circuit = value
				elif name == "srclink":
					parsed_url = urllib.parse.urlparse(value)
					query = urllib.parse.parse_qs(parsed_url.query)
					if "ctz" not in query:
						raise MissingParameterException(f"The URI provided as a 'srclink' for the 's:circuit' tag is missing the ctz= portion in its query string: {value}")
					srclink = query["ctz"][0]
					circuit = lzstr.LZStringDecompressor.decompress_from_url_component(srclink, escape = False).decode("ascii")
				elif name in [ "name", "content" ]:
					presentation_params[name] = value
				else:
					circuit_params[name] = value
			else:
				display_content.append(child_node)

		if circuit is not None:
			circuit = circuit.strip("\r\n")
			circuit = [ line.strip(" \t\r\n") for line in circuit.split("\n") ]
		return cls(circuit = circuit, circuit_params = circuit_params, uri = uri, presentation_params = presentation_params, display_content = display_content)

	def __str__(self):
		args = [ ]
		if self._circuit is None:
			args.append("no data")
		else:
			args.append(f"{len(self._circuit)} lines")
		args.append(self.full_url(True))
		return f"CircuitJS<{', '.join(args)}>"
