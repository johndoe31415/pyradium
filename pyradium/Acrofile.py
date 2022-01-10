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

import json
import tempfile
import shutil
import contextlib
from .Exceptions import InvalidAcronymFileException, DuplicateAcronymException

class Acrofile():
	_ALLOWED_KEYS = set([ "text", "acronym", "uri" ])

	def __init__(self):
		self._acronym_dict = { }

	def has(self, acronym):
		return acronym in self._acronym_dict

	def get(self, acronym):
		return self._acronym_dict.get(acronym)

	def add_entry(self, acronym, acro_data):
		assert(isinstance(acro_data, dict))
		illegal_keys = set(acro_data.keys()) - self._ALLOWED_KEYS
		if len(illegal_keys) > 0:
			raise InvalidAcronymFileException("Acronym %s contains illegal key(s): %s" % (acronym, ", ".join(sorted(illegal_keys))))
		if acronym in self._acronym_dict:
			raise DuplicateAcronymException("Acronym '%s' already present in acronym file." % (acronym))
		self._acronym_dict[acronym] = acro_data

	def write_to_file(self, filename):
		# Format nicely
		rows = [ ]
		for (acronym, acro_data) in self._acronym_dict.items():
			rows.append((acronym, acro_data["text"], acro_data.get("acronym")))

		# Determine maximum length of columns
		lengths = [  max((len(row[colid]) for row in rows if row[colid] is not None), default = 0) for colid in range(len(rows[0])) ]

		lines = [ ]
		for (acronym, acro_data) in sorted(self._acronym_dict.items()):
			line = [ ]
			line.append("%-*s" % (lengths[0] + 3, "\"%s\":" % (acronym)))
			line.append(" { ")
			line.append("%-*s" % (lengths[1] + 12, "\"text\": \"%s\", " % (acro_data["text"])))
			if "acronym" in acro_data:
				inner = "\"acronym\": \"%s\", " % (acro_data["acronym"])
			else:
				inner = ""
			line.append("%-*s" % (lengths[2] + 15, inner))

			if "uri" in acro_data:
				line.append("\"uri\": \"%s\", " % (acro_data["uri"]))


			line = "".join(line)
			line = line.rstrip(", ")
			line = line + " }"
			lines.append(line)
		jsondata = "{\n\t" + (",\n\t".join(lines)) + "\n}"

		with contextlib.suppress(FileNotFoundError):
			with tempfile.NamedTemporaryFile(mode = "w") as f:
				f.write(jsondata)
				f.write("\n")
				f.flush()
				shutil.move(f.name, filename)

	@classmethod
	def load_from_file(cls, filename):
		with open(filename) as f:
			acronyms = json.load(f)
		assert(isinstance(acronyms, dict))
		acrofile = cls()
		for (acronym, acro_data) in acronyms.items():
			acrofile.add_entry(acronym, acro_data)
		return acrofile

if __name__ == "__main__":
	af = Acrofile.load_from_file("/tmp/x.json")
#	af.add_entry("BB3C", { "text": "barfsdfdsf", "uri": "http://x.com" })
	af.add_entry("BB3C-1", { "acronym": "BB3C", "text": "barfsdfdsf", "uri": "http://x.com" })
	af.write_to_file("/tmp/x.json")
