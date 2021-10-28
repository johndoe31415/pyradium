#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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
_NormalizedTOCItem = collections.namedtuple("NormalizedTOCItem", [ "depth", "text", "pages" ])
_TOCInstruction = collections.namedtuple("TOCInstruction", [ "opcode", "data" ])

class FrozenTOC():
	TOCEntry = collections.namedtuple("TOCEntry", [ "order", "index", "depth", "local_number", "full_number", "text", "full_text", "pages" ])

	def __init__(self, toc):
		self._toc = toc
		self._levels = self._determine_levels(toc)
		self._instructions = self._normalize_instructions(toc)
		self._entries = [ ]
		self._index_by_full_number = { }
		self._current_index = -1

		self._text = collections.defaultdict(str)
		self._counter = collections.defaultdict(int)
		self._transcriptions = { }
		self._separators = { }
		self._unroll()

	@property
	def max_depth(self):
		return self.level_count

	@property
	def toc_item_count(self):
		return len(self._entries)

	@property
	def level_count(self):
		return len(self._levels)

	@property
	def toc(self):
		return self._toc

	@property
	def current_item(self):
		if self._current_index < 0:
			return None
		else:
			return self._entries[self._current_index]

	def advance(self):
		self._current_index += 1

	def reset_index(self):
		self._current_index = -1

	def _seperator(self, depth):
		return self._separators.get(depth, ".")

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

	def _transcribe(self, depth, value):
		transcriptor = self._transcriptions.get(depth, TOCTranscription.Integer)
		if transcriptor == TOCTranscription.Integer:
			return str(value)
		elif transcriptor == TOCTranscription.LowerAlpha:
			return self._transcribe_alpha(value - 1, string.ascii_lowercase)
		elif transcriptor == TOCTranscription.UpperAlpha:
			return self._transcribe_alpha(value - 1, string.ascii_uppercase)
		else:
			raise NotImplementedError(transcriptor)

	def _normalize_instructions(self, toc):
		depth_by_level = { level: depth for (depth, level) in enumerate(self._levels, 1) }

		normalized_instructions = [ ]
		for item in toc.instructions:
			if item.opcode == _TOCInstructionOpcode.TOCItem:
				normalized_instructions.append(_TOCInstruction(opcode = item.opcode, data = _NormalizedTOCItem(depth = depth_by_level[item.data.level], text = item.data.text, pages = item.data.pages)))
			else:
				normalized_instructions.append(_TOCInstruction(opcode = item.opcode, data = { depth_by_level[level]: data for (level, data) in item.data.items() if (level in depth_by_level) }))
		return normalized_instructions

	def _create_entry(self, depth, pages):
		order = tuple(depth for (level, depth) in sorted(self._counter.items()))

		local_number = self._transcribe(depth, self._counter[depth]) + self._seperator(depth)

		full_number = [ ]
		for i in range(1, depth + 1):
			full_number.append(self._transcribe(i, self._counter[i]))
			if i != depth:
				full_number.append(self._seperator(i))
		full_number = "".join(full_number)

		full_text = [ ]
		for i in range(1, depth + 1):
			full_text.append(self._text[i])

		entry_index = len(self._entries)
		if full_number not in self._index_by_full_number:
			self._index_by_full_number[full_number] = entry_index

		return self.TOCEntry(order = order, index = entry_index, depth = depth, local_number = local_number, full_number = full_number, text = self._text[depth], full_text = full_text, pages = pages)

	def _unroll(self):
		current_depth = -1
		for instruction in self._instructions:
			if instruction.opcode == _TOCInstructionOpcode.TranscriptionUpdate:
				self._transcriptions.update(instruction.data)
			elif instruction.opcode == 	_TOCInstructionOpcode.CounterSet:
				self._counter.update(instruction.data)
			elif instruction.opcode == 	_TOCInstructionOpcode.CounterAdd:
				for (key, value) in instruction.data.items():
					self._counter[key] += value
			elif instruction.opcode == 	_TOCInstructionOpcode.TOCItem:
				depth = instruction.data.depth

				if depth != current_depth:
					for i in range(depth + 1, self.max_depth + 1):
						self._counter[i] = 0
						self._text[i] = ""

				self._counter[depth] += 1
				self._text[depth] = instruction.data.text
				self._entries.append(self._create_entry(depth, instruction.data.pages))

				current_depth = depth
			else:
				raise NotImplementedError(instruction.opcode)


	def emit_commands(self, toc_items):
		current_depth = 0
		for entry in toc_items:
			if entry.depth > current_depth:
				for i in range(entry.depth - current_depth):
					yield (TOCCommand.NestingIncrease, None)
			elif entry.depth < current_depth:
				for i in range(current_depth - entry.depth):
					yield (TOCCommand.NestingDecrease, None)
			current_depth = entry.depth
			yield (TOCCommand.Item, entry)

		for i in range(current_depth):
			yield (TOCCommand.NestingDecrease, None)

	def subset(self, start_at = None, end_before = None, max_items = None):
		start_index = 0
		if start_at is not None:
			if isinstance(start_at, str):
				start_index = self._index_by_full_number[start_at]
			else:
				start_index = start_at
		seen = 0
		current_depth = 0

		for entry in self._entries[start_index : ]:
			if (end_before is not None) and (entry.full_number == end_before):
				break

			seen += 1
			if (max_items is not None) and (seen > max_items):
				break

			yield entry

	def count_toc_items(self, start_at = None, end_before = None):
		return len(list(self.subset(start_at = start_at, end_before = end_before)))

	def __iter__(self):
		return self.emit_commands(self._entries)

	def dump(self):
		for entry in self._entries:
			print(entry)

class GenericTOC():
	"""\
	'levels' are arbitrary IDs, not necessarily consecutive
		e.g. chapter is level 4
		section is level 9
		subsection is level 10

	They are mapped to 'depths', which are index 1. In the aforementioned example
		chapter is level 4 but depth 1
		section is level 9 but depth 2
		subsection is level 10 but depth 3
	"""
	def __init__(self):
		self._instructions = [ ]
		self._last_toc_item = { }

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

	def new_heading(self, level, text, at_page = None):
		toc_item = _TOCItem(level = level, text = text, pages = set())
		self._instructions.append(_TOCInstruction(opcode = _TOCInstructionOpcode.TOCItem, data = toc_item))
		self._last_toc_item[level] = toc_item

	def at_page(self, page_no):
		for (level, toc_item) in self._last_toc_item.items():
			toc_item.pages.add(page_no)

	def finalize(self):
		return FrozenTOC(self)

	def dump(self):
		for instruction in self._instructions:
			if instruction.opcode == _TOCInstructionOpcode.TOCItem:
				print(instruction.data)

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
	for x in range(3):
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

	frozen_toc = toc.finalize()
	for cmd in frozen_toc:
		print(cmd)

	print("-" * 120)
	for cmd in frozen_toc.subset(start_at = "2.1", end_before = "3", max_items = 4):
		print(cmd)
