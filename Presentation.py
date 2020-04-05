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
import xml.dom.minidom
from Slide import Slide
from Tools import XMLTools
from Metadata import Metadata

class Presentation():
	def __init__(self, filename):
		self._filename = filename
		self._dom = xml.dom.minidom.parse(self._filename)
		self._meta = Metadata.from_xmlnode(XMLTools.child_tagname(self._dom, ("presentation", "meta")))
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
		for child in XMLTools.child_tagname(self._dom, "presentation").childNodes:
			if child.nodeType != child.ELEMENT_NODE:
				continue
			if child.tagName == "slide":
				slides.append(Slide(child))
			elif child.tagName == "include":
				dirname = os.path.dirname(self._filename)
				sub_presentation = Presentation(dirname + "/" + child.getAttribute("src"))
				slides += sub_presentation.slides
		return slides

	def dump(self):
		for (slideno, slide) in enumerate(self._slides, 1):
			print("Slide %d:" % (slideno))
			slide.dump()
			print()

	def __iter__(self):
		return iter(self._slides)
