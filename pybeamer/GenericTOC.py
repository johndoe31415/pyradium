#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
#
#	This file is part of pybeamer.
#
#	pybeamer is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pybeamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pybeamer; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import enum
import string
import collections

class TOCCommand(enum.IntEnum):
	NestingIncrease = 0
	NestingDecrease = 1
	Item = 2

class TOCTranscription(enum.IntEnum):
	Integer = 0
	LowerAlpha = 1
	UpperAlpha = 2

class _TOCInstructionOpcode(enum.IntEnum):
	TOCItem = 0
	CounterSet = 1
	CounterAdd = 2
	TranscriptionUpdate = 3
	SeparatorUpdate = 4

_TOCItem = collections.namedtuple("TOCItem", [ "level", "text", "pages" ])
_TOCInstruction = collections.namedtuple("TOCInstruction", [ "opcode", "data" ])

class FrozenTOC():
	TOCEntry = collections.namedtuple("TOCEntry", [ "order", "local_number", "full_number", "text", "full_text" ])

	def __init__(self, toc):
		self._toc = toc
		self._levels = self._determine_levels(toc)
		self._instructions = self._normalize_instructions(toc)
		self._entries = [ ]

		self._text = collections.defaultdict(str)
		self._counter = collections.defaultdict(int)
		self._transcriptions = { }
		self._separators = { }
		self._unroll()

	@property
	def level_count(self):
		return len(self._levels)

	@property
	def toc(self):
		return self._toc

	def _seperator(self, level):
		return self._separators.get(level, ".")

	def _determine_levels(self, toc):
		levels = set()
		for instruction in toc.instructions:
			if instruction.opcode == _TOCInstructionOpcode.TOCItem:
				levels.add(instruction.data.level)
		return tuple(sorted(levels))

	@staticmethod
	def _transcribe_alpha(index, alphabet):
		letters = [ ]
		while index > 0:
			if len(letters) > 0:
				index -= 1
			(index, char) = divmod(index, len(alphabet))
			letters.append(alphabet[char])
		if len(letters) == 0:
			letters.append(alphabet[0])
		return "".join(reversed(letters))

	def _transcribe(self, level, value):
		transcriptor = self._transcriptions.get(level, TOCTranscription.Integer)
		if transcriptor == TOCTranscription.Integer:
			return str(value)
		elif transcriptor == TOCTranscription.LowerAlpha:
			return self._transcribe_alpha(value - 1, string.ascii_lowercase)
		elif transcriptor == TOCTranscription.UpperAlpha:
			return self._transcribe_alpha(value - 1, string.ascii_uppercase)
		else:
			raise NotImplementedError(transcriptor)

	def _normalize_instructions(self, toc):
		level_map = { level: index for (index, level) in enumerate(self._levels) }

		normalized_instructions = [ ]
		for item in toc.instructions:
			if item.opcode == _TOCInstructionOpcode.TOCItem:
				normalized_instructions.append(_TOCInstruction(opcode = item.opcode, data = _TOCItem(level = level_map[item.data.level], text = item.data.text, pages = item.data.pages)))
			else:
				normalized_instructions.append(_TOCInstruction(opcode = item.opcode, data = { level_map[level]: data for (level, data) in item.data.items() if (level in level_map) }))
		return normalized_instructions

	def _create_entry(self, at_level):
		order = tuple(depth for (level, depth) in sorted(self._counter.items()))

		local_number = self._transcribe(at_level, self._counter[at_level]) + self._seperator(at_level)

		full_number = [ ]
		for level in range(at_level + 1):
			full_number.append(self._transcribe(level, self._counter[level]))
			if level != at_level:
				full_number.append(self._seperator(level))
		full_number = "".join(full_number)

		full_text = [ ]
		for level in range(at_level + 1):
			full_text.append(self._text[level])
		return self.TOCEntry(order = order, local_number = local_number, full_number = full_number, text = self._text[at_level], full_text = full_text)

	def _unroll(self):
		previous_level = -1
		for instruction in self._instructions:
			if instruction.opcode == _TOCInstructionOpcode.TranscriptionUpdate:
				self._transcriptions.update(instruction.data)
			elif instruction.opcode == 	_TOCInstructionOpcode.CounterSet:
				self._counter.update(instruction.data)
			elif instruction.opcode == 	_TOCInstructionOpcode.CounterAdd:
				for (key, value) in instruction.data.items():
					self._counter[key] += value
			elif instruction.opcode == 	_TOCInstructionOpcode.TOCItem:
				at_level = instruction.data.level

				if at_level != previous_level:
					for level in range(at_level + 1, self.level_count):
						self._counter[level] = 0
						self._text[level] = ""

				if at_level > previous_level:
					for level in range(at_level - previous_level):
						self._entries.append((TOCCommand.NestingIncrease, None))
				elif at_level < previous_level:
					for i in range(previous_level - at_level):
						self._entries.append((TOCCommand.NestingDecrease, None))

				self._counter[at_level] += 1
				self._text[at_level] = instruction.data.text
				entry = self._create_entry(at_level)
				self._entries.append((TOCCommand.Item, entry))

				previous_level = at_level


			else:
				raise NotImplementedError(instruction.opcode)

		for i in range(previous_level + 1):
			self._entries.append((TOCCommand.NestingDecrease, None))

	def __iter__(self):
		return iter(self._entries)

class GenericTOC():
	def __init__(self):
		self._instructions = [ ]
		self._text = { }

	def current_text(self, level):
		return self._text.get(level)

	@property
	def instructions(self):
		return iter(self._instructions)

	def set_transcription(self, level, transcription):
		assert(isinstance(transcription, TOCTranscription))
		self._instructions.append(_TOCInstruction(opcode = _TOCInstructionOpcode.TranscriptionUpdate, data = { level: transcription }))

	def set_counter(self, level, value):
		self._instructions.append(_TOCInstruction(opcode = _TOCInstructionOpcode.CounterSet, data = { level: value }))

	def add_counter(self, level, value):
		self._instructions.append(_TOCInstruction(opcode = _TOCInstructionOpcode.CounterAdd, data = { level: value }))

	def new_heading(self, level, text):
		self._text[level] = text
		self._instructions.append(_TOCInstruction(opcode = _TOCInstructionOpcode.TOCItem, data = _TOCItem(level = level, text = text, pages = [ ])))

	def at_page(self, page_no):
		if len(self._items) > 0:
			last_item = self._items[-1]
			last_item.pages.append(page_no)

	def finalize(self):
		return FrozenTOC(self)

if __name__ == "__main__":
	toc = GenericTOC()
	toc.set_transcription(6, TOCTranscription.LowerAlpha)
	toc.new_heading(0, "Intro")
	toc.new_heading(1, "Background")
	toc.new_heading(1, "Related Work")
	toc.new_heading(1, "Things")
	toc.new_heading(0, "Main")
	toc.new_heading(1, "Apparatus")
	toc.new_heading(5, "Design")
	toc.new_heading(5, "Implementation")
	for x in range(30):
		toc.new_heading(6, "fooo %d" % (x))
	toc.new_heading(1, "Setup")
	toc.new_heading(5, "Initital")
	toc.new_heading(5, "Final")
	toc.new_heading(0, "Results")
	toc.set_counter(0, 0)
	toc.set_transcription(0, TOCTranscription.UpperAlpha)
	toc.new_heading(0, "Data Set")
	toc.new_heading(1, "Foobar")
	toc.new_heading(1, "Barfoo")
	toc.new_heading(1, "Mookoo")
	for cmd in toc.finalize():
		print(cmd)
