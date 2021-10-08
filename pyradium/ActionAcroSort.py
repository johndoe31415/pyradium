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

import json
import tempfile
import shutil
import contextlib
from .BaseAction import BaseAction

class ActionAcroSort(BaseAction):
	def run(self):
		with open(self._args.acrofile) as f:
			acronyms = json.load(f)

		rows = [ ]
		for (acro_id, acro_data) in acronyms.items():
			rows.append((acro_id, acro_data["text"], acro_data.get("acronym")))

		lengths = [  max(len(row[colid]) for row in rows if row[colid] is not None) for colid in range(len(rows[0])) ]

		allowed_keys = set([ "text", "acronym", "uri" ])
		lines = [ ]
		for (acro_id, acro_data) in sorted(acronyms.items()):
			illegal_keys = set(acro_data.keys()) - allowed_keys
			if len(illegal_keys) > 0:
				print("Refusing to process because of illegal key(s): %s" % (", ".join(sorted(illegal_keys))))
				return 1

			line = [ ]
			line.append("%-*s" % (lengths[0] + 3, "\"%s\":" % (acro_id)))
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
				f.flush()
				shutil.move(f.name, self._args.acrofile)

		return 0
