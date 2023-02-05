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
from .Exceptions import InvalidDateException

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
