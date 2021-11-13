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

import textwrap
from .Exceptions import InvalidStyleParameterDefinitionException, InvalidStyleParameterValueException

class ParsedStyleParameters():
	def __init__(self, parameters):
		self._parameters = parameters
		self._values = { }

	@property
	def values(self):
		return self._values

	def set_value(self, key, value):
		self._values[key] = value

	def parse(self, text):
		return self._parameters.parse(self, text)

class StyleParameters():
	def __init__(self, definition):
		assert(isinstance(definition, dict))
		self._defs = definition

	def new_parser(self):
		parser = ParsedStyleParameters(self)
		for (name, definition) in self._defs.items():
			if "default" in definition:
				parser.set_value(name, definition["default"])
		return parser

	def parse(self, parser, text):
		split_text = text.split("=", maxsplit = 1)
		if len(split_text) != 2:
			raise InvalidStyleParameterValueException("Expected a key=value tuple for the style parameter, but got: %s" % (text))
		(key, value) = split_text

		key = key.strip()
		value = value.strip()
		if key not in self._defs:
			raise InvalidStyleParameterValueException("Not a valid style parameter: %s (must be one of %s)" % (key, ", ".join(sorted(self._defs))))

		parameter_def = self._defs[key]
		if "type" in parameter_def:
			parameter_type = parameter_def["type"]
			if parameter_type == "str":
				pass
			elif parameter_type == "int":
				try:
					value = int(value)
				except ValueError as e:
					raise InvalidStyleParameterValueException("Not a valid integer value for parameter %s: %s (%s)" % (key, value, str(e))) from e
			elif parameter_type == "float":
				try:
					value = float(value)
				except ValueError as e:
					raise InvalidStyleParameterValueException("Not a valid floating point value for parameter %s: %s (%s)" % (key, value, str(e))) from e
			elif parameter_type == "choice":
				if "choices" not in parameter_def:
					raise InvalidStyleParameterDefinitionException("Choice defined for parameter %s, but 'choices' entry missing." % (key))
				choices = parameter_def["choices"]
				if not isinstance(choices, list):
					raise InvalidStyleParameterDefinitionException("Choice defined for parameter %s, but choices are not a list." % (key))
				if value not in choices:
					raise InvalidStyleParameterValueException("Not a valid value for parameter %s: %s (should be one of %s)" % (key, value, ", ".join(choices)))
			else:
				raise InvalidStyleParameterDefinitionException("Unknown type defined for parameter %s: %s" % (key, parameter_type))
		parser.set_value(key, value)

	def print(self):
		print("Known style parameters:")
		for (name, definition) in sorted(self._defs.items()):
			if definition["type"] == "choice":
				value = "{%s}" % (",".join(definition["choices"]))
			else:
				value = "[%s]" % (definition.get("type", "str"))
			command_name = "%s %s" % (name, value)

			for description_line in textwrap.wrap(definition.get("description", "no description available"), width = 56):
				print("    %-15s    %s" % (command_name, description_line))
				command_name = ""

if __name__ == "__main__":
	sp = StyleParameters({
		"font-style": {
			"description": "influences the font choice used as the main slide text",
			"type":	"choice",
			"choices": [ "normal", "light" ],
			"default": "normal",
		},
		"intval": {
			"type":	"int",
		},
		"scale": {
			"type":	"float",
		}
	})

	parser = sp.new_parser()
	parser.parse("font-style=normal")
	parser.parse("scale=1.234")
	parser.parse("intval=1234")
	print(parser.values)
