#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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
#from Slide import Slide
from .Tools import XMLTools
#from Metadata import Metadata
#from TOC import TOC

class Presentation():
	def __init__(self):
		self._meta = None
		#self._toc = TOC()
		self._content = [ ]

	@property
	def meta(self):
		return self._meta

	@property
	def slides(self):
		return self._slides

	def _parse(self, filename):
		dom = xml.dom.minidom.parse(filename)
		if self._meta is None:
			self._meta = XMLTools.xml_to_dict(XMLTools.child_tagname(dom, ("presentation", "meta")))

		for child in XMLTools.child_tagname(dom, "presentation").childNodes:
			if child.nodeType != child.ELEMENT_NODE:
				continue
			if child.tagName == "slide":
				slide = Slide(child)
				slide.set_meta("section", self._toc.section)
				slide.set_meta("subsection", self._toc.subsection)
				slide.set_meta("slideno", len(self._slides) + 1)
				self._slides.append(slide)
			elif child.tagName == "include":
				dirname = os.path.dirname(self._filename)
				sub_presentation = dirname + "/" + child.getAttribute("src")
				self._parse(sub_presentation)
			elif child.tagName == "section":
				self._toc.section = XMLTools.inner_text(child)
			elif child.tagName == "subsection":
				self._toc.subsection = XMLTools.inner_text(child)

		for slide in self._slides:
			slide.set_meta("slidecnt", len(self._slides))
			slide.set_meta("toc", self._toc)

	@classmethod
	def load_from_file(cls, filename):
		return cls()._parse(filename)

	def __iter__(self):
		return iter(self._content)
