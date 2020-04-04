#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2020 Johannes Bauer
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

import os
import xml.etree.ElementTree
from Slide import Slide
from Tools import XMLTools
from Metadata import Metadata

class Presentation():
	def __init__(self, filename):
		self._filename = filename
		self._tree = xml.etree.ElementTree.parse(self._filename)
		self._xml = self._tree.getroot()
		self._meta = Metadata.from_xmlnode(self._xml.find("meta"))
		self._slides = self._parse_slides()

	@property
	def meta(self):
		return self._meta

	@property
	def filename(self):
		return self._filename

	@property
	def slides(self):
		return self._slides

	def _parse_slides(self):
		slides = [ ]
		for child in self._xml.getchildren():
			if child.tag == "slide":
				slides.append(Slide(child, self))
			elif child.tag == "include":
				dirname = os.path.dirname(self._filename)
				sub_presentation = Presentation(dirname + "/" + child.attrib["src"])
				slides += sub_presentation.slides
		return slides

	def dump(self):
		for (slideno, slide) in enumerate(self._slides, 1):
			print("Slide %d from %s:" % (slideno, slide.presentation.filename))
			slide.dump()
			print()

	def process_slides(self):
		"""Go through slides and interpret special commands (e.g., pause/clear/etc.)"""
		pass
