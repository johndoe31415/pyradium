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

import enum
from .BaseDirective import BaseDirective

class TOCElement(enum.Enum):
	Chapter = "chapter"
	Section = "section"
	SubSection = "subsection"

class TOCDirective(BaseDirective):
	_TOC_LEVEL = {
		TOCElement.Chapter:		0,
		TOCElement.Section:		1,
		TOCElement.SubSection:	2,
	}

	def __init__(self, toc_element, value):
		assert(isinstance(toc_element, TOCElement))
		self._toc_element = toc_element
		self._value = value

	@property
	def toc_element(self):
		return self._toc_element

	@property
	def value(self):
		return self._value

	def render(self, rendered_presentation):
		level = self._TOC_LEVEL[self.toc_element]
		rendered_presentation.toc.new_heading(level, self.value)
		if rendered_presentation.frozen_toc is not None:
			rendered_presentation.frozen_toc.advance()
