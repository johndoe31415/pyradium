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

import enum
import time
import json
import subprocess
import collections
import logging
import bisect
import urllib.parse
import xml.parsers.expat
import requests
from pyradium.Exceptions import SpellcheckerException

_log = logging.getLogger(__spec__.name)

class LanguageToolConfig():
	def __init__(self, language = "en-US", picky = False, enabled_rules = None, disabled_rules = None, enabled_categories = None, disabled_categories = None):
		self._language = language
		self._picky = picky
		self._enabled_rules = enabled_rules
		self._disabled_rules = disabled_rules
		self._enabled_categories = enabled_categories
		self._disabled_categories = disabled_categories

	@property
	def language(self):
		return self._language

	@property
	def picky(self):
		return self._picky

	@property
	def enabled_rules(self):
		return self._enabled_rules

	@property
	def disabled_rules(self):
		return self._disabled_rules

	@property
	def enabled_categories(self):
		return self._enabled_categories

	@property
	def disabled_categories(self):
		return self._disabled_categories

class SpellcheckerAPI():
	def __init__(self, languagetool_uri, languagetool_config = None):
		self._languagetool_uri = languagetool_uri
		self._languagetool_config = languagetool_config
		if self._languagetool_config is None:
			self._languagetool_config = LanguageToolConfig()
		self._sess = requests.Session()

	def check_data(self, annotations):
		json_payload = {
			"annotation": annotations,
		}
		json_data = json.dumps(json_payload, separators = (",", ":"))
		query_args = {
			"language":	self._languagetool_config.language,
			"data":		json_data,
			"level":	"picky" if self._languagetool_config.picky else "default",
		}
		if self._languagetool_config.enabled_rules is not None:
			query_args["enabledRules"] = ",".join(self._languagetool_config.enabled_rules)
		if self._languagetool_config.disabled_rules is not None:
			query_args["disabledRules"] = ",".join(self._languagetool_config.disabled_rules)
		if self._languagetool_config.enabled_categories is not None:
			query_args["enabledCategories"] = ",".join(self._languagetool_config.enabled_categories)
		if self._languagetool_config.disabled_categories is not None:
			query_args["disabledCategories"] = ",".join(self._languagetool_config.disabled_categories)
		query_str = urllib.parse.urlencode(query_args)
		response = self._sess.post(self._languagetool_uri + "/check?" + query_str, headers = {
			"Accept": "application/json",
		})
		assert(response.status_code == 200)
		return response.json()

	def check_multitext(self, *texts):
		return self.check_data([ { "text": piece } for piece in texts ])

	def check(self, text):
		return self.check_data([{
			"text": text,
		}])

	def try_connect(self, timeout_sec = 3.0, time_between_attempts_sec = 0.25):
		t0 = time.time()
		tend = t0 + timeout_sec
		while time.time() < tend:
			try:
				response = self._sess.get(self._languagetool_uri + "/info")
				if response.status_code == 200:
					return True
			except requests.exceptions.ConnectionError:
				pass
			time.sleep(time_between_attempts_sec)
		return False

class TextChunk():
	def __init__(self, text_type, text, group = None, row = None, column = None):
		assert(text_type in [ "text", "markup" ])
		self._text_type = text_type
		self._text = text
		self._group = group
		self._row = row
		self._column = column

	@property
	def group(self):
		return self._group

	@property
	def row(self):
		return self._row

	@property
	def column(self):
		return self._column

	@property
	def text(self):
		return self._text

	def to_dict(self):
		return { self._text_type: self._text }

	@classmethod
	def joinall(cls, chunks):
		return "".join(chunk.text for chunk in chunks)

	def __str__(self):
		return "Chunk<%s, \"%s\", %s/%s>" % (self._text_type, self._text.replace("\n", r"\n"), self.row, self.column)

class TextChunks():
	def __init__(self):
		self._chunks = [ ]
		self._offsets = [ ]

	@property
	def first_chunk(self):
		return self._chunks[0]

	def append(self, chunk):
		assert(isinstance(chunk, TextChunk))
		if len(self._offsets) == 0:
			start_offset = 0
		else:
			start_offset = self._offsets[-1]
		self._chunks.append(chunk)
		self._offsets.append(start_offset + len(chunk.text))

	def joinall(self):
		return "".join(chunk.text for chunk in self)

	def to_data(self):
		return [ chunk.to_dict() for chunk in self ]

	def dump(self):
		for chunk in self._chunks:
			print(chunk)

	def find_chunk(self, chunk):
		index = self._chunks.index(chunk)
		return self[index]

	def find_offset(self, offset):
		index = bisect.bisect(self._offsets, offset)
		if index >= len(self._offsets):
			index = len(self._offsets) - 1
		return self[index]

	def __getitem__(self, index):
		start_offset = 0 if (index == 0) else self._offsets[index - 1]
		return (self._chunks[index], start_offset)

	def __iadd__(self, others):
		for chunk in others:
			self.append(chunk)
		return self

	def __iter__(self):
		return iter(self._chunks)

