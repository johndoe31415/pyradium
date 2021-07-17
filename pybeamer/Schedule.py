#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
#
#	This file is part of pybeamer.
#
#	pybeamer is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pybeamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pybeamer; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import re
import enum
from .Exceptions import TimeSpecificationError

class TimeSpecificationType(enum.IntEnum):
	Relative = 0
	Absolute = 1

class TimeSpecification():
	_ABS_REGEX = re.compile(r"((?P<single_value>(\d*\.)?\d+)\s*(?P<unit>min|sec|m|s)|(?P<mins>\d+):(?P<secs>\d+))")
	_REL_REGEX = re.compile(r"(?P<rel_value>(\d*\.)?\d+)")

	def __init__(self, value, spec_type):
		assert(isinstance(spec_type, TimeSpecificationType))
		self._value = value
		self._spec_type = spec_type

	@property
	def value(self):
		return self._value

	@property
	def spec_type(self):
		return self._spec_type

	@classmethod
	def parse(cls, abs_string = None, rel_string = None):
		if (abs_string is None) and (rel_string is None):
			raise TimeSpecificationError("Either absolute or relative timing must be supplied.")
		if (abs_string is not None) and (rel_string is not None):
			raise TimeSpecificationError("Either absolute or relative timing must be supplied, not both.")

		if abs_string is not None:
			match = cls._ABS_REGEX.fullmatch(abs_string)
			if match is None:
				raise TimeSpecificationError("Invalid string for absolute timespecification: \"%s\"" % (abs_string))
			match = match.groupdict()
			if match["unit"] in [ "min", "m" ]:
				value = float(match["single_value"]) * 60
			elif match["unit"] in [ "sec", "s" ]:
				value = float(match["single_value"])
			elif match["unit"] is None:
				value = (60 * int(match["mins"])) + int(match["secs"])
			else:
				raise NotImplementedError(match["unit"])
			return cls(spec_type = TimeSpecificationType.Absolute, value = value)
		else:
			match = cls._REL_REGEX.fullmatch(rel_string)
			if match is None:
				raise TimeSpecificationError("Invalid string for relative timespecification: \"%s\"" % (rel_string))
			match = match.groupdict()
			return cls(spec_type = TimeSpecificationType.Relative, value = float(match["rel_value"]))

	def __str__(self):
		return "TimeSpecification<%s, %.0f>" % (self.spec_type.name, self.value)
