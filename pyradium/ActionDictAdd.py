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
import base64
import zlib
import re
from .BaseAction import BaseAction
from .SpellcheckDictionary import SpellcheckDictionary, SpellcheckExceptionType

class ActionDictAdd(BaseAction):
	_EVIM_REGEX = re.compile(r"^(?P<base64>[A-Za-z0-9/+=]+)::(?P<filename>[^:]+)::(?P<line>\d+)::(?P<col>\d+)::(?P<msg>.*)$")

	def _choice(self, prompt, valid_answers, default_answer = None):
		while True:
			answer = input(prompt)
			if (answer == "") and (default_answer is not None):
				answer = default_answer
			if answer in valid_answers:
				return answer

	def _handle_current_finding(self):
		if self._current_finding < 0:
			self._current_finding = 0
		(match, data) = self._findings[self._current_finding]
		if self._dictionary.has_exception(offense = data["offense"], context = data["ctx"], rule_id = data["rule"]):
			# Already handeled the same finding in this session, do not handle it again
			self._current_finding += 1
			return

		print()
		print(f"Finding {self._current_finding + 1} of {len(self._findings)}:")
		print(match["msg"])
		print(f"Offense: > {data['offense']} <")
		print("   [A]dd word to dictionary")
		print("   Add word to [g]lobal dictionary (for all languages, e.g., names)")
		print("   Add specific [c]ontext to dictionary")
		print("   Jump to [p]previous finding")
		print("   Do [n]othing with this match (default)")
		answer = self._choice("Your choice: ", [ "a", "g", "c", "p", "n" ], default_answer = "n")
		if answer in [ "a", "g", "c" ]:
			exception_type = {
				"a": SpellcheckExceptionType.RuleWord,
				"g": SpellcheckExceptionType.GeneralWord,
				"c": SpellcheckExceptionType.RuleContext,
			}[answer]
			self._dictionary.add_exception(offense = data["offense"], context = data["ctx"], rule_id = data["rule"], exception_type = exception_type)
			self._current_finding += 1
		elif answer == "n":
			self._current_finding += 1
		elif answer == "p":
			self._current_finding -= 1
		else:
			raise NotImplementedError(answer)

	def _handle_findings(self):
		while self._current_finding < len(self._findings):
			self._handle_current_finding()

	def run(self):
		self._dictionary = SpellcheckDictionary.open_global_dict()
		self._current_finding = 0
		self._findings = [ ]

		try:
			with open(self._args.infile) as f:
				for line in f:
					line = line.rstrip("\r\n")
					match = self._EVIM_REGEX.fullmatch(line)
					if match is not None:
						match = match.groupdict()
						data = json.loads(zlib.decompress(base64.b64decode(match["base64"])))
						if not self._dictionary.has_exception(offense = data["offense"], context = data["ctx"], rule_id = data["rule"]):
							self._findings.append((match, data))
			self._handle_findings()
		finally:
			self._dictionary.write_if_modified()
