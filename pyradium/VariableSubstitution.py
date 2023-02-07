#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2023 Johannes Bauer
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

import datetime
import dataclasses
from .Tools import EvalTools
from .Exceptions import InvalidFStringExpressionException, InfiniteRecusionVariableSubstitution, InvalidDateException

class DateTimeWrapper():
	_DEFAULT_PARSE_STRINGS = [
		"%Y-%m-%d",
		"%m/%d/%Y",
		"%d.%m.%Y",
	]

	def __init__(self, dt):
		self._dt = dt

	@classmethod
	def parse(cls, datespec: str, parse_string: str | None = None):
		if parse_string is None:
			parse_strings = cls._DEFAULT_PARSE_STRINGS
		else:
			parse_strings = [ parse_string ]

		for parse_string in parse_strings:
			try:
				return cls(datetime.datetime.strptime(datespec, parse_string))
			except ValueError:
				pass
		raise InvalidDateException(f"Unable to parse datespec: {datespec}")

	def add_days(self, delta_days):
		return DateTimeWrapper(self._dt + datetime.timedelta(delta_days))

	def strftime(self, fmt):
		return self._dt.strftime(fmt)


class VariableSubstitutionContainer():
	@dataclasses.dataclass
	class EvaluatedExpression():
		value: None = None

	def __init__(self, content, environment: dict | None = None, self_varname: str | None = "v"):
		self._content = content
		if environment is None:
			self._environment = { }
		else:
			self._environment = environment
		if self_varname is not None:
			self._environment[self_varname] = self
		self._evaluating_var = set()

	@classmethod
	def default_environment(cls):
		return {
			"int":		int,
			"datetm":	DateTimeWrapper,
		}

	@classmethod
	def merge_dicts(cls, obj1, obj2):
		assert(isinstance(obj1, dict))
		assert(isinstance(obj2, dict))
		result = obj1
		for (key, value) in obj2.items():
			if (key in result) and isinstance(result[key], dict) and isinstance(value, dict):
				result[key] = cls.merge_dicts(result[key], value)
			else:
				result[key] = value
		return result

	def evaluate_fstring(self, fstring):
		if "\"\"\"" in fstring:
			raise InvalidFStringExpressionException(f"Unable to evaluate as f-string: {fstring} may not contain triple quotes")
		expression = "f\"\"\"" + fstring + "\"\"\""
		try:
			return EvalTools.secure_eval(expression, self._environment)
		except Exception as e:
			raise InvalidFStringExpressionException(f"Unable to evaluate as f-string: {expression} -- {type(e).__name__}: {str(e)}") from e

	def evaluate_all(self):
		def _evaluate_if_possible(value):
			if isinstance(value, VariableSubstitutionContainer):
				value = value.evaluate_all()
			return value

		if isinstance(self._content, dict):
			result = { }
			for key in self._content:
				result[key] = _evaluate_if_possible(self[key])
		elif isinstance(self._content, list):
			result = [ ]
			for key in range(len(self._content)):
				result.append(_evaluate_if_possible(self[key]))
		else:
			raise NotImplementedError(type(self._content))
		return result

	def _evaluate(self, key, element):
		if isinstance(element, self.EvaluatedExpression):
			# expression already evaluated, return value
			return element.value
		elif isinstance(element, str):
			# not yet evaluated, evaluate as f-string
			if key in self._evaluating_var:
				raise InfiniteRecusionVariableSubstitution(f"Infinite recursion when accessing dictionary member {key}.")
			self._evaluating_var.add(key)
			evaluated_value = self.evaluate_fstring(fstring = element)
			self._evaluating_var.remove(key)
			self._content[key] = self.EvaluatedExpression(value = evaluated_value)
			return evaluated_value
		elif isinstance(element, (list, dict)):
			return VariableSubstitutionContainer(content = element, environment = self._environment, self_varname = None)
		else:
			return element

	def __getitem__(self, key):
		element = self._content[key]
		return self._evaluate(key, element)
