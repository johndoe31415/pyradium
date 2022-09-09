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

import json
import collections
from pyradium.Exceptions import MalformedJSONInputException

ResolvedAcronym = collections.namedtuple("ResolvedAcronym", [ "acronym_id", "acronym", "text", "uri" ])

class AcronymDirective():
	def __init__(self, node):
		self._src = node.getAttribute("src")

	@property
	def src(self):
		return self._src

	def render(self, rendered_presentation):
		filename = rendered_presentation.renderer.lookup_include(self._src)
		acronyms = rendered_presentation.renderer.get_custom_renderer("acronym")
		acronyms.load_database(filename)

class Acronyms():
	def __init__(self):
		self._acronyms = { }
		self._loaded_files = set()
		self._looked_up = set()
		self._unresolvable = set()

	def get_all_used_acronyms(self):
		used_acronyms = [ self.resolve(acronym_id) for acronym_id in self._looked_up ]
		used_acronyms.sort()
		return used_acronyms

	def load_database(self, filename):
		if filename in self._loaded_files:
			return
		with open(filename) as f:
			try:
				acronyms = json.load(f)
			except json.decoder.JSONDecodeError as e:
				raise MalformedJSONInputException(f"Acronym JSON file {filename} is malformed: {str(e)}") from e
		for (acronym_id, acronym_data) in acronyms.items():
			resolved_acronym = ResolvedAcronym(acronym_id = acronym_id, acronym = acronym_data.get("acronym", acronym_id), text = acronym_data["text"], uri = acronym_data.get("uri"))
			self._acronyms[acronym_id] = resolved_acronym

	def resolve(self, acronym_id):
		if acronym_id in self._acronyms:
			self._looked_up.add(acronym_id)
		else:
			if acronym_id not in self._unresolvable:
				print("Warning: Acronym '%s' not in acronym database." % (acronym_id))
				self._unresolvable.add(acronym_id)
		return self._acronyms.get(acronym_id)
