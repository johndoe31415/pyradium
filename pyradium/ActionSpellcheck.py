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

import os
import sys
from .BaseAction import BaseAction
from .Spellcheck import XMLSpellchecker, SpellcheckerAPI, LanguageToolProcess

class ActionSpellcheck(BaseAction):
	def _add_finding_print(self, spellcheck_result):
		offense = spellcheck_result.chunk.text[spellcheck_result.chunk_offset : spellcheck_result.chunk_offset + spellcheck_result.match["length"]]

		msg = [ ]
		msg.append("%s " % (spellcheck_result.group.description))
		msg.append("[line %d, col %d] " % (spellcheck_result.row, spellcheck_result.column))
		msg.append("\"%s\": " % (offense))
		msg.append("%s" % (spellcheck_result.match["message"]))
		if len(spellcheck_result.match["replacements"]) > 0:
			msg.append(" (suggest %s)" % (" or ".join(replacement["value"] for replacement in spellcheck_result.match["replacements"][:3])))
		print("".join(msg), file = self._f)

	def _add_finding_vim(self, spellcheck_result):
		offense = spellcheck_result.chunk.text[spellcheck_result.chunk_offset : spellcheck_result.chunk_offset + spellcheck_result.match["length"]]
		msg = "\"%s\": %s" % (offense, spellcheck_result.match["message"])
		print("%s:%d:%d:%s" % (self._args.infile, spellcheck_result.row, spellcheck_result.column, msg), file = self._f)

	def _run_spellcheck(self, spellchecker_api):
		finding_handler = getattr(self, "_add_finding_" + self._args.mode)
		emission_handler = getattr(self, "_emit_findings_" + self._args.mode, None)
		for spellcheck_result in self._xml_spellchecker.spellcheck(spellchecker_api):
			finding_handler(spellcheck_result)
		if emission_handler is not None:
			emission_handler()

	def run(self):
		if (self._args.outfile is not None) and (not self._args.force) and (os.path.exists(self._args.outfile)):
			print("Refusing to overwrite: %s" % (self._args.outfile))
			return 1
		if self._args.outfile is None:
			self._f = sys.stdout
		else:
			self._f = open(self._args.outfile, "w")

		try:
			self._xml_spellchecker = XMLSpellchecker()
			self._xml_spellchecker.parse(self._args.infile)

			if self._args.jar is not None:
				ltp = LanguageToolProcess(self._args.jar)
				with ltp as spellchecker_api:
					self._run_spellcheck(spellchecker_api)
			else:
				spellchecker_api = SpellcheckAPI(lt_uri = self._args.uri)
				self._run_spellcheck(spellchecker_api)
		finally:
			self._f.close()