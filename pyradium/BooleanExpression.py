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

import enum
import string
import contextlib
import collections
from pyradium.Exceptions import InvalidBooleanExpressionException

ParsedElement = collections.namedtuple("ParsedElement", [ "etype", "content" ])

class SpecialCharacter(enum.IntEnum):
	LogicalOr = 0
	LogicalAnd = 1

class BooleanExpressionParser():
	_SPECIAL_CHARS = {
		"|":	SpecialCharacter.LogicalOr,
		"+":	SpecialCharacter.LogicalOr,
		"&":	SpecialCharacter.LogicalAnd,
		"*":	SpecialCharacter.LogicalAnd,
	}
	_LITERAL_CHARS = set(string.ascii_uppercase + string.ascii_lowercase)
	_LONG_LITERAL_CHARS = set(string.ascii_uppercase + string.ascii_lowercase + string.digits + "_")
	_TEXT_CHARS = set(" =," + string.digits)

	def __init__(self, string):
		self._index = 0
		self._string = string
		self._result = None
		self._current = None

	@property
	def char(self):
		if self._index < len(self._string):
			return self._string[self._index]
		else:
			return None

	@property
	def remaining(self):
		return self._string[self._index : ]

	def _produce(self, etype, content):
		element = ParsedElement(etype = etype, content = content)
		if self._result is not None:
			self._current.append(element)
		else:
			self._result = element
			self._current = self._result.content

	def _advance(self):
		self._index += 1

	@contextlib.contextmanager
	def _nested(self, etype):
		if etype is not None:
			content = [ ]
			self._produce(etype, content)
			(prev, self._current) = (self._current, content)
			yield
			self._current = prev
		else:
			yield

	def _parse_inverted(self):
		if self.char == "!":
			self._advance()
			with self._nested("invert"):
				if not self._parse_short_literal() and not self._parse_escaped_long_literal() and not self._parse_parenthesis():
					raise InvalidBooleanExpressionException("Invalid token after '!' sign: {self.remaining}")
			return True
		else:
			return False

	def _parse_long_literal(self):
		result = ""
		while self.char in self._LONG_LITERAL_CHARS:
			result += self.char
			self._advance()
		if result == "":
			return False
		else:
			self._produce("literal", result)
			return True

	def _parse_enclosed(self, etype, start, end, inner_parse_function):
		if self.char == start:
			self._advance()
			with self._nested(etype):
				inner_parse_function()
				if self.char != end:
					raise InvalidBooleanExpressionException(f"Enclosed expression started with '{start}' but does not terminate with '{end}' but '{self.char}' instead.")
				self._advance()
				return True
		else:
			return False

	def _parse_escaped_long_literal(self):
		return self._parse_enclosed(etype = None, start = "[", end = "]", inner_parse_function = self._parse_long_literal)

	def _parse_parenthesis(self):
		return self._parse_enclosed(etype = "parenthesis", start = "(", end = ")", inner_parse_function = self._parse_expression)

	def _parse_simple_char(self, etype, permissible_set, lookup = None):
		if self.char in permissible_set:
			if lookup is None:
				self._produce(etype, self.char)
			else:
				self._produce(etype, lookup(self.char))
			self._advance()
			return True
		return False

	def _parse_short_literal(self):
		return self._parse_simple_char("literal", self._LITERAL_CHARS)

	def _parse_special_char(self):
		return self._parse_simple_char("special", self._SPECIAL_CHARS, lookup = lambda c: self._SPECIAL_CHARS[c])

	def _parse_text(self):
		return self._parse_simple_char("text", self._TEXT_CHARS)

	def _parse_expression(self):
		with self._nested("expr"):
			have_terms = False
			while (self._index < len(self._string)) and (self._parse_escaped_long_literal() or self._parse_short_literal() or self._parse_inverted() or self._parse_special_char() or self._parse_text() or self._parse_parenthesis()):
				have_terms = True
		if not have_terms:
			raise InvalidBooleanExpressionException("Expression has no terms")
		return have_terms

	def parse(self):
		self._parse_expression()
		try:
			if len(self._string) != self._index:
				raise InvalidBooleanExpressionException(f"Trailing unparsed data: {self.remaining}")
		except InvalidBooleanExpressionException as e:
			raise InvalidBooleanExpressionException(f"Error parsing Boolean formula {self._string}: {str(e)}")
		return self._result


class TexBooleanExpressionPrinter():
	def __init__(self, invert_by_overline = True):
		self._invert_by_overline = invert_by_overline

	def _print(self, node, sibling = None):
		if isinstance(node, list):
			prev = None
			for child in node:
				yield from self._print(child, sibling = prev)
				prev = child
			return
		match node.etype:
			case "literal":
				yield r"\textnormal{"
				if "_" not in node.content:
					yield node.content
				else:
					(prefix, suffix) = node.content.split("_", maxsplit = 1)
					yield prefix
					yield "}_{"
					yield suffix
				yield "}"

			case "text":
				yield node.content

			case "invert":
				if self._invert_by_overline:
					if (sibling is not None) and (sibling.etype == "invert"):
						yield r"\ "
					yield r"\overline{"
					if node.content[0].etype == "parenthesis":
						# Don't display parenthesis
						yield from self._print(node.content[0].content)
					else:
						yield from self._print(node.content)
					yield "}"
				else:
					yield r"\neg "
					yield from self._print(node.content)

			case "special":
				yield {
					SpecialCharacter.LogicalOr:		r"\vee",
					SpecialCharacter.LogicalAnd:	r"\wedge",
				}[node.content]

			case "parenthesis":
				yield "("
				yield from self._print(node.content)
				yield ")"

			case "expr":
				yield from self._print(node.content)

			case _:
				raise NotImplementedError(node.etype)

	def print(self, tree):
		return "".join(self._print(tree))