class LanguageToolProcess():
	def __init__(self, languagetool_server_jar_filename, port = 12764, languagetool_config = None):
		self._languagetool_server_jar_filename = languagetool_server_jar_filename
		self._port = port
		self._languagetool_config = languagetool_config
		self._proc = None

	def __enter__(self):
		assert(self._proc is None)
		try:
			self._proc = subprocess.Popen([ "java", "-cp", self._languagetool_server_jar_filename, "org.languagetool.server.HTTPServer", "--port", str(self._port), "--allow-origin", "*" ], stdout = _log.subproc_target, stderr = _log.subproc_target)
		except FileNotFoundError as e:
			raise SpellcheckerException("Unable to start LanguageTool on port %d: %s" % (self._port, str(e))) from e

		languagetool_uri = "http://127.0.0.1:%d/v2" % (self._port)
		sc = SpellcheckerAPI(languagetool_uri, self._languagetool_config)
		sc_available = sc.try_connect()
		if not sc_available:
			raise SpellcheckerException("Unable to establish connection to LanguageTool at %s" % (languagetool_uri))
		return sc

	def __exit__(self, *args):
		self._proc.kill()
		self._proc = None

class XMLSpellchecker():
	class ParserMode(enum.IntEnum):
		Normal = 0
		DropText = 1

		# "Markup" does include the text, but if it finds errors in the span,
		# ignores those. Useful for acronyms
		Markup = 2

	_SpellcheckGroup = collections.namedtuple("SpellcheckGroup", [ "description", "identifier", "row", "column", "chunks" ])
	_SpellcheckResult = collections.namedtuple("SpellcheckResult", [ "offense", "chunk", "chunk_offset", "group", "group_offset", "match", "row", "column" ])
	class _GroupIdentifier(enum.IntEnum):
		Slide = 1


	def __init__(self):
		self._parser = xml.parsers.expat.ParserCreate()
		self._parser.StartElementHandler = self._handle_start_element
		self._parser.EndElementHandler = self._handle_end_element
		self._parser.CharacterDataHandler = self._handle_character_data
		self._path = [ ]
		self._mode = [ self.ParserMode.Normal ]
		self._slides = { }
		self._slide_no = 0
		self._metadata = { }
		self._current_group_path = None
		self._current_group = None
		self._groups = [ ]

	@property
	def current_mode(self):
		return self._mode[-1]

	def _add_group(self, group_description, group_identifier):
		(_, column, row) = self._whereami()
		group = self._SpellcheckGroup(description = group_description, identifier = group_identifier, row = row, column = column, chunks = TextChunks())
		self._groups.append(group)
		return group

	def _whereami(self):
		byte_position = self._parser.CurrentByteIndex
		column = self._parser.CurrentColumnNumber + 1
		row = self._parser.CurrentLineNumber
		return (byte_position, column, row)

	def _record_group(self, group_description, text, group_identifier = None):
		(byte_position, column, row) = self._whereami()
		group = self._add_group(group_description, group_identifier)
		group.chunks.append(TextChunk("text", text, group = group, column = column, row = row))

	def _activate_group(self, group_description, group_identifier = None):
		assert(self._current_group is None)
		group = self._add_group(group_description, group_identifier)
		self._current_group = group
		self._current_group_path = list(self._path)

	def _handle_start_element(self, tag, attributes):
		self._path.append(tag)
		next_mode = self.current_mode
		if self._path == [ "presentation", "slide" ]:
			self._slide_no += 1
			self._activate_group("Slide %d content" % (self._slide_no), group_identifier = self._GroupIdentifier.Slide)
		elif (self._path == [ "presentation", "slide", "s:var" ]) and (attributes.get("name") == "heading"):
			self._record_group("Slide %d heading" % (self._slide_no), text = attributes.get("value", ""))
		elif self._path == [ "presentation", "meta", "title" ]:
			self._activate_group("Title metadata")
		elif self._path == [ "presentation", "meta", "subtitle" ]:
			self._activate_group("Subtitle metadata")

		if tag == "br":
			self._handle_character_data("\n")
		elif tag in [ "s:emo", "s:sym", "s:tex", "s:ar", "s:code", "s:term", "s:nsc" ]:
			next_mode = self.ParserMode.DropText
		elif tag == "s:ac":
			next_mode = self.ParserMode.Markup
		elif tag == "s:nth":
			self._handle_character_data("1st")
			next_mode = self.ParserMode.DropText

		self._mode.append(next_mode)

	def _handle_end_element(self, tag):
		if self._current_group_path == self._path:
			self._current_group_path = None
			self._current_group = None
		self._path.pop()
		self._mode.pop()

	def _handle_character_data(self, text):
		if self._current_group is not None:
			(byte_position, column, row) =  self._whereami()
			if self.current_mode == self.ParserMode.Normal:
				self._current_group.chunks.append(TextChunk("text", text, group = self._current_group, row = row, column = column))
			elif self.current_mode == self.ParserMode.Markup:
				self._current_group.chunks.append(TextChunk("markup", text, group = self._current_group, row = row, column = column))

			if self._current_group.identifier == self._GroupIdentifier.Slide:
				if self._slide_no not in self._slides:
					self._slides[self._slide_no] = { "group": self._current_group, "content": [ ] }
				self._slides[self._slide_no]["content"].append(text)

	def parse(self, xml_filename):
		with open(xml_filename, "rb") as f:
			self._parser.ParseFile(f)
		list(self._internal_spellcheck()) # TODO

	def dump(self):
		for group in self._groups:
			print("=> %s" % (group.description))
			for chunk in group.chunks:
				print(chunk)
			print("-" * 120)

	def _internal_spellcheck(self):
		stripped_content = { }
		for (slide_no, content) in self._slides.items():
			stripped = "".join(content["content"])
			stripped = stripped.replace("\n", "").replace("\t", "").replace(" ", "")
			if stripped != "":
				stripped_content[slide_no] = { "group": content["group"], "text": stripped }

		for (slide_no, content) in sorted(stripped_content.items()):
			next_slide_no = slide_no + 1
			if next_slide_no in stripped_content:
				text = content["text"]
				next_text = stripped_content[next_slide_no]["text"]
				if text == next_text:
					match = {
						"message": "Possible duplicate slide %d / %d" % (slide_no, next_slide_no),
						"replacements": [ ],
						"context": {
							"text": "N/A",
						},
						"rule": {
							"id": "pyradium-duplicate-slide-%d-%d" % (slide_no, next_slide_no)
						}
					}
					spellcheck_result = self._SpellcheckResult(offense = None, chunk = None, chunk_offset = None, group = content["group"], group_offset = None, match = match, row = content["group"].row, column = content["group"].column)
					yield spellcheck_result

	def spellcheck(self, spellcheck_api):
		yield from self._internal_spellcheck()

		separator = "\n\n"

		all_chunks = TextChunks()
		for group in self._groups:
			all_chunks += group.chunks
			all_chunks.append(TextChunk("markup", separator))
		result = spellcheck_api.check_data(all_chunks.to_data())

		for match in result["matches"]:
			(chunk, chunk_start_offset) = all_chunks.find_offset(match["offset"])
			chunk_offset = match["offset"] - chunk_start_offset

			group = chunk.group
			(first_chunk, first_chunk_start_offset) = all_chunks.find_chunk(group.chunks.first_chunk)
			group_offset = match["offset"] - first_chunk_start_offset

			row = chunk.row
			column = chunk.column
			for char in chunk.text[:chunk_offset]:
				if char == "\n":
					row += 1
					column = 1
				else:
					column += 1
			offense = chunk.text[chunk_offset : chunk_offset + match["length"]]
			spellcheck_result = self._SpellcheckResult(offense = offense, chunk = chunk, chunk_offset = chunk_offset, group = group, group_offset = group_offset, match = match, row = row, column = column)
			yield spellcheck_result

if __name__ == "__main__":
	ltp = LanguageToolProcess("lt/LanguageTool-5.5/languagetool-server.jar")
	xml_spellcheck = XMLSpellchecker()
	xml_spellcheck.parse("examples/example.xml")
	with ltp as api:
		for result in xml_spellcheck.spellcheck(api):
			offense = result.chunk.text[result.chunk_offset : result.chunk_offset + result.match["length"]]

			group_text = result.group.chunks.joinall()
			offense_group = group_text[result.group_offset : result.group_offset + result.match["length"]]
			assert(offense == offense_group)
			print("%s [line %d, col %d] \"%s\": %s" % (result.group.description, result.row, result.column, offense, result.match["message"]))
