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
import logging
import collections
import enum
import os
import contextlib

_log = logging.getLogger(__spec__.name)

class SpellcheckExceptionType(enum.IntEnum):
	GeneralWord = 0
	RuleWord = 1
	RuleContext = 2

class SpellcheckDictionary():
	def __init__(self, filename):
		self._filename = filename
		self._modified = False

		try:
			with open(self._filename) as f:
				self._entries = json.load(f, object_pairs_hook = collections.OrderedDict)
		except FileNotFoundError:
			self._entries = collections.OrderedDict()
			self.write()
			_log.info("Creating empty dictionary: %s", self._filename)
		except json.decoder.JSONDecodeError as e:
			self._entries = collections.OrderedDict()
			self.write()
			_log.warning("Creating empty dictionary because it was malformed JSON: %s (%s)", self._filename, str(e))

	@classmethod
	def open_global_dict(cls):
		directory = os.path.realpath(os.path.expanduser("~/.config/pyradium"))
		with contextlib.suppress(FileExistsError):
			os.makedirs(directory)
		return cls(filename = directory + "/dictionary.json")

	def write(self):
		with open(self._filename, "w") as f:
			json.dump(self._entries, f, indent = 4)
			print(file = f)
			self._modified = False

	def write_if_modified(self):
		if self._modified:
			self.write()

	def add_general_word_exception(self, offense):
		self._modified = True
		if "general_words" not in self._entries:
			self._entries["general_words"] = [ ]
		self._entries["general_words"].append(offense)

	def add_word_exception(self, offense, rule_id):
		self._modified = True
		if "rule_words" not in self._entries:
			self._entries["rule_words"] = { }
		if rule_id not in self._entries["rule_words"]:
			self._entries["rule_words"][rule_id] = [ ]
		self._entries["rule_words"][rule_id].append(offense)

	def add_context_exception(self, context, rule_id):
		self._modified = True
		if "rule_context" not in self._entries:
			self._entries["rule_context"] = { }
		if rule_id not in self._entries["rule_context"]:
			self._entries["rule_context"][rule_id] = [ ]
		self._entries["rule_context"][rule_id].append(context)

	def has_exception(self, offense, context, rule_id):
		# Word is generally accepted, independent of rule/context
		if offense in self._entries.get("general_words", [ ]):
			return True

		# Word is allowed for this rule/language
		if offense in self._entries.get("rule_words", { }).get(rule_id, [ ]):
			return True

		# Context is allowed for this rule/language
		if context in self._entries.get("rule_context", { }).get(rule_id, [ ]):
			return True

		return False

	def add_exception(self, offense, context, rule_id, exception_type):
		assert(isinstance(exception_type, SpellcheckExceptionType))
		if exception_type == SpellcheckExceptionType.GeneralWord:
			self.add_general_word_exception(offense)
		elif exception_type == SpellcheckExceptionType.RuleWord:
			self.add_word_exception(offense, rule_id)
		elif exception_type == SpellcheckExceptionType.RuleContext:
			self.add_context_exception(context, rule_id)
		else:
			raise NotImplementedError(exception_type)

if __name__ == "__main__":
	dictionary = SpellcheckDictionary.open_global_dict()
