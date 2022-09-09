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

import os
import sys
import json
import base64
import zlib
import logging
import subprocess
from .BaseAction import BaseAction
from .Spellcheck import XMLSpellchecker, SpellcheckerAPI, LanguageToolProcess, LanguageToolConfig
from .SpellcheckDictionary import SpellcheckDictionary
from .CmdlineEscape import CmdlineEscape

_log = logging.getLogger(__spec__.name)

class ActionSpellcheck(BaseAction):
	_EVIM_SEPARATOR = "::"

	def _add_finding_print(self, spellcheck_result):
		msg = [ ]
		msg.append("%s " % (spellcheck_result.group.description))
		msg.append("[line %d, col %d] " % (spellcheck_result.row, spellcheck_result.column))
		if spellcheck_result.offense is not None:
			msg.append("\"%s\": " % (spellcheck_result.offense))
		else:
			msg.append(": ")
		msg.append("%s" % (spellcheck_result.match["message"]))
		if len(spellcheck_result.match["replacements"]) > 0:
			msg.append(" (suggest %s)" % (" or ".join(replacement["value"] for replacement in spellcheck_result.match["replacements"][:3])))
		print("".join(msg), file = self._f)

	def _get_vim_msg(self, spellcheck_result):
		if spellcheck_result.offense is not None:
			msg = [ "\"%s\": %s" % (spellcheck_result.offense, spellcheck_result.match["message"]) ]
		else:
			msg = [ spellcheck_result.match["message"] ]
		if len(spellcheck_result.match["replacements"]) > 0:
			msg.append(" (suggest %s)" % (" or ".join(replacement["value"] for replacement in spellcheck_result.match["replacements"][:3])))
		return "".join(msg)

	def _add_finding_vim(self, spellcheck_result):
		print("%s:%d:%d:%s" % (self._args.infile, spellcheck_result.row, spellcheck_result.column, self._get_vim_msg(spellcheck_result)), file = self._f)

	def _add_finding_evim(self, spellcheck_result):
		data = {
			"offense":	spellcheck_result.offense,
			"ctx":		spellcheck_result.match["context"]["text"],
			"rule":		spellcheck_result.match["rule"]["id"],
		}
		bin_data = zlib.compress(json.dumps(data, sort_keys = True, separators = (",", ":")).encode("ascii"))
		encoded_data = base64.b64encode(bin_data).decode("ascii")
		print(self._EVIM_SEPARATOR.join([ encoded_data, self._args.infile, str(spellcheck_result.row), str(spellcheck_result.column), self._get_vim_msg(spellcheck_result) ]), file = self._f)

	def _add_finding_fulljson(self, spellcheck_result):
		finding = {
			"chunk":			spellcheck_result.chunk.text,
			"chunk_offset":		spellcheck_result.chunk_offset,
			"group": {
				"description":	spellcheck_result.group.description,
				"chunks":		[ chunk.text for chunk in spellcheck_result.group.chunks ]
			},
			"group_offset":		spellcheck_result.group_offset,
			"match":			spellcheck_result.match,
		}
		self._findings.append(finding)

	def _emit_findings_fulljson(self):
		json.dump(self._findings, self._f)

	def _run_spellcheck(self, spellchecker_api):
		self._findings = [ ]
		finding_handler = getattr(self, "_add_finding_" + self._args.mode)
		emission_handler = getattr(self, "_emit_findings_" + self._args.mode, None)
		for spellcheck_result in self._xml_spellchecker.spellcheck(spellchecker_api):
			if not self._dictionary.has_exception(offense = spellcheck_result.offense, context = spellcheck_result.match["context"]["text"], rule_id = spellcheck_result.match["rule"]["id"]):
				finding_handler(spellcheck_result)
		if emission_handler is not None:
			emission_handler()

	def run(self):
		if self._args.vim:
			if not self._args.mode in [ "vim", "evim" ]:
				print("When trying to run in VIM mode, you need to specify either the 'vim' or 'evim' output facility.", file = sys.stderr)
				return 1
			if self._args.outfile is None:
				print("When trying to run in VIM mode, you need to specify an output file, not stdout.", file = sys.stderr)
				return 1

		if (self._args.outfile is not None) and (not self._args.force) and (os.path.exists(self._args.outfile)):
			print("Refusing to overwrite: %s" % (self._args.outfile), file = sys.stderr)
			return 1
		if self._args.outfile is None:
			self._f = sys.stdout
		else:
			self._f = open(self._args.outfile, "w")

		self._dictionary = SpellcheckDictionary.open_global_dict()
		languagetool_config = LanguageToolConfig(language = self._args.language, disabled_rules = [ "WHITESPACE_RULE", "COMMA_PARENTHESIS_WHITESPACE" ])
		try:
			self._xml_spellchecker = XMLSpellchecker()
			self._xml_spellchecker.parse(self._args.infile)

			if self._args.jar is not None:
				ltp = LanguageToolProcess(self._args.jar, languagetool_config = languagetool_config)
				with ltp as spellchecker_api:
					self._run_spellcheck(spellchecker_api)
			else:
				spellchecker_api = SpellcheckerAPI(languagetool_uri = self._args.uri)
				self._run_spellcheck(spellchecker_api)
		finally:
			self._f.close()

		if self._args.vim:
			vim_errorformat = {
				"vim":		r"%f:%l:%c:%m",
				"evim":		self._EVIM_SEPARATOR.join([ r"%[A-Za-z0-9/+=]%\\\\+", r"%f", r"%l", r"%c", r"%m" ]),
			}[self._args.mode]
			cmd = [ "vi", "-c", ":set errorformat=%s" % (vim_errorformat), "-c", ":cf %s" % (self._args.outfile) ]
			_log.info("Running: %s", CmdlineEscape().cmdline(cmd))
			subprocess.check_call(cmd)
		return 0
