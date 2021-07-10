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

from .Tools import XMLTools
from .Exceptions import UndefinedContentException
from .BaseDirective import BaseDirective

class RenderSlideDirective(BaseDirective):
	def __init__(self, xmlnode):
		assert(xmlnode.tagName == "slide")
		self._dom = xmlnode
		if not self._dom.hasAttribute("type"):
			self._dom.setAttribute("type", "default")

	def clone(self):
		dom = self._dom.cloneNode(deep = True)
		clone = Slide(xmlnode = dom)
		clone._meta = dict(self._meta)
		return clone

	@property
	def slide_type(self):
		return self._dom.getAttribute("type")

	@property
	def dom(self):
		return self._dom

	def __getattr__(self, key):
		if self._dom.hasAttribute(key):
			return self._dom.getAttribute(key)
		else:
			return None

	def content(self, content_name = None):
		if content_name is None:
			# All inner
			return XMLTools.inner_toxml(self._dom)
		else:
			for child in self._dom.getElementsByTagNameNS("http://github.com/johndoe31415/pybeamer", "content"):
				if child.getAttribute("name") == content_name:
					return XMLTools.inner_toxml(child)
			else:
				raise UndefinedContentException("Template tried to access content named '%s', but no such content defined in slide." % (content_name))

	def dump(self):
		print("Slide<%s>" % (self.slide_type))

	def __repr__(self):
		return "Slide<%s>" % (self.slide_type)
