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

class VariableSubstitutionHelper():
	_ATTEMPT_PARSE_STRINGS = [
		"%Y-%m-%d",
		"%m/%d/%Y",
		"%d.%m.%Y",
	]

	@classmethod
	def date_parse(cls, datespec):
		for parse_string in cls._ATTEMPT_PARSE_STRINGS:
			try:
				return datetime.datetime.strptime(datespec, parse_string)
			except ValueError:
				pass
		raise InvalidDateException(f"Unable to parse datespec: {datespec}")

	@classmethod
	def date_add(cls, date, delta_days):
		return date + datetime.timedelta(delta_days)

	@classmethod
	def date_strftime(cls, dt, format_string):
		# We actually no not want isinstance() here, because we care
		# specifically about class identity, not subclasses
		if not dt.__class__ is datetime.datetime:
			raise InvalidDateException(f"Unable to strftime: {dt} is not of class datetime.datetime")
		return dt.strftime(format_string)
