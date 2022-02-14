#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2022 Johannes Bauer
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

import os
import json
from .Exceptions import ConfigurationException

class GlobalConfig():
	def __init__(self, filename):
		self._filename = filename
		try:
			with open(self._filename) as f:
				self._config = json.load(f)
		except FileNotFoundError:
			self._config = { }
		self._plausibilize()

	@classmethod
	def read(cls):
		filename = os.path.expanduser("~/.config/pyradium/configuration.json")
		return cls(filename)

	def _plausibilize(self):
		if self.has("spellcheck", "jar") and self.has("spellcheck", "uri"):
			raise ConfigurationException("%s: spellcheck.jar and spellcheck.uri are mutually exclusive" % (self._filename))

	def has(self, *args):
		value = self._config
		for key in args:
			if key not in value:
				return False
			value = value[key]
		return True

	def get(self, *args):
		value = self._config
		for key in args:
			value = value.get(key)
			if value is None:
				return value
		return value
