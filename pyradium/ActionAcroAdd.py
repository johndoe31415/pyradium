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

from .Acrofile import Acrofile
from .BaseAction import BaseAction

class ActionAcroAdd(BaseAction):
	def run(self):
		acrofile = Acrofile.load_from_file(self._args.acrofile)
		while True:
			acronym = input("Acronym: ")
			if acrofile.has(acronym):
				acro_data = acrofile.get(acronym)
				print("Acronym '%s' already in database." % (acronym))
				for i in range(1, 100):
					suggestion = "%s-%d" % (acronym, i)
					if not acrofile.has(suggestion):
						print("Suggest to use: %s" % (suggestion))
						break
				if "text" in acro_data:
					print("Text   : %s" % (acro_data["text"]))
				if "acronym" in acro_data:
					print("Acronym: %s" % (acro_data["acronym"]))
				if "uri" in acro_data:
					print("URI    : %s" % (acro_data["uri"]))
			else:
				break

		text = input("Text   : ")
		actual_acronym = input("Acronym: ")
		uri = input("URI    : ")
		acro_data = { }
		if text != "":
			acro_data["text"] = text
		if actual_acronym != "":
			acro_data["acronym"] = actual_acronym
		if uri != "":
			acro_data["uri"] = uri

		acrofile.add_entry(acronym, acro_data)
		acrofile.write_to_file(self._args.acrofile)
