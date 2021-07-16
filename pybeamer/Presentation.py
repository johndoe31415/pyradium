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

import xml.dom.minidom
from .Tools import XMLTools
from .TOC import TOCElement, TOCDirective
from .Slide import RenderSlideDirective
from .Acronyms import AcronymDirective

class Presentation():
	_NAMESPACES = {
		"https://github.com/johndoe31415/pybeamer":		"s",
	}

	def __init__(self, meta, content):
		self._meta = meta
		self._content = content
		self._sources = [ ]

	@property
	def meta(self):
		return self._meta

	@property
	def content(self):
		return self._content

	@classmethod
	def load_from_file(cls, filename, rendering_parameters = None):
		dom = xml.dom.minidom.parse(filename)
		cls._NAMESPACES.update(XMLTools.normalize_ns(dom.documentElement, cls._NAMESPACES))
		meta = None
		content = [ ]
		for child in XMLTools.child_tagname(dom, "presentation").childNodes:
			if child.nodeType != child.ELEMENT_NODE:
				continue

			if child.tagName == "meta":
				meta = XMLTools.xml_to_dict(XMLTools.child_tagname(dom, ("presentation", "meta")))
			elif child.tagName == "slide":
				content.append(RenderSlideDirective(child))
			elif child.tagName == "include":
				sub_presentation_filename = rendering_parameters.include_dirs.lookup(child.getAttribute("src"))
				sub_presentation = cls.load_from_file(sub_presentation_filename)
				content += sub_presentation.content
			elif child.tagName in [ "chapter", "section", "subsection" ]:
				toc_element = TOCElement(child.tagName)
				toc_directive = TOCDirective(toc_element, XMLTools.inner_text(child))
				content.append(toc_directive)
			elif child.tagName == "acronyms":
				content.append(AcronymDirective(child))
			else:
				print("Warning: Ignored unknown tag '%s'." % (child.tagName))
		return cls(meta, content)

	def __iter__(self):
		return iter(self._content)
